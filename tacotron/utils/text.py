import re

from tacotron.utils import cleaners
from tacotron.utils.symbols import symbols
from tacotron.utils.symbols import is_arpabet

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}

# Regular expression matching text enclosed in curly braces:
_curly_re = re.compile(r'(.*?)\{(.+?)\}(.*)')


def text_to_sequence(text, cleaner_names):
	'''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.

	  The text can optionally have ARPAbet sequences enclosed in curly braces embedded
	  in it. For example, "Turn left on {HH AW1 S S T AH0 N} Street."

	  Args:
		text: string to convert to a sequence
		cleaner_names: names of the cleaner functions to run the text through

	  Returns:
		List of integers corresponding to the symbols in the text
	'''
	sequence = []

	# Check for curly braces and treat their contents as ARPAbet:
	sequence += _symbols_to_sequence(_clean_text(text, cleaner_names))

	# Append EOS token
	sequence.append(_symbol_to_id['~'])
	return sequence


def sequence_to_text(sequence):
	'''Converts a sequence of IDs back to a string'''
	result = ''
	for symbol_id in sequence:
		if symbol_id in _id_to_symbol:
			s = _id_to_symbol[symbol_id]
			# Enclose ARPAbet back in curly braces:
			# if len(s) > 1 and s[0] == '@':
			# 	s = '{%s}' % s[1:]
			result += s
	# return result.replace('}{', ' ')
	return result


def _clean_text(text, cleaner_names):
	for name in cleaner_names:
		cleaner = getattr(cleaners, name)
		if not cleaner:
			raise Exception('Unknown cleaner: %s' % name)
		text = cleaner(text)
	return text


def _symbols_to_sequence(symbols):
	seq = []
	pre_is_arpabet = False
	symbols = symbols.strip().split(" ")
	for s in symbols:
		id_s = _symbol_to_id[s]
		if _should_keep_symbol(s):
			if pre_is_arpabet and not is_arpabet(s):
				seq.append(_symbol_to_id[" "])
				seq.append(id_s)
				if s[-1] in ["1", "2", "3", "4", "5"] or s == ",":
					seq.append(_symbol_to_id[" "])
				pre_is_arpabet = False
			elif not pre_is_arpabet and not is_arpabet(s):
				seq.append(id_s)
				if s[-1] in ["1", "2", "3", "4", "5"] or s == ",":
					seq.append(_symbol_to_id[" "])
			elif pre_is_arpabet and is_arpabet(s):
				if s != ".":
					seq.append(id_s)
				else:
					seq.append(_symbol_to_id[" "])
				pre_is_arpabet = True
			else:
				seq.append(id_s)
				pre_is_arpabet = True
	return seq


def _arpabet_to_sequence(text):
	return _symbols_to_sequence(['@' + s for s in text.split()])


def _should_keep_symbol(s):
	return s in _symbol_to_id and s is not '_' and s is not '~'


if __name__ == '__main__':
	f_out = open("out.txt", "w")
	with open("metadata.csv", "r") as f:
		while 1:
			line = f.readline()
			if not line:
				break
			filename, text = line.split("|")
			seqs = _symbols_to_sequence(text)
			text_converted = sequence_to_text(seqs)
			f_out.write(text_converted + "\n")
	f_out.close()
