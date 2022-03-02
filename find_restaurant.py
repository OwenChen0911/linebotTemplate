import googlemaps,requests,json,re
from datetime import datetime
from google_weather import get_weather_data


mKey =  os.environ.get("GOOGLE_MAP_KEY")
gmaps = googlemaps.Client(key=mKey)

address  =  '高雄市三民區大昌二路152號'
s = "https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&sensor=false".format(mKey,address)
addreq = requests.get(s)

addDic = addreq.json()
lat = addDic['results'][0]['geometry']['location']['lat']
lng = addDic['results'][0]['geometry']['location']['lng']

#-
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

restaurant = goodRes[8]

if restaurant.get('photos') is None:
    print('No image')
else:
    photo_ref = restaurant['photos'][0]['photo_reference']
    photo_width = restaurant['photos'][0]['width']
    thumbnail_image_url = 'https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}'\
    .format(mKey,photo_ref,photo_width)
    st = restaurant['photos'][0]['html_attributions'][0]
    print('Imgae : ',thumbnail_image_url)



rating = "無" if restaurant.get('rating') is None else restaurant['rating']
address = "None" if restaurant.get('vicinity') is None else restaurant['vicinity']
details = "Google Map 評分 : {}\n地址 : {}".format(rating,address)

map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(
    lat = restaurant['geometry']['location']['lat'], long = restaurant['geometry']['location']['lng'],
    place_id=restaurant['place_id'])


#print(map_url)
URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
data = get_weather_data(URL+ "台中市龍井區")
mDict={}
mDict['region'] = data["region"]
mDict['Now'] = data["dayhour"]
mDict['Temperature'] = data["temp_now"]
mDict['Description'] = data["weather_now"]

print(mDict)

    

