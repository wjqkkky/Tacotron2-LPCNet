#encoding=utf-8
import front_end.chinesetone2pinyin as cp
import front_end.remove_special_symbols as rm
from front_end.ChineseRhythmPredictor import *
from front_end.ChineseRhythmPredictor.experiment import test_sentences,load_model
from front_end import split_phoneme
import re
import copy
import time
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import sys
import codecs
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# sys.stdout.write("Your content....\n")

####英文字母映射词典，GLOBAL_ENGLISH_DICT_LEXICON
with open('front_end/lexicon26.txt', 'r', encoding='utf-8') as fo:
    global GLOBAL_ENGLISH_DICT_LEXICON
    GLOBAL_ENGLISH_DICT_LEXICON = dict()
    lines = fo.readlines()
    for line in lines:
        character, phone, character_pinyin = line.split('\t')
        GLOBAL_ENGLISH_DICT_LEXICON[character] = phone
global LIST_DICT_KEY
LIST_DICT_KEY=list(GLOBAL_ENGLISH_DICT_LEXICON.keys())
def with_rhythm(chinese:str,model,split=True):
    '''
    用模型添加韵律，中文转拼音
    :param chinese: 未加韵律、未正则化的中文
    :param model:韵律模型
    :param split:是否将拼音切分为音素，True为切分，False为不切分
    :return:正则化后的、加韵律的中文，正则化后的、加韵律的拼音
    '''
    pinyin_input = test_sentences(model,[chinese])
    chinese_normal, pinyin = cp.chinese2pinyin(pinyin_input)
    if split:
        pinyin = split_phoneme.split_sheng(pinyin)
        pinyin = pinyin.replace(' r5 ', ' er5 ')
    else:
        pinyin = split_phoneme.u_to_v(pinyin)
        pinyin = pinyin.replace(' r 5 ', ' er5 ')
    pinyin = pinyin.replace(' #0', '').replace('#2', '#1').replace('\n','')
    punctuation = [',', '.', '!', '?']
    print(pinyin)
    pinyin = pinyin.replace('  ', ' ')
    if pinyin[-1] in punctuation:
        pinyin = pinyin[:-2] + ' #2 ' + pinyin[-1] + '\n'
    else:
        pinyin = pinyin + ' #2' + '\n'
    return chinese_normal,pinyin
def without_rhythm(chinese:str,split=True):
    '''
    不添加韵律，中文转拼音
    :param chinese: 未正则化的中文
    :param split: 是否将拼音切分为音素，True为切分，False为不切分
    :return:正则化后的中文，正则化后的拼音
    '''
    chinese_normal, pinyin = cp.chinese2pinyin(chinese)
    if split:
        pinyin = split_phoneme.split_sheng(pinyin)
        pinyin = pinyin.replace(' r 5 ', ' er5 ')
    else:
        #pinyin = split_phoneme.u_to_v(pinyin)
        pinyin = pinyin.replace(' r5 ', ' er5 ')
    return chinese_normal, pinyin
def map_english(pinyin:str):
    '''
    英文字母映射，将英文字母映射为英文音素
    :param pinyin:汉语拼音
    :return:汉语拼音
    '''
    pinyin_split = pinyin.split()
    for phoneme in pinyin_split:
        if phoneme.isupper():
            if phoneme in LIST_DICT_KEY:
                continue
            else:
                pinyin_split.remove(phoneme)


    # pinyin_split_copy = copy.copy(pinyin_split)
    for num in range(0,len(pinyin_split)):
        if pinyin_split[num].isupper():
            if num+1<len(pinyin_split) and pinyin_split[num+1].isupper():
                pinyin_split[num]= GLOBAL_ENGLISH_DICT_LEXICON[pinyin_split[num]]+' .'
            else:
                pinyin_split[num] = GLOBAL_ENGLISH_DICT_LEXICON[pinyin_split[num]]


    pinyin=' '.join(pinyin_split)
    pinyin = pinyin.replace('  ',' ')
    return pinyin
def ending_add_rhy(chinese:str):
    '''
    在汉语句末加韵律。
    :param chinese:汉语句子，字符串
    :return: 句末加韵律的汉语
    '''
    chinese=chinese.replace(',','#1,').replace('!','#2!').replace('?','#2?')\
        .replace('，','#1,').replace('。','#2.').replace('！','#2!').replace('？','#2?')
    # print(chinese)
    if len(chinese)>2 and chinese[-3] =='#':
        chinese = chinese[:-2]+'2'+chinese[-1]
    else:
        chinese = chinese+'#2.'
    return chinese
# def method_point(chinese):
#     chinese_split = chinese.split()
#     for i in range(0,len(chinese_split)//2):
#         if chinese_split[i]=='.':


# if __name__ == '__main__':
def ch2py(chinese):
    # chinese='aaa你好，请你一定要好好学习哦'
    # r4 = "\\【】+|\\《》+|\\##+|[/_$&^*()<>+ ""'～·@|~{}#]+|[——\\\=、：\\-\"“”‘’ ‘'￥……（）\\[\\] 《》【】]"
    chinese = chinese.replace('、',',').replace(';',',').replace('；',',').replace('：', ':').replace('℃', '摄氏度').replace('\n','')
    # chinese=re.sub(r4, '', chinese)
    chinese_rm_symbols = rm.remove_symbols(chinese)
    chinese=ending_add_rhy(chinese_rm_symbols)
    # print(chinese)
    chinese = chinese.upper()
#     model = load_model()
    try:
        chinese_normal,pinyin = without_rhythm(chinese,split=True)
        # print(chinese_normal)
        # chinese_normal, pinyin = with_rhythm(chinese, model,split=False)
        pinyin = map_english(pinyin)
        # print(pinyin)
        pinyin = pinyin.replace('#1 , #2 .','#2 .')

        return pinyin
    except Exception as e:
        print('Exception',e)
        pinyin = 'zh e4 g e4 w o3 b u2 r en4 sh i2 y a5 #2 !'
        return pinyin

def ch2nr(chinese):
    # chinese='aaa你好，请你一定要好好学习哦'
    # r4 = "\\【】+|\\《》+|\\##+|[/_$&^*()<>+ ""'～·@|~{}#]+|[——\\\=、：\\-\"“”‘’ ‘'￥……（）\\[\\] 《》【】]"
    chinese = chinese.replace('、', ',').replace(';', ',').replace('；', ',').replace('：', ':').replace('℃',
                                                                                                      '摄氏度').replace(
        '\n', '')
    # chinese = re.sub(r4, '', chinese)
    chinese_rm_symbols = rm.remove_symbols(chinese)
    chinese = ending_add_rhy(chinese_rm_symbols)
    # print(chinese)
    chinese = chinese.upper()
    #     model = load_model()
    try:
        chinese_normal, pinyin = without_rhythm(chinese, split=True)
        print(chinese_normal)

        return chinese_normal
    except Exception as e:
        print('Exception', e)
        pinyin = 'zh e4 g e4 w o3 b u2 r en4 sh i2 y a5 #2 !'
    return pinyin

    # file_input = 'hr.txt'
    # file_out = 'hr_yunlv.txt'
    # fo = open(file_out, "w", encoding="utf-8")
    # with open(file_input, "r", encoding="utf-8") as f:
    #     while 1:
    #         line_1 = f.readline()
    #         if not line_1:
    #             break
    #         chinese_Normal, pinyin = with_rhythm(line_1, model)
    #         fo.write(pinyin)
    # # chinese_Normal,pinyin = without_rhythm(chinese,split=False)
    # # print(chinese_Normal)
    # # print(pinyin)
    # f.close()
    # fo.close()
