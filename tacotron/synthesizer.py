import datetime
import logging
import os
import subprocess

import numpy as np
import tensorflow as tf

from infolog import log
from tacotron.models import create_model
from tacotron.utils.text import text_to_sequence, sequence_to_text

fh = logging.FileHandler(encoding='utf-8', mode='a', filename="tts.log")
logging.basicConfig(level=logging.INFO, handlers=[fh], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Synthesizer:
	def load(self, checkpoint_path, hparams, gta=False, model_name='Tacotron'):
		log('Constructing model: %s' % model_name)
		inputs = tf.placeholder(tf.int32, [1, None], 'inputs')
		input_lengths = tf.placeholder(tf.int32, [1], 'input_lengths')
		targets = tf.placeholder(tf.float32, [1, None, hparams.num_mels], 'mel_targets')
		with tf.variable_scope('model') as scope:
			self.model = create_model(model_name, hparams)
			if gta:
				self.model.initialize(inputs, input_lengths, targets, gta=gta)
			else:
				self.model.initialize(inputs, input_lengths)
			self.mel_outputs = self.model.mel_outputs
			self.alignment = self.model.alignments[0]
		self.gta = gta
		self._hparams = hparams

		log('Loading checkpoint: %s' % checkpoint_path)
		gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
		self.session = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
		self.session.run(tf.global_variables_initializer())
		saver = tf.train.Saver()
		saver.restore(self.session, checkpoint_path)

	# mel_filename = synth.synthesize(text, i+1, eval_dir, log_dir, None)

	def synthesize(self, text, index, out_dir, log_dir, mel_filename):
		hparams = self._hparams
		cleaner_names = [x.strip() for x in hparams.cleaners.split(',')]
		seq = text_to_sequence(text, cleaner_names)
		print(text)
		print(seq)
		text_converted = sequence_to_text(seq)
		print(text_converted)
		feed_dict = {
			self.model.inputs: [np.asarray(seq, dtype=np.int32)],
			self.model.input_lengths: np.asarray([len(seq)], dtype=np.int32),
		}

		if self.gta:
			# feed_dict[self.model.mel_targets] = np.load(mel_filename).reshape(1, -1, 80)
			feed_dict[self.model.mel_targets] = np.load(mel_filename).reshape(1, -1, 40)
		if self.gta or not hparams.predict_linear:
			mels, alignment = self.session.run([self.mel_outputs, self.alignment], feed_dict=feed_dict)

		else:
			linear, mels, alignment = self.session.run([self.linear_outputs, self.mel_outputs, self.alignment],
													   feed_dict=feed_dict)
			linear = linear.reshape(-1, hparams.num_freq)

		mels = mels.reshape(-1, hparams.num_mels)  # Thanks to @imdatsolak for pointing this out

		# convert checkpoint to frozen model
		minimal_graph = tf.graph_util.convert_variables_to_constants(self.session, self.session.graph_def,
																	 ["model/inference/add"])
		tf.train.write_graph(minimal_graph, '.', 'inference_model.pb', as_text=False)

		npy_data = mels.reshape((-1,))

		f32name = os.path.join(out_dir, 'mels/feature-{}.f32'.format(index))  # by jiang
		npy_data.tofile(f32name)  # by jiang
		return

	def live_synthesize(self, text, filename):
		hparams = self._hparams
		cleaner_names = [x.strip() for x in hparams.cleaners.split(',')]
		seq = text_to_sequence(text, cleaner_names)
		text_converted = sequence_to_text(seq)
		feed_dict = {
			self.model.inputs: [np.asarray(seq, dtype=np.int32)],
			self.model.input_lengths: np.asarray([len(seq)], dtype=np.int32),
		}
		start_time = datetime.datetime.now()
		mels, alignment = self.session.run([self.mel_outputs, self.alignment], feed_dict=feed_dict)
		end_time = datetime.datetime.now()
		period = round((end_time - start_time).total_seconds(), 3)
		logging.info("%s - Tacotron2 time consuming - [%sms]", filename, period * 1000)

		mels = mels.reshape(-1, hparams.num_mels)  # Thanks to @imdatsolak for pointing this out

		# # convert checkpoint to frozen model
		# minimal_graph = tf.graph_util.convert_variables_to_constants(self.session, self.session.graph_def,
		# 															 ["model/inference/add"])
		# tf.train.write_graph(minimal_graph, '.', 'inference_model.pb', as_text=False)

		npy_data = mels.reshape((-1,))

		f32_name = os.path.join('{}.f32'.format(filename))
		s16_name = os.path.join('{}.s16'.format(filename))
		npy_data.tofile(f32_name)
		start_time = datetime.datetime.now()
		p = subprocess.Popen(
			"lpcnet/test_lpcnet {} {}".format(f32_name, s16_name), shell=True,
			preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		end_time = datetime.datetime.now()
		period = round((end_time - start_time).total_seconds(), 3)
		logging.info("%s - LPCNet time consuming - [%sms]", filename, period * 1000)
		stdout, stderr = p.communicate()
		return_code = p.returncode
		res = ''
		start_time = datetime.datetime.now()

		with open(s16_name, 'rb') as f:
			res = f.read()
		if os.path.exists(f32_name):
			os.remove(f32_name)
		if os.path.exists(s16_name):
			os.remove(s16_name)
		end_time = datetime.datetime.now()
		period = round((end_time - start_time).total_seconds(), 3)
		logging.info("%s - IO time consuming - [%sms]", filename, period * 1000)
		return res
