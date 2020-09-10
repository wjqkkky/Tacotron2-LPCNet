# encoding=utf-8
import chinesetone2pinyin as cp
from ChineseRhythmPredictor import *
from ChineseRhythmPredictor.experiment import test_sentences, load_model
import chaifen
import re
import time
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
import sys
import codecs

# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# sys.stdout.write("Your content....\n")


with open('lexicon26.txt', 'r', encoding='utf-8') as fo:
	dict_lexicon = dict()
	lines = fo.readlines()
	for line in lines:
		character, phone, character_pinyin = line.split('\t')
		dict_lexicon[character] = phone


def with_Rhythm(chinese, model, split=True):
	pinyin_input = test_sentences(model, [chinese])
	chinese_Normal, pinyin = cp.chinese2pinyin(pinyin_input)
	if split:
		pinyin = chaifen.split_sheng(pinyin)
		pinyin = pinyin.replace(' r5 ', ' er5 ')

	else:
		pinyin = chaifen.u_to_v(pinyin)
		pinyin = pinyin.replace(' r 5 ', ' er5 ')
	pinyin = pinyin.replace(' #0', '').replace('#2', '#1').replace('\n', '')
	punctuation = [',', '.', '!', '?']
	print(pinyin)
	pinyin = pinyin.replace('  ', ' ')
	if pinyin[-1] in punctuation:
		pinyin = pinyin[:-2] + ' #2 ' + pinyin[-1] + '\n'
	else:
		pinyin = pinyin + ' #2' + '\n'
	return chinese_Normal, pinyin


def without_Rhythm(chinese, split=True):
	chinese_Normal, pinyin = cp.chinese2pinyin(chinese)
	if split:
		pinyin = chaifen.split_sheng(pinyin)
		pinyin = pinyin.replace(' r 5 ', ' er5 ')
	else:
		pinyin = chaifen.u_to_v(pinyin)
		pinyin = pinyin.replace(' r5 ', ' er5 ')
	return chinese_Normal, pinyin


def map_lexicon(pinyin: str):
	pinyin_split = pinyin.split()
	for num in range(0, len(pinyin_split)):
		if pinyin_split[num].isupper():
			if num + 1 < len(pinyin_split) and pinyin_split[num + 1].isupper():
				pinyin_split[num] = dict_lexicon[pinyin_split[num]] + ' .'
			else:
				pinyin_split[num] = dict_lexicon[pinyin_split[num]]
	pinyin = ' '.join(pinyin_split)
	return pinyin


def add_Rhy_self(chinese: str):
	chinese = chinese.replace(',', '#1,').replace('!', '#1!').replace('?', '#1?') \
		.replace('，', '#1,').replace('。', '#1.').replace('！', '#1!').replace('？', '#1?')

	if len(chinese) > 2 and chinese[-3] == '#':
		chinese = chinese[:-2] + '2' + chinese[-1]
	else:
		chinese = chinese + '#2 .'
	return chinese


def chinese2py(chinese):
	chinese = chinese.replace('、', ',').replace('：', ',').replace(';', ',').replace('；', ',').replace("——", "，")
	r4 = "\\【】+|\\《》+|\\##+|[/_$&^*()<>+""'@|~{}#]+|[——\\\=、：\\-\"“”‘’‘'￥……（）\\[\\] 《》【】]"
	chinese = re.sub(r4, '', chinese)
	chinese = add_Rhy_self(chinese)
	chinese = chinese.upper()
	chinese_Normal, pinyin = without_Rhythm(chinese, split=True)
	pinyin = map_lexicon(pinyin)
	return pinyin


if __name__ == '__main__':
	r4 = "\\【.*?】+|\\《.*?》+|\\#.*?#+|[/_$&%^*()<>+""'@|~{}#]+|[——\\\=、：\\-\"“”‘’‘'￥……（）\\[\\] 《》【】]"
	chinese = '第一天11:00天24:00结束;；'
	chinese = chinese.replace('、', ',').replace('：', ',').replace(';', ',').replace('；', ',')
	chinese = re.sub(r4, '', chinese)
	chinese = add_Rhy_self(chinese)
	print(chinese)
	chinese = chinese.upper()
	#     model = load_model()
	chinese_Normal, pinyin = without_Rhythm(chinese, split=True)
	# chinese_Normal, pinyin = with_Rhythm(chinese, model,split=False)
	pinyin = map_lexicon(pinyin)
	print(pinyin)

# file_input = 'hr.txt'
# file_out = 'hr_yunlv.txt'
# fo = open(file_out, "w", encoding="utf-8")
# with open(file_input, "r", encoding="utf-8") as f:
#     while 1:
#         line_1 = f.readline()
#         if not line_1:
#             break
#         chinese_Normal, pinyin = with_Rhythm(line_1, model)
#         fo.write(pinyin)
# # chinese_Normal,pinyin = without_Rhythm(chinese,split=False)
# # print(chinese_Normal)
# # print(pinyin)
# f.close()
# fo.close()
