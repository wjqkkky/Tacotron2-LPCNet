#encoding=utf-8
import chinesetone2pinyin as cp
import time
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stdout.write("Your content....\n")


def split_sheng(words):
    '''
    :param words: 一段未拆分的拼音，拼音和标点和字符之间要用一个空格空起来
    :return: 拆分好的拼音。拆分为声母，韵母。
    '''
    list_sheng = ['b' ,'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k',  'j', 'q', 'x', 'zh',
                  'ch', 'sh','h', 'r', 'z', 'c', 's', 'w', 'y']
    words = words.replace('  ',' ')
    words =words.split(' ')
    word_split =[]
    list_special = ['y', 'j', 'q', 'x']
    for word in words:
        if word[0] in list_sheng:
            if word[:2] in list_sheng:
                word_split.append(word[:2])
                word_split.append(word[2:])
                continue
            else:
                if word[1] == 'u' and (word[0] in list_special):
                    word_temp = 'v' + word[2:]
                    word_split.append(word[0])
                    word_split.append(word_temp)
                else:
                    word_split.append(word[0])
                    word_split.append(word[1:])
        else:
            word_split.append(word)
    str_ = ' '.join(word_split)
    return str_

def with_Rhythm(chinese,model,split=True):
    pinyin_input = test_sentences(model,[chinese])
    chinese_Normal, pinyin = cp.chinese2pinyin(pinyin_input)
    if split:
        pinyin = split_sheng(pinyin)
    pinyin = pinyin.replace('#0', '').replace('#2', '#1')
    punctuation = [',', '.', '!', '?']
    if pinyin[-1] in punctuation:
        pinyin = pinyin[:-2] + '#2 ' + pinyin[-1]
    else:
        pinyin = pinyin + ' #2'
    pinyin = pinyin.replace(' r 5 ', ' er5 ')
    pinyin = pinyin.replace('  ', ' ')
    return chinese_Normal,pinyin
def without_Rhythm(chinese,split=True):
    chinese_Normal, pinyin = cp.chinese2pinyin(chinese)
    if split:
        pinyin = split_sheng(pinyin)
    return chinese_Normal, pinyin
# if __name__ == '__main__':
#     chinese='嗯haha，时间~是$下午2点36分TN。'
# # pinyin_input = '今天是个好日子，心想的事儿都能成。儿子已经好了'
# #     model = load_model()
#     # chinese_Normal, pinyin = with_Rhythm(chinese, model)
#     chinese_Normal,pinyin = without_Rhythm(chinese,split=False)
#     print(chinese_Normal)
#     print(pinyin)
