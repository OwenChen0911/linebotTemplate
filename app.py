import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
import random,googlemaps,requests,json

from google_weather import get_weather_data

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
mKey = os.environ.get("GOOGLE_MAP_KEY")
gmaps = googlemaps.Client(key=mKey)

def getPaymentInfo():
    url = "https://sandbox-api-pay.line.me/v2/payments/request"

    payload = "{\r\n    \"amount\": 100,\r\n    \"productImageUrl\": \"http://placehold.it/84x84\",\r\n    \"confirmUrl\": \"127:0.0.1:8880/\",\r\n    \"productName\": \"Buy Bot\",\r\n    \"orderId\": \"15615156\",\r\n    \"currency\": \"TWD\"\r\n}"
    headers = {
  'X-LINE-ChannelID': '1656931714',
  'X-LINE-ChannelSecret': 'e8b70140c11946b1b56476e9633e01bd',
  'Content-Type': 'application/json;charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    reJson = response.json()

    print(reJson['returnMessage'])
    print(reJson['info']['paymentUrl']['web'])
    return reJson['info']['paymentUrl']['web']

#1

def getWeather(dist):
    URL = "https://www.google.com/search?lang_zh-CN&ie=UTF-8&q=天氣"
    try:
        data = get_weather_data(URL+ dist+" 攝氏")
        mDict={}
        mDict['region'] = data["region"]
        mDict['Now'] = data["dayhour"]
        mDict['Temperature'] = data["temp_now"]
        mDict['Description'] = data["weather_now"]
        print(data)
        print(f"Temperature now: {data['temp_now']}°C")
        return '地區 :　{reg} - {mNow}\n溫度 : {temp}\n{note}'.format(reg = mDict['region'],mNow = mDict['Now'],
                                                         temp = mDict['Temperature'],note = mDict['Description'])
    except Exception as ex:
        print('err : ',ex)
        return '阿........'

#tourist_attraction 景點 / restaurant  /  lodging
def getRestaurant(address,findType):
    #address  =  '高雄市三民區大昌二路152號'
    s = "https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&sensor=false".format(mKey,address)
    addreq = requests.get(s)
    addDic = addreq.json()
    lat = addDic['results'][0]['geometry']['location']['lat']
    lng = addDic['results'][0]['geometry']['location']['lng']
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=zh-TW&key={}&location={},{}&rankby=distance&type={}".format(mKey,lat,lng,findType)
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    goodRes = []
    for i in data['results']:
        try:
            if i['rating'] > 3.9 and i.get('photos') is not None:
                print('rate : ',i['rating'])
                goodRes.append(i)
        except:
            print('')


    if len(goodRes)<0:
        print('No one')

    restaurant = goodRes[random.randint(0,len(goodRes)-1)]
    thumbnail_image_url = ''
    if restaurant.get('photos') is None:
        print('No image')
    else:
        photo_ref = restaurant['photos'][0]['photo_reference']
        photo_width = restaurant['photos'][0]['width']
        thumbnail_image_url = 'https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}'\
        .format(mKey,photo_ref,photo_width)
        print(thumbnail_image_url)
        
       

    rating = "無" if restaurant.get('rating') is None else restaurant['rating']
    address = "None" if restaurant.get('vicinity') is None else restaurant['vicinity']
    details = "Google Map 評分 : {}\n地址 : {}".format(rating,address)

    map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(
        lat = restaurant['geometry']['location']['lat'], long = restaurant['geometry']['location']['lng'],place_id=restaurant['place_id'])
    
    
    return restaurant,details,map_url,thumbnail_image_url


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "123sHra~~~~~"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


def processFood(event,findType):
    restaurant,details ,map_url,thumbnail_image_url  = getRestaurant(event.message.text.replace('美食',''),findType)
    print('food')
    #thumbnail_image_url = 'https://www.google.com/search?rlz=1C1CHBD_zh-TW&tbs=lf:1,lf_ui:9&tbm=lcl&sxsrf=APq-WBvP9hiuov0mR5H8AD7xCQOd9ZiElA:1646187463802&q=%E9%BB%91%E5%BA%97&rflfq=1&num=10#rlfi=hd:;si:509673220156312110,l,Cgbpu5HlupdaCCIG6buR5bqXkgELbm9vZGxlX3Nob3CaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVUnRNM0V6YmpoM1JSQUKqAQ4QASoKIgbpu5HlupcoRQ,y,eJvyoaOJJa4;mv:[[22.6966268,120.3058832],[22.601616399999997,120.2911106]]'
            #ButtonsTemplate
    return TemplateSendMessage(
        alt_text= restaurant['name'],
        template=ButtonsTemplate(
            thumbnail_image_url = thumbnail_image_url,
            title = "這是您想要的 : " + restaurant['name'] + "?",
            text = details,
            actions = [
                URITemplateAction(
                    label="查看地圖",
                    uri = map_url
                    ),
                 PostbackTemplateAction(
                                        label='是',
                                        text='是',
                                        data='A&是'
                                    ),
                PostbackTemplateAction(
                                        label='否',
                                        text='否',
                                        data='A&否'
                                    )
                ]
            )
    )
                    
    
#https://developers.google.com/maps/documentation/places/web-service/supported_types
@handler.add(MessageEvent, message=TextMessage,PostbackEvent)
def handle_message(event):
    
    if isinstance(event, MessageEvent):
        print("MessageEvent")
    elif isinstance(event, PostbackEvent):
        print("PostbackEvent!!!")
        
    get_message = event.message.text
    if "美食" in event.message.text:
        replyData = []        
        replyData.append(processFood(event,'restaurant'))            
        line_bot_api.reply_message(event.reply_token,replyData)
    elif "住宿" in event.message.text:
        replyData = []        
        replyData.append(processFood(event,'lodging'))           
        line_bot_api.reply_message(event.reply_token,replyData)
    elif "景點" in event.message.text:
        replyData = []        
        replyData.append(processFood(event,'tourist_attraction'))        
        line_bot_api.reply_message(event.reply_token,replyData)        
    elif "天氣" in event.message.text:
        data = getWeather(event.message.text.replace('天氣',''))         
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=data))
    elif "付款" in event.message.text:
        url = 'https://linepayment0911.herokuapp.com/reserve'
        payUrl = response = requests.request("GET", url)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=payUrl.text)  )
    elif "評論" in event.message.text:
        #payUrl = getPaymentInfo()
        comment = '探探Tourism 問卷調查 \n {}'.format('https://docs.google.com/forms/u/0/d/11U1bFxMLEufwiBBxjLCBs_g7hJVCevkMMJA_MQsCw6w/viewform?edit_requested=true')
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=comment)  )
    else:
        rules = '機器人小規則\n※查美食 : 美食大昌一路15號\n※查天氣 : 天氣高雄市三民區\n※付款\n※評論\n※查景點 : 景點台中市大肚區\n※查飯店 : 住宿高雄市三民區'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=rules) )
       
        
