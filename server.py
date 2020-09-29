import argparse
import base64
import datetime
import io
import logging
import os
import re
import uuid
import tensorflow as tf
import numpy as np
import tornado.web
import tornado.ioloop
import tornado.escape
from scipy.io import wavfile
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from hparams import hparams
from tacotron.synthesizer import Synthesizer
from front_end.tts_front_end_main import ch2py

html_body = '''<html><title>TTS Demo</title><meta charset='utf-8'>
<style>
body {padding: 16px; font-family: sans-serif; font-size: 14px; color: #444}
input {font-size: 14px; padding: 8px 12px; outline: none; border: 1px solid #ddd}
input:focus {box-shadow: 0 1px 2px rgba(0,0,0,.15)}
p {padding: 12px}
button {background: #28d; padding: 9px 14px; margin-left: 8px; border: none; outline: none;
	color: #fff; font-size: 14px; border-radius: 4px; cursor: pointer;}
button:hover {box-shadow: 0 1px 2px rgba(0,0,0,.15); opacity: 0.9;}
button:active {background: #29f;}
button[disabled] {opacity: 0.4; cursor: default}
</style>
<body>
<form>
  <textarea id="text" type="text" style="width:400px; height:200px;" placeholder="请输入要合成的文字..."></textarea>
  <script>
  document.getElementById("text").value="由汽车之家举办的第二届八幺八全球超级车展8月27日落幕。这场持续一个月的网上车展开设了近百个独立品牌展馆，推出了百城车展、全球汽车夜、汽车新消费论坛、金融节等主题活动。从公开数据看，车展累计浏览独立用户数超过1.3亿，视频播放2.7亿次。活动不仅聚焦购车，还涵盖跨界营销、汽车文化、行业交流、技术展览等多元内涵，成为汽车行业营销的新“IP”。"
  </script> 
  <button id="button" name="synthesize">合成</button>
</form>
<p id="message"></p>
<audio id="audio" controls autoplay hidden></audio>
<script>
function q(selector) {return document.querySelector(selector)}
q('#text').focus()
q('#button').addEventListener('click', function(e) {
  text = q('#text').value.trim()
  if (text) {
	q('#message').textContent = '合成中...'
	q('#button').disabled = true
	q('#audio').hidden = true
	synthesize(text)
  }
  e.preventDefault()
  return false
})
function synthesize(text) {
  fetch('/tts/synthesize?text=' + encodeURIComponent(text), {cache: 'no-cache'})
	.then(function(res) {
	  if (!res.ok) throw Error(res.statusText)
	  return res.blob()
	}).then(function(blob) {
	  q('#message').textContent = ''
	  q('#button').disabled = false
	  q('#audio').src = URL.createObjectURL(blob)
	  q('#audio').hidden = false
	}).catch(function(err) {
	  q('#message').textContent = 'ERROR! '
	  q('#button').disabled = false
	})
}
</script></body></html>
'''

fh = logging.FileHandler(encoding='utf-8', mode='a', filename="tts.log")
logging.basicConfig(level=logging.INFO, handlers=[fh], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MainHandler(tornado.web.RequestHandler, object):
	def get(self):
		self.set_header("Content-Type", "text/html")
		self.write(html_body)


class SynHandler(tornado.web.RequestHandler, object):
	executor = ThreadPoolExecutor(15)

	@gen.coroutine
	def get(self):
		try:
			orig_text = self.get_argument('text')
			logger.info("Receiving get request - [%s]", orig_text)

			pcms = yield self.syn(orig_text)
			wav = io.BytesIO()
			wavfile.write(wav, hparams.sample_rate, pcms.astype(np.int16))
			self.set_header("Content-Type", "audio/wav")
			self.write(wav.getvalue())
		except Exception as e:
			logger.exception(e)

	@gen.coroutine
	def post(self):
		self.set_header("Content-Type", "text/json;charset=UTF-8")
		res = {}
		try:
			body = self.request.body
			b64decode_text = base64.b64decode(body).decode("utf-8")
		except Exception as e:
			logger.exception(e)
			res["audio"] = ""
			res["returnCode"] = 101
			res["message"] = "param error"
			self.write(tornado.escape.json_encode(res))
			return
		try:
			pcms = yield self.syn(b64decode_text)
			logger.info("Receiving post request - [%s]", b64decode_text)
			wav = io.BytesIO()
			wavfile.write(wav, hparams.sample_rate, pcms.astype(np.int16))
			res["audio"] = wav.getvalue()
			res["returnCode"] = 0
			res["message"] = "ok"
			self.write(tornado.escape.json_encode(res))
		except Exception as e:
			logger.exception(e)
			res["audio"] = ""
			res["returnCode"] = 102
			res["message"] = "system internal error"
			self.write(tornado.escape.json_encode(res))

	@run_on_executor
	def syn(self, text):
		pcms = np.array([])
		texts = split_text(text.strip())
		for txt in texts:
			name = str(uuid.uuid4())
			logger.info("chinese_split: [%s]", txt)
			pinyin = ch2py(txt)
			logger.info("pinyin_result: [%s]", pinyin)
			start_time = datetime.datetime.now()
			res = synth.live_synthesize(pinyin, name)
			end_time = datetime.datetime.now()
			period = round((end_time - start_time).total_seconds(), 3)
			logger.info("%s - total time consuming - [%sms]", name, period * 1000)
			pcm_arr = np.frombuffer(res, dtype=np.int16)[5000:-4000]
			pcms = np.append(pcms, pcm_arr)
		return pcms


def split_text(text):
	# TODO 切割后的text不包含！？
	pattern_str = "，|：|。|；|？|！|——"
	match = re.search(r"\W", text)
	if not match:
		return [text]
	res = []
	texts = re.split(pattern_str, text)
	if texts[-1] == "":
		texts = texts[:-1]
	cur_text = ""
	for text in texts:
		if len(cur_text) == 0:
			cur_text += text
		else:
			cur_text += "，" + text
		if len(cur_text) > 10:
			res.append(cur_text + "。")
			cur_text = ""
	if cur_text != "":
		res.append(cur_text + "。")
	return res


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--checkpoint', default='model/tacotron_model.ckpt-135000',
						help='Path to model checkpoint')
	parser.add_argument('--hparams', default='',
						help='Hyperparameter overrides as a comma-separated list of name=value pairs')
	parser.add_argument('--port', default=12807, help='Port of Http service')
	parser.add_argument('--host', default="0.0.0.0", help='Host of Http service')
	parser.add_argument('--name', help='Name of logging directory if the two models were trained together.')
	args = parser.parse_args()
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
	os.environ['CUDA_VISIBLE_DEVICES'] = '0'
	checkpoint = os.path.join(args.checkpoint)

	try:
		checkpoint_path = checkpoint
		logger.info('loaded model at {}'.format(checkpoint_path))
		modified_hp = hparams.parse(args.hparams)
		synth = Synthesizer()
		synth.load(checkpoint_path, modified_hp)
	except:
		raise RuntimeError('Failed to load checkpoint at {}'.format(checkpoint))
	logger.info("TTS service started...")
	application = tornado.web.Application([
		(r"/", MainHandler),
		(r"/synthesize", SynHandler),
	])
	application.listen(int(args.port), xheaders=True)
	tornado.ioloop.IOLoop.instance().start()
