# -*- coding: utf-8 -*-
"""
@Time: 2020/7/23
@author: JiangPeipei
"""
import jieba
from ChineseTone import *
import jieba.posseg as pseg
import chaifen
def is_have_con(text_pinyin: str, tone: str, text_chinese:str):
    """
    检查该句拼音是否有连续的某个声调
    :param text_pinyin: 拼音文本
    :param tone: 声调
    :param con_num: 连续声调的个数，比如2或3
    :return: 有的话返回True,连续声调开始处的index；没有的话返回False,0
    """
    n_cur_con = 0
    # index = 0
    pinyins = text_pinyin.split()
    bian_diao_list =[]
    for i in range(0,len(pinyins)):
        if pinyins[i][-1] == tone:
            n_cur_con += 1
        else:
            if n_cur_con>1:
                bian_diao_list.append([pinyins[i - n_cur_con:i], n_cur_con,[text_chinese[i - n_cur_con:i]]])
            # print(n_cur_con)
            n_cur_con = 0
        if pinyins[i][-1] == tone and i ==len(pinyins)-1:
            if n_cur_con>1:
                bian_diao_list.append([pinyins[i-n_cur_con+1:i+1],n_cur_con,[text_chinese[i-n_cur_con+1:i+1]]])
    return bian_diao_list
def san_san_bian_diao(chinese_pinyin:str,list_modified_tone:list):
    for modified_tone in list_modified_tone:
        # print(type(modified_tone[-1]))
        if modified_tone[1] == 2:
            temp_modified_tone = modified_tone[0][0].replace('3','2')+ ' '+modified_tone[0][1]
            temp_tone = modified_tone[0][0]+' '+modified_tone[0][1]
            chinese_pinyin=chinese_pinyin.replace(temp_tone,temp_modified_tone)
        elif modified_tone[1] == 3:
            # temp_modified_tone = modified_tone[0][0].replace('3','2')+ ' '+modified_tone[0][1].replace('3','2')+ ' '+modified_tone[0][2]
            # temp_tone = modified_tone[0][0]+' '+modified_tone[0][1]+' '+modified_tone[0][2]
            # chinese_pinyin=chinese_pinyin.replace(temp_tone,temp_modified_tone)
            split_word = list(jieba.cut(modified_tone[2][0],cut_all=True))
            if modified_tone[2][0][1:] in split_word:
                temp_modified_tone = modified_tone[0][0]+ ' '+modified_tone[0][1].replace('3','2')+ ' '+modified_tone[0][2]
                temp_tone = modified_tone[0][0]+' '+modified_tone[0][1]+' '+modified_tone[0][2]
                chinese_pinyin=chinese_pinyin.replace(temp_tone,temp_modified_tone)
            if modified_tone[2][0][:2] in split_word:
                temp_modified_tone = modified_tone[0][0].replace('3','2')+ ' '+modified_tone[0][1].replace('3','2')+ ' '+modified_tone[0][2]
                temp_tone = modified_tone[0][0]+' '+modified_tone[0][1]+' '+modified_tone[0][2]
                chinese_pinyin=chinese_pinyin.replace(temp_tone,temp_modified_tone)
        # else:
            # print(modified_tone)
    return chinese_pinyin
def san_san_all_sentence(chinese_pinyin:str,list_index_san_tone:list,chinese):
    split_pinyin = chinese_pinyin.split()

    for index_san_tone in range((len(list_index_san_tone)-1),-1,-1):
        if list_index_san_tone[index_san_tone] > 2:
            _, pos = list(pseg.cut(chinese[list_index_san_tone[index_san_tone] - 3:list_index_san_tone[index_san_tone]]))[
                -1]
            pos = str(pos)
            # if pos[0] == 'n'or pos[0]=='N':
            #     # if split_pinyin[list_index_san_tone[index_san_tone] - 1][-1] == '3':
            #     #     print(111)
            # else:
            if pos[0]=='m' or pos[0]=='v':
                if split_pinyin[list_index_san_tone[index_san_tone] -1][-1] == '3':
                    split_pinyin[list_index_san_tone[index_san_tone] - 1] = split_pinyin[list_index_san_tone[
                                                                                             index_san_tone] - 1][
                                                                            :-1] + '2'
        if index_san_tone==0 and list_index_san_tone[index_san_tone] <3:
            if split_pinyin[list_index_san_tone[index_san_tone] -1][-1] == '3':
                split_pinyin[list_index_san_tone[index_san_tone]-1] = split_pinyin[list_index_san_tone[index_san_tone]-1][
                                                                        :-1] + '2'
        if list_index_san_tone[index_san_tone]==len(split_pinyin)-1:
            continue
        if split_pinyin[list_index_san_tone[index_san_tone]+1][-1]=='3':
            split_pinyin[list_index_san_tone[index_san_tone]]=split_pinyin[list_index_san_tone[index_san_tone]][:-1]+'2'
    return ' '.join(split_pinyin)
