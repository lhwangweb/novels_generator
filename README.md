## 說明

 - 小說產生器，輸入某些小說並作訓練後，輸出類似風格的新章節，流程如下：
    - 爬蟲(Scrapy)會先把已有章節爬回來，存到 Mongo
    - 決定想拿哪些文章來做訓練基礎，例如前 N 篇
    - 以 LSTM 模型讀入 N 篇文章並反覆訓練 M 次，完成後依訓練結果預測後續文字 P 個
    - P 個文字內包含標點與斷行，故即為新章節

## 技術

   - Python 3
   - 爬蟲： Scrapy 1.5.x + Mongo 儲存
   - 文章產生： TensorFlow 2.1.0 (CPU Only), Keras 跑 LSTM 進行訓練＆預測文章
   - 瀏覽結果： Django 2.1.x + Mongo 做個簡單的小 web，瀏覽產生的文章

## 成果範例文章

1. 小說『[巫師生活指南](https://sj.uukanshu.com/book.aspx?id=83004)』前 5 篇，訓練 59 次， batch_size=32, sequence_length=20 (耗費約 1.5 hr)

   ```chinese
   教去之這，你是以麼年不一”李的在””奧恩苦淡道：道：“是魔開時餐將定會一一千年封魔石，“
   
   托六個十人人早早的人，通常因況這一一年於來，，飯我一一的武後，衰常我來，：時的是麼 ...
   ```
   
   可以看到： 有標點有斷句，稍微能成句。但不要說語意了，句構都亂七八糟。

2. 小說『[巫師生活指南](https://sj.uukanshu.com/book.aspx?id=83004)』前 10 篇，訓練 300 次  batch_size=8, sequence_length=8 (耗費約 13 hr)

   ```chinese
   洛娜道：“你給我講的故事裏，巫師都是壞人，我要得，身，主以一洛娜道着立你頭命，洛娜看在古的。，藥那二一最一加你你睡李作來
   
   拉爾朝着一道！“那鬼：“是很是一的的友爲，不
   
   奧爾摸頭李昂道：“一主晚雖，你，你不一階天莉”？個人主們拉也大，，一不
   托爾有笑頭道“我昂來點，都不，，怎人。我你怕我決龍不我了不是不晶，的這，光
   ```
   
   可以看到，稍微有一些比較接近文章的句構出現，以及人名基本上都已經被記起來
   
   注意，上面的斷行不是我加的，是訓練後的機器按照原文風格加的

## 安裝步驟

1. 環境安裝
   - 使用 Docker 建構環境，提供建立指令參考：

   ```bash
   host-user$ docker image build -t python/novels:18.04 /Path/To/novels_generator/
   host-user$ docker run -itd -p 8888:8888 -v /Path/To/novels_generator/:/var/www/html --name novels python/novels:18.04
   host-user$ docker exec -it novels bash
   docker-root# .... (這裏已進入 docker 內的 bash 環境)
   
   注意： /Path/To/novels_generator/ 請改成您自己放置 novels_generator 的路徑
   ```
   - Docker 內包含了爬蟲、文章產生以及瀏覽的環境。
   - 如果不使用 Docker，可自行參照 Dockerfile 及 requirements.txt 內容來建構環境
   
2. Mongo 相關工作
   - 建立 1 個 db，名稱: novels
   - 建立 3 個 collections，名稱: links, articles, raw_articles
   - 建立可存取 novels 的帳密，例如: test_user/test_password
   
3. 連線資訊
   - 編輯 novels_spider/novel/db/\__init__.py 約 L3 ，替換 Mongo 連線資訊(如下範例)
   - 編輯 novels_web/novels_web/settings.py 約 L87 ，替換 Mongo 連線資訊(如下範例)
   - 編輯 novels_lstm/main.py 約 L14 ，替換 Mongo 連線資訊(如下範例)

   ```python
   # Mongo 連線資訊
   MONGO_USER="test_user"
   MONGO_PASSWD="test_password"
   MONGO_HOST= "your.mongodb.host"
   MONGO_DBNAME = "novels"
   ```

## 使用步驟

### 爬取文章

1. 進入目錄並執行爬蟲指令
   ```bash
   docker-root# cd novels_spider
   docker-root# scrapy crawl UU
   ```
   - 如果想看更多 Console Log，請調整 Log Level
      - 在 novels_spider/novel/settings.py L93
      - 把 LOG_LEVEL = 'ERROR' 改為 INFO 之類的層級，可觀察到詳細的輸出
   - 如果想換一本書，請編輯 novels_spider/novel/spiders/UU.py L16，換其他本的網址即可

2. 到 Mongo 查看 raw_articles 這個 collection ，看文章是否成功收錄

### 訓練＆產生新文章

1. 進入目錄並執行 LSTM 相關指令
   ```bash
   docker-root# cd novels_lstm
   docker-root# python3 main.py
   ```
   
2. 訓練過程的 Console Log 範例
   ```bash
   Epoch 00060: loss improved from 0.57488 to 0.57097, saving model to ./weights-improvement.hdf5
   Epoch 61/100
   12087/12087 [==============================] - 60s 5ms/step - loss: 0.5987
   ```

3. 成功後，可到 Mongo 查看 articles 這個 collection 

4. 要改善結果，可以調整訓練參數，可到 novels_lstm/main.py 約 L230，調整一些初步參數。

   ```python
   # 用於預測新字的句子長度
   sequence_length = 6

   # 每批訓練的樣本數 batch_size大小選擇: https://www.zhihu.com/question/32673260
   batch_size = 4

   # 要用幾篇文章訓練
   num_articles = 1

   # 訓練次數
   epochs = 100
   ```

   或者進一步自行調整 function 中的 LSTM 模型

   ```python
   def make_lstm_model(raw_text= "", sequence_length=10):
   ```

### 瀏覽產生的文章

方法一： 到 Mongo 查看 articles 這個 collection

方法二： 用 Django 寫的介面來看

   1. Django 啟動 - 執行 Django 的 runserver 來做啟動

   ```bash
   docker-root# cd novels_web
   docker-root# python3 manage.py runserver 0.0.0.0:8888
   ```

   2. 啟動後，即可以瀏覽器連接 http://localhost:8888 ，查看生成的文章

## 參考資料

### 爬蟲篇
1. [Scrapy-Splash 說明文件](https://splash-cn-doc.readthedocs.io/zh_CN/latest/scrapy-splash-toturial.html)

2. [[Day 22] 實戰：Scrpay 爬取動態網頁](https://ithelp.ithome.com.tw/articles/10208357)
3. [爬虫之scrapy-splash——scrapy+js渲染容器](https://www.jianshu.com/p/2516138e9e75)

### 機器學習篇
1. [Text Generation With LSTM Recurrent Neural Networks in Python with Keras](https://machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/)

2. [RNN入門（三）利用LSTM生成旅遊點評](https://www.cnblogs.com/jclian91/p/9863848.html)
3. [讓 AI 寫點金庸：如何用 TensorFlow 2.0 及 TensorFlow.js 寫天龍八部](https://leemeng.tw/how-to-generate-interesting-text-with-tensorflow2-and-tensorflow-js.html)

### Django
1. [Django 官網的 Get Start (2.1)](https://docs.djangoproject.com/zh-hans/2.1/intro/)
2. [MongoDB with Python & MongoEngine | MongoDB & Python Pt. 1](https://pythonise.com/series/mongodb-and-python/mongodb-python-mongoengine-pt1)
3. [MongoEngine 說明文件](http://docs.mongoengine.org/apireference.html)


## LICNESE ＆ COPYRIGHT
### novels_spider

爬蟲部分採 UNLICENSE，請參考 LICENSE 檔案

### novels_web

Web 瀏覽部分採 UNLICENSE，請參考 LICENSE 檔案

### novels_lstm

Copyright (c) Original Authors 所有權利應保留給原作者：Jason Brownlee, 山陰少年

1. [Jason Brownlee, Text Generation With LSTM Recurrent Neural Networks in Python with Keras](https://machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/)

2. [山陰少年, RNN入門（三）利用LSTM生成旅遊點評](https://www.cnblogs.com/jclian91/p/9863848.html)

LSTM 模型這部分，我仿照了上述兩篇文章的步驟以及大部分設置，完成了這個練習。因此需聲明在這部分本人無任何權利，所有權利應歸屬兩位原作者。
