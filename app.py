import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage



from google_weather import get_weather_data

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
	
		# Send To Line
    reply = TextSendMessage(text=f"YoY : {get_message} " + getWeather('台中市龍井區'))
    line_bot_api.reply_message(event.reply_token, reply)
