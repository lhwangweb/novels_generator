import re
import html2text
import sys, os, traceback
from datetime import datetime

import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

# Mongo 連線資訊
MONGO_USER="test_user"
MONGO_PASSWD="test_password"
MONGO_HOST= "mongodb"
MONGO_DBNAME = "novels"

def read_article(aricles_num=5):
    """
    讀入文章 - 從 mongo 內讀出 aricles_num 篇文章，並剔除不需要的內容後，組合為訓練用的語料
        aricles_num - 篇數
    """
    import pymongo
    client = pymongo.MongoClient(
        host = MONGO_HOST,
        username = MONGO_USER,
        password = MONGO_PASSWD,
        authSource = MONGO_DBNAME,
        authMechanism = 'SCRAM-SHA-1',
        port = 27017,
    )
    novels_db = client.novels
    raw_articles = novels_db.raw_articles

    articles = raw_articles.find({}).limit(aricles_num)
    ht_inst = html2text.HTML2Text()
    ht_inst.ignore_links = True

    text = ""
    for article in articles:
        content = article["content"]
        # 清除不必要的內容
        content = content.replace("UＵ看書", "").replace("ＵU看書", "").replace("UU看書", "").replace("ＵＵ看書", "").replace("章節缺失、錯誤舉報", "").replace("…", "")
        content = content.replace("Ｕ", "U").replace("ｗ", "w").replace("ｕ", "u").replace("ｓ", "s").replace("．", ".").replace(".", ".").replace("ｋ", "k").replace("ａ", "a").replace("ｎ", "n").replace("ｈ", "h").replace("ｃ", "o").replace("ｏ", "o").replace("ｍ", "m")
        content = content.replace("www.uukanshu.coｍ", "")
        content = ht_inst.handle(content)
        # content = re.sub(r'\s+', '', content, flags = re.MULTILINE)
        text += content

    return text


def save_article(result_data):
    """
    把新文章存到 Mongo
    """
    import pymongo
    client = pymongo.MongoClient(
        host = MONGO_HOST,
        username = MONGO_USER,
        password = MONGO_PASSWD,
        authSource = MONGO_DBNAME,
        authMechanism = 'SCRAM-SHA-1',
        port = 27017,
    )
    novels_db = client.novels
    articles = novels_db.articles
    articles.insert_one(result_data)
    return True
    
def make_lstm_model(raw_text= "", sequence_length=10):
    """
    建立適當的 LSTM 模型
        raw_text 完整語料
        sequence_length 預測新字所使用之句長
    """
    if raw_text:
        # 先把語料製作為 text <-> int 比對的 dict，兩種 key-value 關係的都要
        uniq_words = sorted(list(set(raw_text)))
        text_int_relation = dict((it, ii) for ii, it in enumerate(uniq_words))
        int_text_relation = dict((ii, it) for ii, it in enumerate(uniq_words))
        no_words = len(raw_text)
        uniq_no_words = len(uniq_words)

        dataX = []
        dataY = []
        for i in range(0, no_words-sequence_length, 1):
            seq_in = raw_text[i:i + sequence_length]
            seq_out = raw_text[i + sequence_length]
            dataX.append([text_int_relation[char] for char in seq_in])
            dataY.append(text_int_relation[seq_out])
        
        n_patterns = len(dataX)
        X = numpy.reshape(dataX, (n_patterns, sequence_length, 1))
        X = X/uniq_no_words
        y = np_utils.to_categorical(dataY)

        # 定義＆產生 LSTM 模型
        lstm_model = Sequential()
        lstm_model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
        lstm_model.add(Dropout(0.2))
        lstm_model.add(Dense(y.shape[1], activation='softmax'))
        lstm_model.compile(loss='categorical_crossentropy', optimizer='adam')

        return {
            "lstm_model":lstm_model,
            "text_int_relation":text_int_relation,
            "int_text_relation":int_text_relation,
            "no_words":no_words,
            "uniq_no_words":uniq_no_words,
            "X": X,
            "y": y
        }
    else:
        return None

def keras_train(lstm_model_data=None, epochs = 1, batch_size= 32, verbose=1, weight_filename = './weights-records.hdf5'):
    """
    訓練 - 針對數入的語料進行 epochs 次的閱讀訓練
        lstm_model_data - LSTM Model 相關資料
        epochs - 訓練次數
        batch_size - 每批訓練的樣本數
        verbose - Log 詳細度
        weight_filename - 訓練結果的檔名
    """
    if lstm_model_data and "lstm_model" in lstm_model_data and "X" in lstm_model_data and "y" in lstm_model_data:
        lstm_model = lstm_model_data["lstm_model"]
        X = lstm_model_data["X"]
        y = lstm_model_data["y"]
        checkpoint = ModelCheckpoint(weight_filename, monitor='loss', verbose=verbose, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]
        lstm_model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=callbacks_list)
    else:
        print("Model Empty")

