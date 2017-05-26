#coding=utf-8
import pandas as pd
import numpy as np

def word_length(wordguess):
    cnt=0
    for x in wordguess:
        if x=='*':
            cnt += 1
    return cnt

#以字母拼接数字的形式组成list
def word_list(word):
    listword=list()
    for i,x in enumerate(word):
        listword.append(x+str(i))
    return listword

#排序后的所有字母和位置组合的频率 input: 2-dimension list
def letter_count(list_word):
    dict_letter={}
    for i in word_list2guess:
        for j in i:
            if dict_letter.has_key(j):
                dict_letter[j]=dict_letter[j]+1
            else:
                dict_letter[j]=1
    return sorted(dict_letter.items(),key=lambda item:item[1])

#读取频数最高的几个字母 input: list
def get_words(letter_list):
    i=1
    while i < len(letter_list):
        yield letter_list[-i][0][0]
        i+=1
#返回尝试前n次概率比较高的字母
def word_iter(sorted_letter,n):
    word=get_words(sorted_letter)
    temp=list()
    for x in word:
        temp.append(x)
        if len(set(temp))>n:
            break
    return temp

#《机器学习实战11.3》
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    #map函数表示遍历C1中的每一个元素执行forzenset，frozenset表示“冰冻”的集合，即不可改变
    return map(frozenset,C1)

#Ck表示数据集，D表示候选集合的列表，minSupport表示最小支持度
#该函数用于从C1生成L1，L1表示满足最低支持度的元素集合
def scanD(D,Ck,minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            #issubset：表示如果集合can中的每一元素都在tid中则返回true
            if can.issubset(tid):
                #统计各个集合scan出现的次数，存入ssCnt字典中，字典的key是集合，value是统计出现的次数
                if not ssCnt.has_key(can):
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        #计算每个项集的支持度，如果满足条件则把该项集加入到retList列表中
        support = ssCnt[key]/numItems
        if support >= minSupport:
            retList.insert(0, key)
        #构建支持的项集的字典
        supportData[key] = support
    return retList,supportData
#Create Ck,CaprioriGen ()的输人参数为频繁项集列表Lk与项集元素个数k，输出为Ck
def aprioriGen(Lk,k):
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1,lenLk):
            #前k-2项相同时合并两个集合
            L1 = list(Lk[i])[:k-2]
            L2 = list(Lk[j])[:k-2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList

def apriori(dataSet,minSupport=10):
    C1 = createC1(dataSet)
    D = map(set,dataSet)
    L1,supportData = scanD(D, C1, minSupport)
    L = [L1]
    #若两个项集的长度为k - 1,则必须前k-2项相同才可连接，即求并集，所以[:k-2]的实际作用为取列表的前k-1个元素
    k = 2
    while(len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2], k)
        Lk,supK = scanD(D,Ck, minSupport)
        supportData.update(supK)
        L.append(Lk)
        k +=1
    return L,supportData

