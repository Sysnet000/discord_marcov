import discord
import os, re, json, random
from janome.tokenizer import Tokenizer




dict_file = "chatbot-data.json"
dic = {}
tokenizer = Tokenizer()

if os.path.exists(dict_file):
    dic = json.load(open(dict_file, "r"))

def register_dic(words):
    global dic
    if len(words) == 0: return
    tmp = ["@"]
    for i in words:
        word = i.surface
        if word == "" or word == "\r\n" or word == "\n": continue
        tmp.append(word)
        if len(tmp) < 3: continue
        if len(tmp) > 3: tmp = tmp[1:]
        set_word3(dic, tmp)
        if word == "。" or word == "?":
            tmp = ["@"]
            continue
        #辞書更新毎にファイル保存
        f = open(dict_file, "w", encoding="utf-8")
        json.dump(dic, f)

def set_word3(dic, s3):
    w1, w2, w3 = s3
    if not w1 in dic: dic[w1] = {}
    if not w2 in dic[w1]: dic[w1][w2] = {}
    if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0
    dic[w1][w2][w3] += 1


def make_sentence(head):
    if not head in dic: return ""
    ret = []
    if head != "@": ret.append(head)
    top = dic[head]
    w1 = word_choice(top)
    w2 = word_choice(top[w1])
    ret.append(w1)
    ret.append(w2)
    while True:
        if w1 in dic and w2 in dic[w1]:
            w3 = word_choice(dic[w1][w2])
        else:
            w3 = ""
        ret.append(w3)
        if w3 == "。" or w3 == "？" or w3 == "": break
        w1, w2 = w2, w3
    return "".join(ret)


def word_choice(sel):
    keys = sel.keys()
    return random.choice(list(keys))



# slackbotに返答させる
def make_reply(text):
    # まず単語を学習する
    if text[-1] != "。": text += "。"
    words = tokenizer.tokenize(text)
    register_dic(words)
    # 辞書に単語があれば、そこから話す
    for w in words:
        face = w.surface
        ps = w.part_of_speech.split(',')[0]
        if ps == "感動詞":
            return face + "。"
        if ps == "名詞" or ps == "形容詞":
            if face in dic: return make_sentence(face)
    return make_sentence("@")

#ここからメッセージ取得&返信

#
#
#以下、discord処理
#
#

client = discord.Client()



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')




@client.event

async def on_message(message):
    if client.user != message.author:
        text = message.content
        res = make_reply(text)
        await client.send_message(message.channel, res)


client.run('NDUzMTk5NzQ5MTY4ODg5ODg5.DfbiGg.9G6dSHtX1RN6EuMZ5mAcLx_j70M')