def find_index(word:str,key_word:str):
    index_list =[]
    for i in range(0,len(word)):
        if word[i]==key_word:
            index_list.append(i)
    return index_list

def yi_bian_diao(chinese_pinyin:str,word:str,split_pinyin:str,text_chinese:str,order_yi:int):
    number_list = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    all_index_list_yi=find_index(text_chinese,'一')
    split_chinese_pinyin = chinese_pinyin.split()
    if len(word)>1:
        index_list_yi=find_index(word,'一')
        for index_yi in index_list_yi:
            if index_yi==len(word)-1:
                return chinese_pinyin
            if word[index_yi+1] in number_list or word[index_yi-1] in number_list:
                continue
            if len(word) == 3 and word[index_yi - 1] == word[index_yi + 1] and index_yi==2:
                split_temp = split_pinyin.replace('yi1', 'yi5')
                chinese_pinyin = chinese_pinyin.replace(split_pinyin, split_temp)
                # continue
                return chinese_pinyin
            temp_pinyin = split_pinyin.split()
            # split_before = ' '.join(temp_pinyin[index_yi:(index_yi + 2)])
            split_before = ' '.join(split_chinese_pinyin[all_index_list_yi[order_yi - 1]:(all_index_list_yi[order_yi - 1] + 2)])
            # print(split_chinese_pinyin)
            if split_chinese_pinyin[all_index_list_yi[order_yi-1]+1][-1] == '4':
                split_temp = split_before.replace('yi1', 'yi2')
            else:
                if word=='一点' and text_chinese[all_index_list_yi[order_yi-1]+2] in number_list:
                    continue
                else:
                    split_temp = split_before.replace('yi1', 'yi4')
            chinese_pinyin = chinese_pinyin.replace(split_before, split_temp)
    else:
        split_before = ' '.join(
            split_chinese_pinyin[all_index_list_yi[order_yi - 1]:(all_index_list_yi[order_yi - 1] + 2)])
        # split_chinese_pinyin = chinese_pinyin.split()
        # print(split_chinese_pinyin)
        if all_index_list_yi[order_yi - 1] !=len(split_chinese_pinyin)-1:
            if split_chinese_pinyin[all_index_list_yi[order_yi - 1] + 1][-1]=='4':
                # split_before =split_chinese_pinyin[all_index_list_yi[order_yi - 1]]+' '+ split_chinese_pinyin[all_index_list_yi[order_yi - 1] + 1]
                split_temp = split_before.replace('yi1', 'yi2')
            else:
                split_temp = split_before.replace('yi1', 'yi4')
            chinese_pinyin = chinese_pinyin.replace(split_before, split_temp)
    if len(text_chinese)>1:
        before_yi = text_chinese[all_index_list_yi[order_yi-1]-1]
        after_yi = text_chinese[all_index_list_yi[order_yi-1]+1]
        if before_yi in number_list or after_yi in number_list:
            chinese_pinyin = chinese_pinyin.split()
            chinese_pinyin[all_index_list_yi[order_yi-1]]='yi1'
            chinese_pinyin = ' '.join(chinese_pinyin)
        # print(111)
    return chinese_pinyin
def bu_bian_diao(chinese_pinyin:str,word:str,split_pinyin:str):
    if len(word) > 1:
        index_list_bu = find_index(word, '不')
        for index_bu in index_list_bu:
            if index_bu ==len(word)-1:
                return chinese_pinyin
            if len(word) == 3 and word[index_bu - 1] == word[index_bu + 1]:
                split_temp = split_pinyin.replace('bu4', 'bu5')
                chinese_pinyin = chinese_pinyin.replace(split_pinyin, split_temp)
                # continue
                return chinese_pinyin
            temp_pinyin = split_pinyin.split()
            split_before = ' '.join(temp_pinyin[index_bu:(index_bu + 2)])
            if temp_pinyin[index_bu + 1][-1] == '4':
                split_temp = split_before.replace('bu4', 'bu2')
                chinese_pinyin = chinese_pinyin.replace(split_before,split_temp)
    return chinese_pinyin
