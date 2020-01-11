# 說明
 - scrapy 為基礎的爬蟲，爬曲
 - 抓取小說後，儲存到 mongo 內

# 技術
   - 爬蟲： Scrapy + Mongo 儲存
   - 文章產生： TensorFlow, Keras 跑 LSTM 來進行訓練＆預測文章
   - 瀏覽結果： Django + Mongo 做個簡單的小 web，瀏覽產生的文章

# 成果範例
## 成果文章
   ```javascript

   ```
## 訓練參數
1. 訓練次數 300
2. 預測新文字之句長 30
3. 每批樣本數 32
4. 使用文章篇數 50
5. 時間

# 安裝步驟
1. 環境安裝
   - 使用 Dockerfile 建構環境，提供建立指令參考：
   ```bash
   user$ docker image build -t python/novels:18.04 /Path/To/novels_generator/
   user$ docker run -itd -p 8888:8888 -v /Path/To/novels_generator/:/var/www/html --name novels python/novels:18.04
   user$ docker exec -it novels bash
   root# ....
   
   注意 /Path/To/novels_generator/ 請改成您自己的路徑
   ```
   - docker 內包含了爬蟲、文章產生以及瀏覽的環境。
   - 如果不使用 Docker，可自行參照 Dockerfile 及 requirements.txt 內容來建構環境
   
2. Mongo 相關
   - 建立 1 個 db，名稱: novels
   - 建立 3 個 collections，名稱: links, articles, raw_articles
   - 建立可存取 novels 的帳密，例如: test_user/test_password
   
3. 連線資訊
   - 編輯 novels_spider/novel/db/\__init__.py 約 L3 ，替換 Mongo 連線資訊(如下範例)
   - 編輯 novels_web/novels_web/settings.py 約 L77 ，替換 Mongo 連線資訊(如下範例)
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

1. 進入目錄並執行爬蟲指令
   ```bash
   user$ cd novels_spider
   user$ scrapy crawl UU
   ```
   - 如果想看更多 Console Log，請調整 Log Level， 在 novels_spider/novel/settings.py L93，
   - 如果想換一本書，請編輯 novels_spider/novel/spiders/UU.py L16，換其他本的網址即可

2. 到 mongo 查看 raw_articles 看文章是否成功收錄

## 產生新文章

1. 進入目錄並執行 LSTM 相關指令
   ```bash
   user$ cd novels_lstm
   user$ python main.py N M
   ```
   - N 取用幾篇文章來當成語料。
   - M 訓練閱讀次數

2. 訓練過程的 Console Log 範例
   ```bash
   Epoch 00060: loss improved from 0.57488 to 0.57097, saving model to ./weights-improvement.hdf5
   Epoch 61/100
   12087/12087 [==============================] - 60s 5ms/step - loss: 0.5987
   ```

3. 成功後，可到 Mongo 查看 articles


4. Django 啟動
   - cd novels_web
   - python3 manage.py runserver 0.0.0.0:8888
   - 以瀏覽器連接 http://localhost:8888 查看生成的文章