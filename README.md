![image](https://github.com/funpi89/-/blob/master/QRCode.png)
## 掃描QR Code即可使用
# 創作理由與使用客群
身為一位北漂青年，每次返回家鄉時必須搭乘高鐵、台鐵與客運等多種交通運輸工具，所以勢必要常常查詢各個交通運輸的時刻。
但無論是在手機裡的瀏覽器上重複搜尋各種大眾運輸的網站或是輪流使用它們的APP，使用感受都相當不便與費時，為了可以同一個頁面下進行各種大眾交通運輸工具的時刻查詢，我選擇了使用 line chat bot 裡面的 LIFF 功能來進行查詢系統的整合，並增加了些可以在搭車途中消遣的娛樂功能。
使用的後端架構為flask, 部屬至heroku上

## 使用LIFF實現大眾運輸工具查詢頁面的整合
![image](https://github.com/funpi89/-/blob/master/traffic_train.JPG)
![image](https://github.com/funpi89/-/blob/master/traffic_h_train.JPG)
![image](https://github.com/funpi89/-/blob/master/bus.JPG)
## 使用微軟azure的computer vision api進行對圖片的地偵測
![image](https://github.com/funpi89/-/blob/master/landmark.JPG)
## 使用自己訓練的image caption model對圖片進行翻譯,模型可參考我的github另一個專案https://github.com/funpi89/image_caption_with_selfAttention
![image](https://github.com/funpi89/-/blob/master/image_caption.JPG)
## 隨機挑選PTT表特版前5頁的其中一則文章的標題、網址與內文第一張圖片的 URL,可參考我的github另一個專案https://github.com/funpi89/cawlerPTTBeauty
![image](https://github.com/funpi89/-/blob/master/beauty.JPG)