def er_hua_yin(chinese_pinyin:str,chinese:str):
    # print(chinese_pinyin)
    index_list_er = find_index(chinese, '儿')
    split_pinyin = chinese_pinyin.split()
    for index_er in index_list_er:
        if split_pinyin[index_er] =='r5':
            split_pinyin[index_er-1] = split_pinyin[index_er-1][:-1] + 'r' + split_pinyin[index_er-1][-1]
    chinese_pinyin = ' '.join(split_pinyin)
    chinese_pinyin = chinese_pinyin.replace(' r5', '')
    return chinese_pinyin
def chinese_bian_diao(chinese:str):
    # chinese = '起火现场消防员正在救火'
    split_chineses = list(jieba.cut(chinese))
    # print(split_chineses)
    chinese_pinyin = PinyinHelper.convertToPinyinFromSentence(chinese, pinyinFormat=PinyinFormat.WITH_TONE_NUMBER)
    chinese_pinyin = ' '.join(chinese_pinyin)
    # print(chinese)
    list_modified_tone = []
    san_dan_word=[]
    order_yi=0
    order_san = -1
    for split_chinese in split_chineses:
        order_san=order_san+len(split_chinese)
        split_pinyin = PinyinHelper.convertToPinyinFromSentence(split_chinese, pinyinFormat=PinyinFormat.WITH_TONE_NUMBER)
        if len(split_chinese)==1 and split_pinyin[0][-1]=='3':
            san_dan_word.append(order_san)
        split_pinyin = ' '.join(split_pinyin)
        if '一' in split_chinese or '一' == split_chinese:
            order_yi=order_yi+split_chinese.count('一')
            chinese_pinyin = yi_bian_diao(chinese_pinyin,split_chinese,split_pinyin,chinese,order_yi)
        if '不' in split_chinese:
            chinese_pinyin = bu_bian_diao(chinese_pinyin,split_chinese,split_pinyin)
        split_list_modified_tone = is_have_con(split_pinyin,'3',split_chinese)
        list_modified_tone.extend(split_list_modified_tone)

    result = san_san_bian_diao(chinese_pinyin,list_modified_tone)
    # all_san=is_have_con(result, '3')
    # final_pinyin = san_san_bian_diao(result,all_san)
    final_pinyin = san_san_all_sentence(result,san_dan_word,chinese)
    # print(san_dan_word)
    # print(final_pinyin)
    # print(result)
    result = chaifen.u_to_v(final_pinyin)
    return result
if __name__ == '__main__':
    # chinese = '所以我只敢打你'
    # chinese = '合计筹资一点一二九一五五亿元'
    # result = chinese_bian_diao(chinese)
    # # result=er_hua_yin(result,chinese)
    # print(result)
    # pinyin_biao = 'li4 shi3 bu4 rong2 fan1 an4 shi4 shi2 bu4 rong2 fou3 ren4'
    # if result ==pinyin_biao:
    #     print(1111)

    filename = '000001-010000.txt'
    # filename = 'test.txt'
    with open(filename,encoding='utf-8') as fo:
        lines = fo.readlines()
        m=0
        for i in range(0, (len(lines) // 2)):
            chinese = lines[2*i].split('\t')[1]
            number =lines[2*i].split('\t')[0]
            pinyin_biao =lines[2*i+1].split('\t')[1]
            chinese=chinese.replace('#1','').replace('#2','').replace('#3','').replace('#4','').replace('——','').replace('“','').replace('”','')
            # chinese = chinese.replace('。','').replace('，','').replace('？','').replace('！','').replace('：','').replace('、','')
            result = chinese_bian_diao(chinese)
            if 'r5' in result:
                result = er_hua_yin(result, chinese)
            # result = result[:-2]+'\n'
            result = result.replace('。','').replace('，','').replace('？','').replace('！','').replace('：','').replace('、','')
            result = result.replace('\n','').replace('  ',' ')
            pinyin_biao = pinyin_biao.replace('\n','').replace('  ',' ')
            if result[-1] == ' ':
                result = result[:-1]
            if result !=pinyin_biao:

                if '6' in pinyin_biao:
                    continue
                else:
                    if '一' in chinese or '不' in chinese:
                        m = m + 1
                        print(number,chinese)
                    # print(pinyin_biao)
                        print(result)
                        print(pinyin_biao)
        print(m)