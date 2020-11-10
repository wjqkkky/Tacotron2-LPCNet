# -*- coding: utf-8 -*-
"""
@Time: 2020/7/23
@author: JiangPeipei
"""
# from nltk.corpus import words,cmudict
# from g2p_en import G2p
import pronouncing
from tts_front.change_tone import chinese_bian_diao_pinyin
from tts_front import split_phoneme
# from tts_front.tts_front_end_main import ch2py
# from tts_front.tts_front_end_main import GLOBAL_ENGLISH_DICT_LEXICON
import re
import enchant
d = enchant.Dict("en_US")
# g2p = G2p()

with open('./tts_front/lexicon26.txt', 'r', encoding='utf-8') as fo:
    global GLOBAL_ENGLISH_DICT_LEXICON
    GLOBAL_ENGLISH_DICT_LEXICON = dict()
    lines = fo.readlines()
    for line in lines:
        character, phone, character_pinyin = line.split('\t')
        GLOBAL_ENGLISH_DICT_LEXICON[character] = phone

def ch2py(chinese:str,u2v=True):
    pinyin = chinese_bian_diao_pinyin(chinese)
    if u2v:
        pinyin = split_phoneme.u_to_v(pinyin)

    return pinyin
def words_flag(string:str):
    if string.isupper():
        flag_now = 0
    elif string.islower():
        flag_now = 1
    else:
        flag_now = 2
    return flag_now
def en_connect(connect_before:list):
    count_en=0
    for cb in connect_before:
        if cb.isupper():
            count_en=count_en+1
    connect_after=''
    for i in range(0,len(connect_before)):
        if count_en>1:
            if connect_before[i].isupper():
                connect_after=connect_after+ connect_before[i]+' / '
                count_en=count_en-1
            else:
                connect_after = connect_after + connect_before[i]+' '
        else:
            if i<len(connect_before)-1:
                connect_after = connect_after + connect_before[i]+' '
            else:
                connect_after = connect_after + connect_before[i]
    return connect_after

def split_chinese_eng(string:str):
    '''
    将英文和非英文分开，例如string='hello hello你好。'中英文分开后为list=['hello',' ','hello','你好']

    :param string: 中英文分开前，字符串
    :return: 中英文分开后，list
    '''
    if string == '':
        return ''
    flag=-1
    list_final=[]
    str_word = ''
    flag_begin=0
    ###中英文分开
    for ph in string:
        flag_begin=flag_begin+1
        if ph.isupper() or ph.islower():
            flag_now=0
        else:
            flag_now=1
        if flag_now==flag:
            str_word=str_word+ph
        else:
            if flag_begin ==1:
                str_word = str_word + ph
                flag = flag_now
            else:
                list_final.append(str_word)
                flag=flag_now
                str_word=ph
    list_final.append(str_word)
    return list_final
