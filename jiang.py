#enconding=utf-8
import io
import sys
from g2pM import G2pM
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
model = G2pM()
sentence = '这是一个测试，不是正式的句子'
pinyin = model(sentence)
print(pinyin)
