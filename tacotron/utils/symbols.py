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
with open("characters.txt") as f:
	while 1:
		line = f.readline()
		if not line:
			break
		_character_list.append(line.strip())
# Prepend "@" to ARPAbet symbols to ensure uniqueness (some are the same as uppercase letters):
# _arpabet = ['@' + s for s in cmudict.valid_symbols]
_arpabet = [s for s in cmudict.valid_symbols]
# Export all symbols:
# symbols = [_pad, _eos, space] + _character_list + _arpabet
symbols = [_pad, _eos, space] + _character_list


def is_arpabet(char):
	return True if char in _arpabet else False