def trans2phone(list_final:list,chinese_split=True,chinese_u2v=True):
    '''
    将单独的英文和中文转化为音素
    :param list_final:中英文分割后的列表
    :return:中英文分割后的列表转化为音素
    '''
    phone_final = []
    ###中文转化为拼音，英文转化为音素
    for word in list_final:

        if word[0].islower() or word[0].isupper():
            # if word in words.words():
            flag_check = d.check(word) or d.check(word.title())  ###True为单词，False为字母
            # flag_check = False  #仅仅处理为字母，全部按照字母读
            if flag_check:
                # en_phone = g2p(word)
                en_phone = pronouncing.phones_for_word(word)
                # phone_tem = ' '.join(en_phone)
                if len(en_phone) == 0:
                    word = word.upper()
                    phone_tem_zimu = []
                    for w in word:
                        en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                        en_phone = ''.join(en_phone)
                        phone_tem_zimu.append(en_phone)
                    phone_tem = ' / '.join(phone_tem_zimu)
                else:
                    phone_tem = en_phone[0]

            else:
                word = word.lower()
                # if word in words.words():###判断是否为英文单词
                flag_check = d.check(word)  ###True为单词，False为字母
                # flag_check=False##全部按照字母读
                if flag_check:
                    # en_phone = g2p(word)
                    en_phone = pronouncing.phones_for_word(word)
                    if len(en_phone) == 0:
                        word = word.upper()
                        phone_tem_zimu = []
                        for w in word:
                            en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                            en_phone = ''.join(en_phone)
                            phone_tem_zimu.append(en_phone)
                        phone_tem = ' / '.join(phone_tem_zimu)
                    else:
                        phone_tem = en_phone[0]
                    # phone_tem = ' '.join(en_phone)
                else:
                    #####字母处理
                    word = word.upper()
                    phone_tem_zimu = []
                    for w in word:
                        en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                        en_phone = ''.join(en_phone)
                        phone_tem_zimu.append(en_phone)
                    phone_tem = ' / '.join(phone_tem_zimu)
        else:
            if word == ' ':
                continue
            else:
                pattern = '#1|#2|#3|#4'
                no_rhy_chinese=re.sub(pattern=pattern,repl='',string=word)
                string_phone = ch2py(no_rhy_chinese, u2v=chinese_u2v)
                split_string_phone = string_phone.split()
                string_lists = re.split(pattern, word)
                phone_list = []
                index_now = 0
                for string_list in string_lists:
                    if '儿' in string_list:
                        string_phone_temp = ch2py(string_list,u2v=False)
                        string_phone = ' '.join(split_string_phone[index_now:index_now + len(string_phone_temp.split())])
                        index_now = index_now + len(string_phone_temp.split())
                    else:
                        string_phone = ' '.join(split_string_phone[index_now:index_now+len(string_list)])
                        index_now = index_now+len(string_list)

                    if chinese_split:
                        string_phone = split_phoneme.split_sheng(string_phone)

                    phone_list.append(string_phone)
                phone_tem = ' #1 '.join(phone_list)
        phone_final.append(phone_tem)
    return phone_final
def add_ch_en_segment_sgin(phone_final):
    flag_before = words_flag(phone_final[0])
    list_temp = []
    list_final_ph = []
    flag = 1
    for i in range(0, len(phone_final)):
        if flag:
            if words_flag(phone_final[i]) == 0:
                flag_before = 0
                flag = 0
                list_temp.append(phone_final[i])

            elif words_flag(phone_final[i]) == 1:
                flag_before = 1
                flag = 0
                list_temp.append(phone_final[i])

            else:
                list_temp.append(phone_final[i])

        else:
            flag_now = words_flag(phone_final[i])
            if flag_now == 2:
                flag_now = flag_before
            if flag_now == flag_before:
                list_temp.append(phone_final[i])
            else:
                if flag_before == 1:
                    str_temp = ''.join(list_temp)
                    list_temp = str_temp
                else:
                    list_temp = en_connect(list_temp)
                list_final_ph.append(list_temp)
                list_temp = []
                flag_before = words_flag(phone_final[i])
                list_temp.append(phone_final[i])
        if i == len(phone_final) - 1:
            if flag_before == 1:
                str_temp = ''.join(list_temp)
                list_temp = str_temp
            else:
                list_temp = en_connect(list_temp)
            list_final_ph.append(list_temp)

    phone_str = ' / '.join(list_final_ph)
    phone_str = phone_str.replace('，', ',').replace('。', '.')#.replace('  ', ' ')
    if '#' in phone_str:
        phone_list = phone_str.split('#')
        phone_str = '#'.join(phone_list[:-1])
        phone_str = phone_str + '#2' + phone_list[-1][1:]
    # else:
    #     phone_str=phone_list[0]
    return phone_str
def word2phone(string,chinese_split=True,chinese_u2v=True):
    if string=='':
        return ''
    split_chinese_eng_list=split_chinese_eng(string)
    phone_split_list = trans2phone(split_chinese_eng_list,chinese_split=chinese_split,chinese_u2v=chinese_u2v)
    phone_str = add_ch_en_segment_sgin(phone_split_list)
    # phone_str = phone_str.replace('  ',' ')
    return phone_str
