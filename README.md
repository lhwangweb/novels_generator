# 說明
 - 小說產生器，輸入某些小說並作訓練後，輸出類似風格的新章節
    - scrape 製作的爬蟲會先把已有章節爬回來，存到 mongo
    - 決定語料的篇幅，例如 5 篇，則 LSTM 模型便會讀入五篇文章，並反覆訓練 (RNN)
    - 完成訓練後，按照訓練結果產生文章
 - 由於訓練就是在統計此文的字詞之間的關係，這是一種量化的『文風』，因此依此結果輸出之文章，會帶有類似的文風，但很可能完全不合中文的正常語意。

# 技術
   - Python 3.6.9
   - 爬蟲： Scrapy 1.5.1 + Mongo 儲存
   - 文章產生： TensorFlow 2.1.0 (CPU Only), Keras 跑 LSTM 來進行訓練＆預測文章
   - 瀏覽結果： Django 2.1.5 + Mongo 做個簡單的小 web，瀏覽產生的文章

# 成果範例
## 成果文章

1. 取 5 篇，訓練 59 次， batch_size=32, seq_len=20 (耗費約 1.5 hr)
  
   節錄部分結果如下：
   
```
教去之這，你是以麼年不一”李的在””奧恩苦淡道：道：“是魔開時餐將定會一一千年封魔石，“托六個十人人早早的人，通常因況這一一年於來，，飯我一一的武後，衰常我來，：時的是麼 ...
```

   可以看到，已經開始稍微能成句，有標點有斷句，但語意當然是亂七八糟。

2. 取 10 篇，訓練 300 次  batch_size=8, seq_len=32(耗費約 16 hr)
   ```
   
   ```

# 安裝步驟
1. 環境安裝
   - 使用 Dockerfile 建構環境，提供建立指令參考：
   ```bash
   host-user$ docker image build -t python/novels:18.04 /Path/To/novels_generator/
   host-user$ docker run -itd -p 8888:8888 -v /Path/To/novels_generator/:/var/www/html --name novels python/novels:18.04
   host-user$ docker exec -it novels bash
   docker-root# .... (這裏已進入 docker 內的 bash 環境)
   
   注意 /Path/To/novels_generator/ 請改成您自己的路徑
   ```
   - docker 內包含了爬蟲、文章產生以及瀏覽的環境。
   - 如果不使用 Docker，可自行參照 Dockerfile 及 requirements.txt 內容來建構環境。
   
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
   MONGO_HOST= "mongodb"
   MONGO_DBNAME = "novels"
   ```

# 使用步驟

## 爬取文章

1. 進入目錄並執行爬蟲指令，
   ```bash
   docker-root# cd novels_spider
   docker-root# scrapy crawl UU
   ```
   - 如果想看更多 Console Log，請調整 Log Level， 在 novels_spider/novel/settings.py L93，
   - 如果想換一本書，請編輯 novels_spider/novel/spiders/UU.py L16，換其他本的網址即可

2. 到 mongo 查看 raw_articles 這個 collection ，看文章是否成功收錄

## 訓練＆產生新文章

1. 進入目錄並執行 LSTM 相關指令
   ```bash
   docker-root# cd novels_lstm
   docker-root# python main.py N M
   ```
   - N - 取用幾篇文章來當成語料。
   - M - 訓練閱讀次數

2. 訓練過程的 Console Log 範例
   ```bash
   Epoch 00060: loss improved from 0.57488 to 0.57097, saving model to ./weights-improvement.hdf5
   Epoch 61/100
   12087/12087 [==============================] - 60s 5ms/step - loss: 0.5987
   ```

3. 成功後，可到 Mongo 查看 articles 這個 collection 

   
## 瀏覽產生的文章

方法一： 到 Mongo 查看 articles 這個 collection

方法二： Django 

   1. Django 啟動 - 執行 Django 的 runserver 啟動

   ```bash
   docker-root# cd novels_web
   docker-root# python3 manage.py runserver 0.0.0.0:8888
   ```

   2. 啟動後即可以瀏覽器連接 http://localhost:8888 查看生成的文章