def keras_generate(lstm_model_data = None, raw_text="", sequence_length = 10, article_length = 1000, weight_filename = './weights-records.hdf5'):
    """
    產生文章 - 訓練模型記住文章的風格，根據風格推斷接下來的文字為何
        lstm_model_data - LSTM Model 相關資料
        raw_text
        sequence_length - 用於預測新字的句子長度
        article_length - 欲產生的文章長度
        weight_filename - 訓練結果的檔名
    """
    result_article = ""
    if lstm_model_data and "lstm_model" in  lstm_model_data and os.path.isfile(weight_filename):
        lstm_model = lstm_model_data["lstm_model"]
        text_int_relation = lstm_model_data["text_int_relation"]
        int_text_relation = lstm_model_data["int_text_relation"]
        no_words = lstm_model_data["no_words"]
        uniq_no_words = lstm_model_data["uniq_no_words"]

        # 載入訓練資料
        lstm_model.load_weights(weight_filename)
        if not uniq_no_words:
            uniq_no_words = len(sorted(list(set(raw_text))))
        
        # 輸入文字 - 就是語料末尾的 sequence_length 個字 
        input_text = raw_text[(0-sequence_length):]

        # 轉換為數字版 int_pattern
        int_pattern = [text_int_relation[value] for value in input_text]

        for i in range(article_length):
            # 預測下一個字
            x = numpy.reshape(int_pattern, (1, len(int_pattern), 1))
            x = x / float(uniq_no_words)
            prediction = lstm_model.predict(x, verbose=0)
            # 取得新字 累加到文章內
            index = numpy.argmax(prediction)
            result_article += int_text_relation[index]
            # shift int_pattern  新字加入尾部，首字移除
            int_pattern.append(index)
            int_pattern = int_pattern[1:len(int_pattern)]
    
    return result_article


def main(num_articles = 5, epochs = 1, sequence_length = 10, batch_size = 32):
    """
    文章產生器
        Mongo 讀出 num_articles 篇文章作為訓練材料，訓練 epochs 次以後，預測出新的一篇文章
        參考文件： jclian91  RNN入門（三）利用LSTM生成旅遊點評 https://www.cnblogs.com/jclian91/p/9863848.html
    """
    result = ""
    
    # 讀入預備訓練的文章
    raw_text = read_article(num_articles)

    # 取得單篇文章的平均長度 -> 新文章的長度
    article_length_avg = len(raw_text)//num_articles

    if raw_text:
        fp = open("./raw_text.txt", "w")
        fp.write(raw_text)
        fp.close()
        print("raw_text.txt 產生完畢，共計 " + str(len(raw_text)) + " 字")
        # 模型建立
        lstm_model_data = make_lstm_model(raw_text= raw_text, sequence_length=sequence_length)
        # 訓練
        keras_train(lstm_model_data=lstm_model_data, epochs=epochs,  batch_size= 32, verbose=1, weight_filename = './weights-records.hdf5')
        # 預測文章
        result_article = keras_generate(lstm_model_data=lstm_model_data, raw_text = raw_text, sequence_length=sequence_length, article_length=article_length_avg, weight_filename = './weights-records.hdf5')
        # 儲存
        if result_article:
            save_article({
                "title":result_article[0:10],
                "content":result_article,
                "epochs":epochs,
                "num_articles":num_articles,
                "sequence_length":sequence_length,
                "article_length":article_length_avg,
                "first_input":raw_text[(0-sequence_length):],
                # "raw_text":raw_text,
                "created_at": datetime.utcnow()
            })
            print("新文章儲存完成")
        else:
            print("此次無新文章")

if __name__ == '__main__':
    try:
        if len(sys.argv) == 3:
            # 用於預測新字的句子長度
            sequence_length = 32
            # 每批訓練的樣本數 batch_size大小選擇: https://www.zhihu.com/question/32673260
            batch_size = 8
            # 要用幾篇文章訓練
            num_articles = int(sys.argv[1])
            # 訓練次數
            epochs = int(sys.argv[2])

            main(num_articles=num_articles, epochs=epochs, sequence_length=sequence_length, batch_size=batch_size)
        else:
            print("Usage: python3 main.py N M")
            print("       N: 文章篇數")
            print("       M: 訓練次數")
    except Exception as e:
        print("發生錯誤")
        print(str(e))
        print(traceback.format_exc())
