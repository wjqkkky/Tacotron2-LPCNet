import argparse
import datetime
import io
import logging
import os

import numpy as np
import tornado.web
import tornado.ioloop
from scipy.io import wavfile
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from hparams import hparams
from tacotron.synthesizer import Synthesizer
from front_end_main import chinese2py

import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stdout.write("Your content....\n")

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
  document.getElementById("text").value="红旗H9曾于2020年8月底正式上市，售价区间为30.98至53.98万元。同时红旗作为唯一的中国豪华品牌，红旗H9作为一款全新的中大型轿车产品也是被给予厚望。此次网络爆出的H9自燃事件或许会对刚上市不久的新车带来不好的影响，事故的具体原因还需要等待相关调查的正式发布。"
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

# fh = logging.FileHandler(encoding='utf-8', mode='a', filename="logs/tts.log")
# logging.basicConfig(level=logging.INFO, handlers=[fh], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
			start_time = datetime.datetime.now()
			orig_text = self.get_argument('text')
			logger.info("Receiving request - [%s]", orig_text)

			pcms = yield self.syn(orig_text)
			wav = io.BytesIO()
			wavfile.write(wav, hparams.sample_rate, pcms.astype(np.int16))
			self.set_header("Content-Type", "audio/wav")
			self.write(wav.getvalue())
			end_time = datetime.datetime.now()
			period = round((end_time - start_time).total_seconds(), 3)
			logging.info("period - [%sms]", period * 1000)
		except Exception as e:
			logger.exception(e)

	@run_on_executor
	def syn(self, text):
		pcms = np.array([])
		texts = split_text(text.strip())
		for txt in texts:
			# logger.info("chinese_split: [%s]", txt)
			print(txt)
			pinyin = chinese2py(txt)
			logger.info("pinyin: [%s]", pinyin)
			res = synth.live_synthesize(pinyin, "1")
			pcm_arr = np.frombuffer(res, dtype=np.int16)[5000:-4000]
			pcms = np.append(pcms, pcm_arr)
		# split_texts = text.split(",")
		# for text in split_texts:
		# 	if text:
		# 		text = text + ","
		# 		text_list = [text]
		# 		model_out = synth.synthesize_from_text(text_list)
		# 		pcm = get_pcm(model_out)
		# 		pcms = np.append(pcms, pcm)
		return pcms


def split_text(text):
	if "，" not in text:
		return [text]
	res = []
	texts = text.split("，")
	cur_text = ""
	for text in texts:
		if len(cur_text) < 10:
			cur_text += text
		else:
			res.append(cur_text)
			cur_text = text
	if cur_text != "":
		res.append(cur_text)
	return res


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--checkpoint', default='model/tacotron_model.ckpt-350000',
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
