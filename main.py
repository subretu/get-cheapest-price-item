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
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (  # 使用するモデル(イベント, メッセージ, アクションなど)を列挙
    FollowEvent, UnfollowEvent, MessageEvent, PostbackEvent, TextMessage,
    TextSendMessage, TemplateSendMessage, ButtonsTemplate, CarouselTemplate,
    CarouselColumn, PostbackTemplateAction, StickerSendMessage, MessageAction,
    ConfirmTemplate, PostbackAction)

app = Flask(__name__)

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


@app.route("/callback", methods=['POST'])
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

# 最安値取得
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

    # with open('./mydata.json', mode='wt', encoding='utf-8') as file:
    #    json.dump(results, file, ensure_ascii=False, indent=2)

    #print('商品名：' + results['hits'][0]['name'])
    #print('商品URL：' + results['hits'][0]['url'])
    #print('価格：' + str(results['hits'][0]['price']))

    return results['hits'][0]['name'], results['hits'][0]['url'], results['hits'][0]['price']


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):

    # 受信メッセージを分割
    umsg = event.message.text.split()

    reply_text_list = get_cheapest_price_item_yahoo(umsg[0])
    reply_text = "うーん、今の日本における最安値の商品はこれですかね。\n\n" + "商品名：" + reply_text_list[0] + "\n" + "価格：" + str(
        reply_text_list[2]) + "\n" + "商品URL：" + reply_text_list[1]

    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=reply_text))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
