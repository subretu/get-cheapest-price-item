# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import requests
import json
import datetime
import uvicorn
from fastapi import FastAPI, Request
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (  # 使用するモデル(イベント, メッセージ, アクションなど)を列挙
    FollowEvent, UnfollowEvent, MessageEvent, PostbackEvent, TextMessage,
    TextSendMessage, TemplateSendMessage, ButtonsTemplate, CarouselTemplate,
    CarouselColumn, PostbackTemplateAction, StickerSendMessage, MessageAction,
    ConfirmTemplate, PostbackAction)

app = FastAPI()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.post("/callback")
def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)

    # handle webhook body

    handler.handle(body, signature)

    # LINEサーバへHTTP応答を返す
    return "ok"

# Yahooより最安値取得関数
def get_cheapest_price_item_yahoo(keyword):

    itemsearchurl = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"

    # 文字列をutf8に変換
    # sentence = parse.quote(text.encode('utf-8'))

    # リクエストパラメーター
    params = {'Content-Type': 'application/json',
              'appid': os.getenv('YAHOO_API_ID', None),
              'query': keyword,
              'results': '1',
              'shipping': 'free',
              'sort': '+price'
              }

    # API接続の実行
    response = requests.get(itemsearchurl, params=params)
    results = response.json()

    return results['hits'][0]['name'], results['hits'][0]['url'], results['hits'][0]['price']

# 楽天より最安値取得関数
def get_cheapest_price_item_rakuten(keyword):

    itemsearchurl = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"

    # 文字列をutf8に変換
    # sentence = parse.quote(text.encode('utf-8'))

    # リクエストパラメーター
    params = {'Content-Type': 'application/json',
              'applicationId': os.getenv('RAKUTEN_API_ID', None),
              "format": "json",
              "formatVersion": 2,
              "keyword": keyword,
              "availability": 0,
              "hits": 10,
              "page": 1,
              "sort": "+itemPrice",
              "NGKeyword": "中古",
              "postageFlag": 1
              }

    # API接続の実行
    response = requests.get(itemsearchurl, params=params)
    results = response.json()

    return results['Items'][0]['itemName'], results['Items'][0]['itemUrl'], results['Items'][0]['itemPrice']


@handler.add(MessageEvent, message=TextMessage)
async def message_text(event):

    # 受信メッセージを分割
    umsg = event.message.text.split()

    result_list_yahoo = get_cheapest_price_item_yahoo(umsg[0])
    result_list_rakuten = get_cheapest_price_item_rakuten(umsg[0])

    if result_list_yahoo[2] < result_list_rakuten[2]:
        reply_text = "うーん、今の日本における最安値の商品はこれですかね。\n\n" + "商品名：" + \
            result_list_yahoo[0] + "\n" + "価格：" + \
            str(result_list_yahoo[2]) + "\n" + "商品URL：" + result_list_yahoo[1]
    elif result_list_yahoo[2] > result_list_rakuten[2]:
        reply_text = "うーん、今の日本における最安値の商品はこれですかね。\n\n" + "商品名：" + \
            result_list_rakuten[0] + "\n" + "価格：" + \
            str(result_list_rakuten[2]) + "\n" + \
            "商品URL：" + result_list_rakuten[1]
    # 現時点ではYahooの方を返すようにしているが、ポイントを加味するようにする予定
    elif result_list_yahoo[2] == result_list_rakuten[2]:
        reply_text = "うーん、今の日本における最安値の商品はこれですかね。\n\n" + "商品名：" + \
            result_list_yahoo[0] + "\n" + "価格：" + \
            str(result_list_yahoo[2]) + "\n" + "商品URL：" + result_list_yahoo[1]
    else:
        reply_text = "うーん、もう一度検索ワードを入れてもらえるかな？"

    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=reply_text))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)