if __name__ == '__main__':
    dict_word = pd.read_csv('/Users/zhulibo/Desktop/简历/english_dict.csv', encoding='gbk')

    #dict data preporcessing
    dict_word['word'] = dict_word['word'].apply(lambda x: str(x).lower())
    # 筛选掉特殊字符字段
    dict_word = dict_word[dict_word['word'].apply(lambda x: x.isalnum()) == True]
    dict_word['length'] = dict_word['word'].apply(lambda x: len(x))
    #生成单词字母和所在位置的组合数组
    dict_word['letter_list'] = dict_word['word'].apply(lambda x: word_list(x))

    # 游戏开始
    url = 'https://strikingly-hangman.herokuapp.com/game/on'
    payload = {"playerId": "bo139189@163.com", "action": "startGame"}
    headers = {'content-type': 'application/json'}
    request = requests.post(url, data=json.dumps(payload), headers=headers).text.encode('utf8')
    # 获取单词个数和尝试次数
    request = eval(request)
    sessionId = request['sessionId']
    numberOfWords = request['data']['numberOfGuessAllowedForEachWord']
    numberOfGuessAllowedForEachWord = request['data']['numberOfGuessAllowedForEachWord']  # 每个单词可以尝试的次数
    for i in range(numberOfWords):
        # 读取单词
        print 'word'+str(i)+'guess'
        payload_word = {"sessionId": sessionId, "action": "nextWord"}
        request_word = requests.post(url, data=json.dumps(payload_word), headers=headers).text.encode('utf8')

        word_len = word_length(eval(request_word)['data']['word'])
        # 确定要猜测单词的字母长度
        dict_word2guess = dict_word[dict_word['length'] == word_len]
        temp_dict_word2guess = pd.DataFrame()
        result_temp = list()  # 存放返回的字母+位置组合
        guessed_letter = list()  # 已猜到的字母列表
        wrongGuessCountOfCurrentWord = 0  #
        temp_result= list()
        while wrongGuessCountOfCurrentWord < numberOfGuessAllowedForEachWord:
            if len(temp_dict_word2guess) == 1:  # 如果只有一个单词，直接输出结果
                print 'you win word'+i+' guess, the word is ', temp_dict_word2guess['word']
                break
            if wrongGuessCountOfCurrentWord==0:  # 第一次猜
                # 提取出单词的单个字母加数字后缀组成2维数组作为数据集
                word_list2guess = dict_word2guess['letter_list'].values.tolist()
                # 猜测第一个字母直接计算的所有字母和位置组合的频数，按照出现频率高低依次作为输入
                letter_candidate = letter_count(word_list2guess)
            else:
                # 根据前几个字母的结果找到频繁项，最小支持度30个，提高运算速度,如果频繁项个数为0减小支持度重新计算
                support_data = pd.DataFrame()
                minSupport = 30
                cnt=0
                while True:
                    print 'word '+str(i)+' try time '+str(cnt)
                    L, suppData = apriori(temp_word_list2guess, minSupport=minSupport)
                    # 筛选出频繁项集为n的所有组合
                    support_data = pd.DataFrame(suppData.items())
                    support_data.rename(columns={1: 'support_ratio', 0: 'letter'}, inplace=True)
                    support_data['len'] = support_data['letter'].apply(lambda x: len(x))
                    # 返回包含之前已猜测的字母个数➕1的所有单词
                    support_data = support_data[support_data['len'] == len(guessed_letter) + 1].sort_values(
                        'support_ratio')
                    if len(support_data) > (numberOfGuessAllowedForEachWord-wrongGuessCountOfCurrentWord):
                        break
                    else:# 如果组合数小于剩余尝试次数，减小支持度，重新计算
                        minSupport = minSupport - 5
                    cnt += 1
                # 按照支持度高低排列字母
                support_data_list = support_data['letter'].values.tolist()
                letter_candidate = [list(set(x) - set(guessed_letter)) for x in support_data_list]
            # 输入字母候选集
            letter = word_iter(letter_candidate, numberOfGuessAllowedForEachWord-wrongGuessCountOfCurrentWord-1)
            input_list = list(set(letter))
            input_list.sort(key=letter.index)
            # 依次输入字母，直到返回值，读取该字母的位置
            # input_list=['z','f','h','k','l','m','v','x']
            for k, x in enumerate(input_list):
                # input x
                print 'guess time '+str(k)+': '+x
                payload_guess = {"sessionId": sessionId,"action": "guessWord","guess": x}
                request = requests.post(url, data=json.dumps(payload_guess), headers=headers).text.encode('utf8')
                if eval(request)['data']['wrongGuessCountOfCurrentWord'] > wrongGuessCountOfCurrentWord:  # 如果猜测错误次数加1，执行下次循环
                    wrongGuessCountOfCurrentWord += 1
                    print eval(request)['data']['word']
                    continue
                else:
                    getword = eval(request)['data']['word']  # get response
                    pos = get_letter_position(word)  # 字母在单词中的位置
                    temp_result = [x + str(j) for j in pos]
                    break
            # 生成已猜成功的字母列表
            guessed_letter.extend(temp_result)
            temp_dict_word2guess = dict_word2guess[
                dict_word2guess.apply(lambda x: set(guessed_letter) & set(x.letter_list) == set(guessed_letter),
                                      axis=1) == True]
            temp_word_list2guess=temp_dict_word2guess['letter_list'].values.tolist()
        if wrongGuessCountOfCurrentWord>=numberOfGuessAllowedForEachWord:
            print 'you lose word'+str(i)+'guess '
    payload_result={
        "sessionId": sessionId,
        "action": "getResult"}
    request = requests.post(url, data=json.dumps(payload_result), headers=headers).text.encode('utf8')
    print request

