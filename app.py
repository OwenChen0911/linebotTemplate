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

def getWeather(dist):
    URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=天氣"
    try:
        data = get_weather_data(URL+ dist)
        mDict={}
        mDict['region'] = data["region"]
        mDict['Now'] = data["dayhour"]
        mDict['Temperature'] = data["temp_now"]
        mDict['Description'] = data["weather_now"]
        print(mDict)
        return '地區 :　{reg} - {mNow}\n溫度 : {temp}\n{note}'.format(reg = mDict['region'],mNow = mDict['Now'],
                                                         temp = mDict['Temperature'],note = mDict['Description'])
    except Exception as ex:
        print('err : ',ex)
        return '阿........'

def getRestaurant(address):
    #address  =  '高雄市三民區大昌二路152號'
    s = "https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&sensor=false".format(mKey,address)
    addreq = requests.get(s)
    addDic = addreq.json()
    lat = addDic['results'][0]['geometry']['location']['lat']
    lng = addDic['results'][0]['geometry']['location']['lng']
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=zh-TW&key={}&location={},{}&rankby=distance&type=restaurant".format(mKey,lat,lng)
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    goodRes = []
    for i in data['results']:
        try:
            if i['rating'] > 3.9:
                print('rate : ',i['rating'])
                goodRes.append(i)
        except:
            print('')


    if len(goodRes)<0:
        print('No one')

    restaurant = goodRes[2]

    if restaurant.get('photos') is None:
        print('No image')
    else:
        photo_ref = restaurant['photos'][0]['photo_reference']
        photo_width = restaurant['photos'][0]['width']
        thumbnail_image_url = 'https://maps.googleapis.com/maps/api/place/photo?key{}&photoreference={}&maxwidth={}'\
        .format(mKey,photo_ref,photo_width)
        
       

    rating = "無" if restaurant.get('rating') is None else restaurant['rating']
    address = "None" if restaurant.get('vicinity') is None else restaurant['vicinity']
    details = "Google Map 評分 : {}\n地址 : {}".format(rating,address)

    map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(
        lat = restaurant['geometry']['location']['lat'], long = restaurant['geometry']['location']['lng'],place_id=restaurant['place_id'])
    
    
    return restaurant,details,map_url,thumbnail_image_url


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "123sHra~~~~~{}".format(getWeather('台中市龍井區'))
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


def processFood(event):
    restaurant,details ,map_url,thumbnail_image_url  = getRestaurant(event.message.text.replace('美食',''))
    print('food')          
            
    return TemplateSendMessage(
        alt_text= restaurant['name'],
        template=ButtonsTemplate(
            thumbnail_image_url = thumbnail_image_url,
            title = restaurant['name'],
            text = details,
            actions = [
                URITemplateAction(
                    label="查看地圖",
                    uri = map_url
                    ),
                ]
            )
    )
                    
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
    if "美食" in event.message.text:
        replyData = []
        replyData.append(processFood(event))
        line_bot_api.reply_message(event.reply_token,replyData)
    elif "天氣" in event.message.text:
        data = getWeather(event.message.text.replace('天氣',''))         
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=data))
    else:
        reply = TextSendMessage(text=f"YoY : {get_message}")
        line_bot_api.reply_message(event.reply_token, reply)
        
