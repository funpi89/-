
# coding: utf-8

# In[ ]:


'''

整體功能描述

'''


# In[ ]:


'''

Application 主架構

'''

# 引用Web Server套件
from flask import Flask, request, abort
import requests
import random
from bs4 import BeautifulSoup
import goslate
from Beauty import Beauty
import tensorflow as tf
import numpy as np
from coco import *
import gc
# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

image_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet')
new_input = image_model.input
hidden_layer = image_model.layers[-1].output
image_features_extract_model = tf.keras.Model(new_input, hidden_layer)

# 載入基礎設定檔
secretFileContentJson=json.load(open("./line_secret_key",'r',encoding='utf8'))
server_url=secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__,static_url_path = "/素材" , static_folder = "./素材/")

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))

# azure cv mode
mode = "models/landmarks/analyze"

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# In[ ]:


'''

消息判斷器

讀取指定的json檔案後，把json解析成不同格式的SendMessage

讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage,TextSendMessage,ImageSendMessage,LocationSendMessage,FlexSendMessage,VideoSendMessage
)

from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
    
)

from linebot.models.template import *

def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName) as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            returnArray.append(VideoSendMessage.new_from_json_dict(jsonObject))    


    # 回傳
    return returnArray


# In[ ]:


'''

handler處理關注消息

用戶關注時，讀取 素材 -> 關注 -> reply.json

將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    
    # 讀取並轉換
    #result_message_array =[]
    #replyJsonPath = "素材/關注/reply.json"
    #result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
    linkRichMenuId = open("素材/rich_menu_a"+'/rich_menu_id', 'r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)

    # 消息發送
#     line_bot_api.reply_message(
#         event.reply_token,
#         result_message_array
#     )


# In[ ]:


'''

handler處理文字消息

收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json

轉譯json後，將消息回傳給用戶

'''

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage
)
from linebot.models.template import(
    ButtonsTemplate
)

# 文字消息處理
@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):

    if event.message.text == "我要看美女":
        page = random.randint(0,5)
        ptt_beauty = Beauty(page)
        title, sex_url, img = ptt_beauty.random_get_beautiful_lady()
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                text=title,
                actions=[
                  {
                    "type": "uri",
                    "label": title,
                    "uri": sex_url
                  }
                ],
        )
        )
        result_message_array = [
            ImageSendMessage(original_content_url=img,
                             preview_image_url=img),
            buttons_template_message
        ]
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    else:
        # 讀取本地檔案，並轉譯成消息
        result_message_array =[]
        replyJsonPath = "素材/"+event.message.text+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

        # 發送
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    
@handler.add(MessageEvent, message=ImageMessage)
def process_image_message_2_location(event):
    global mode
    #馬上跟用戶回復
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text='Image has Upload'))
    # 去跟line要照片
    message_content = line_bot_api.get_message_content(event.message.id)
    filename = event.message.id+'.jpg'
    with open(filename, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    # using azure cv
    img = open(filename, 'rb').read()
    subscription_key = "dabe7edfd998400a9d110ac7a4ecbec1"
    vision_base_url = "https://southeastasia.api.cognitive.microsoft.com/vision/v2.1/"
    analyze_url = vision_base_url + mode
    headers = {'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key 
              }
    if mode == "models/landmarks/analyze":
        params = {
            'visualFeatures': 'landmarks'
        }
        response = requests.post(analyze_url, headers=headers, params=params, data=img )
        analysis = response.json()
        print(analysis)
        if len(analysis["result"]["landmarks"]) > 0 :
            landmarkname = analysis["result"]["landmarks"][0]["name"]
        else:
            landmarkname = "無法辨識地標"
        try:
            gs = goslate.Goslate()
            landmarkname_CH = gs.translate(landmarkname, 'zh-CN')
        except:
            landmarkname_CH = "Google 不給翻譯"
        result_message_array = [
            TextSendMessage(text=landmarkname),
            TextSendMessage(text=landmarkname_CH)
        ]
        line_bot_api.reply_message(
           event.reply_token,
           result_message_array)
    else:
        descriptiontext = translate(filename, image_features_extract_model)
        try:
            gs = goslate.Goslate()
            descriptiontext_CH = gs.translate(descriptiontext, 'zh-TW')
        except:
            descriptiontext_CH = "Google 不給翻譯"
        result_message_array = [
            TextSendMessage(text=descriptiontext),
            TextSendMessage(text=descriptiontext_CH)
        ]
        line_bot_api.reply_message(
           event.reply_token,
           result_message_array)
        del descriptiontext
        gc.collect()


# In[ ]:


'''

handler處理Postback Event

載入功能選單與啟動特殊功能

解析postback的data，並按照data欄位判斷處理

現有三個欄位
menu, folder, tag

若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送

若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送

'''
from linebot.models import (
    PostbackEvent
)

from urllib.parse import parse_qs 

@handler.add(PostbackEvent)
def process_postback_event(event):
    


    query_string_dict = parse_qs(event.postback.data)
    
    print(query_string_dict)
    if 'folder' in query_string_dict:
    
        result_message_array =[]

        replyJsonPath = '素材/'+query_string_dict.get('folder')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'menu' in query_string_dict:
 
        linkRichMenuId = open("素材/"+query_string_dict.get('menu')[0]+'/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
        
#         replyJsonPath = '素材/'+query_string_dict.get('menu')[0]+"/reply.json"
#         result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
#         line_bot_api.reply_message(
#             event.reply_token,
#             result_message_array
#         )
    elif 'mode' in query_string_dict:
        global mode
        mode = query_string_dict.get('mode')[0]
        print("now is "+mode)


# In[ ]:


'''

Application 運行（開發版）

'''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[ ]:


'''

Application 運行（heroku版）

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])

