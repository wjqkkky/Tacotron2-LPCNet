#encoding=utf-8
import chinesetone2pinyin as cp
import chaifen
import time
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stdout.write("Your content....\n")


def with_Rhythm(chinese,model,split=True):
    pinyin_input = test_sentences(model,[chinese])
    chinese_Normal, pinyin = cp.chinese2pinyin(pinyin_input)
    if split:
        pinyin = chaifen.split_sheng(pinyin)
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
        pinyin = chaifen.split_sheng(pinyin)
    return chinese_Normal, pinyin
# if __name__ == '__main__':
#     chinese='嗯haha，时间~是$下午2点36分TN。'
# # pinyin_input = '今天是个好日子，心想的事儿都能成。儿子已经好了'
# #     model = load_model()
#     # chinese_Normal, pinyin = with_Rhythm(chinese, model)
#     chinese_Normal,pinyin = without_Rhythm(chinese,split=False)
#     print(chinese_Normal)
#     print(pinyin)