def word2phone1(string):
    if string == '':
        return ''
    flag=-1
    list_final=[]
    str_word = ''
    flag_begin=0
    ###中英文分开
    for ph in string:
        flag_begin=flag_begin+1
        if ph.isupper() or ph.islower():
            flag_now=0
        else:
            flag_now=1
        if flag_now==flag:
            str_word=str_word+ph
        else:
            if flag_begin ==1:
                str_word = str_word + ph
                flag = flag_now
            else:
                list_final.append(str_word)
                flag=flag_now
                str_word=ph
    list_final.append(str_word)
    # print(list_final)
    phone_final = []
    ###中文转化为拼音，英文转化为音素
    for word in list_final:

        if word[0].islower() or word[0].isupper():
            # if word in words.words():
            flag_check = d.check(word) or d.check(word.title())###True为单词，False为字母
            # flag_check = False  #仅仅处理为字母，全部按照字母读
            if flag_check:
                # en_phone = g2p(word)
                en_phone = pronouncing.phones_for_word(word)
                # phone_tem = ' '.join(en_phone)
                if len(en_phone) == 0:
                    word = word.upper()
                    phone_tem_zimu = []
                    for w in word:
                        en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                        en_phone = ''.join(en_phone)
                        phone_tem_zimu.append(en_phone)
                    phone_tem = ' / '.join(phone_tem_zimu)
                else:
                    phone_tem = en_phone[0]

            else:
                word = word.lower()
                # if word in words.words():###判断是否为英文单词
                flag_check = d.check(word)###True为单词，False为字母
                # flag_check=False##全部按照字母读
                if flag_check:
                    # en_phone = g2p(word)
                    en_phone = pronouncing.phones_for_word(word)
                    if len(en_phone)==0:
                        word = word.upper()
                        phone_tem_zimu = []
                        for w in word:
                            en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                            en_phone = ''.join(en_phone)
                            phone_tem_zimu.append(en_phone)
                        phone_tem = ' / '.join(phone_tem_zimu)
                    else:
                        phone_tem = en_phone[0]
                    # phone_tem = ' '.join(en_phone)
                else:
                    #####字母处理
                    word = word.upper()
                    phone_tem_zimu = []
                    for w in word:
                        en_phone = GLOBAL_ENGLISH_DICT_LEXICON[w]
                        en_phone = ''.join(en_phone)
                        phone_tem_zimu.append(en_phone)
                    phone_tem = ' / '.join(phone_tem_zimu)
        else:
            if word==' ':
                continue
            else:
                pattern = '#1|#2|#3|#4'
                string_lists = re.split(pattern, word)
                phone_list = []
                for string_list in string_lists:
                    string_phone = ch2py(string_list,split=False)
                    phone_list.append(string_phone)
                phone_tem = ' #1 '.join(phone_list)
        phone_final.append(phone_tem)
    # print(phone_final)
    #####添加中英文分割符号
    flag_before = words_flag(phone_final[0])
    list_temp=[]
    list_final_ph = []
    flag=1
    for i in range(0,len(phone_final)):
        if flag:
            if words_flag(phone_final[i])==0:
                flag_before=0
                flag = 0
                list_temp.append(phone_final[i])

            elif words_flag(phone_final[i])==1:
                flag_before = 1
                flag = 0
                list_temp.append(phone_final[i])

            else:
                list_temp.append(phone_final[i])

        else:
            flag_now=words_flag(phone_final[i])
            if flag_now==2:
                flag_now=flag_before
            if flag_now==flag_before:
                list_temp.append(phone_final[i])
            else:
                if flag_before==1:
                    str_temp = ''.join(list_temp)
                    list_temp=str_temp
                else:
                    list_temp = en_connect(list_temp)
                list_final_ph.append(list_temp)
                list_temp=[]
                flag_before=words_flag(phone_final[i])
                list_temp.append(phone_final[i])
        if i ==len(phone_final)-1:
            if flag_before==1:
                str_temp = ''.join(list_temp)
                list_temp=str_temp
            else:
                list_temp = en_connect(list_temp)
            list_final_ph.append(list_temp)
    # print(list_final_ph)

    phone_str = ' / '.join(list_final_ph)
    phone_str = phone_str.replace('，',',').replace('。','.')#.replace('  ',' ')
    if '#' in phone_str:
        phone_list = phone_str.split('#')
        phone_str='#'.join(phone_list[:-1])
        # print(phone_list)
        phone_str = phone_str+'#2'+phone_list[-1][1:]
    # else:
    #     phone_str=phone_list[0]
    return phone_str

if __name__=='__main__':
    string = "晚会#1彩排#3，欢迎#2各位#1朋友#2参加#1party#4。"
    # string = string.replace('#2','').replace('#1','').replace('#3','').replace('#4','')
    print(word2phone(string))

    # print('bx' in words.words())
    # print(g2p('bx'))