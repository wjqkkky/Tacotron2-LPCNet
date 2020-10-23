'''
Defines the set of symbols used in text input to the model.

The default is a set of ASCII characters that works well for English or text that has been run
through Unidecode. For other data, you can modify _characters. See TRAINING_DATA.md for details.
'''
from . import cmudict

_pad = '_'
_eos = '~'
space = " "
# _characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\'\"(),-.:;? '
_character_list = []
with open("characters.txt", encoding="utf-8") as f:
	while 1:
		line = f.readline()
		if not line:
			break
		_character_list.append(line.strip())
# Prepend "@" to ARPAbet symbols to ensure uniqueness (some are the same as uppercase letters):
# _arpabet = ['@' + s for s in cmudict.valid_symbols]
_arpabet = [s for s in cmudict.valid_symbols]
# Export all symbols:
symbols = [_pad, _eos, space] + _character_list + _arpabet


def is_arpabet(char):
	return True if char in _arpabet else False


if __name__ == '__main__':
	s = set()
	with open("../../eng_g2p_trans_final.txt", "r", encoding="utf-8") as f:
		while 1:
			l = f.readline()
			if not l:
				break
			filename, text = l.split("|")
			for word in text.split():
				if word not in symbols:
				# 结论：标注音标全部存在于symbols中
					s.add(word)
	print(s)
	# s1 = set()
	# for phone in cmudict.valid_symbols:
	# 	s1.add(phone)
	# print(s1 - s)

