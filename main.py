import requests
import json


def get_cheapest_price_item_yahoo():

    itemsearchurl = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"

    # 文字列をutf8に変換
    # sentence = parse.quote(text.encode('utf-8'))

    # リクエストパラメーター
    params = {'Content-Type': 'application/json',
               'appid': 'XXXXXXXXXXXXXXXXXXXXXXXX',
               'query': 'AWS認定デベロッパーアソシエイト',
               'results': '1',
               'shipping': 'free',
               'sort': '+price'
               }

    # API接続の実行
    response = requests.get(itemsearchurl, params=params)
    results = response.json()

    # with open('./mydata.json', mode='wt', encoding='utf-8') as file:
    #    json.dump(results, file, ensure_ascii=False, indent=2)

    print('商品名：' + results['hits'][0]['name'])
    print('商品URL：' + results['hits'][0]['url'])
    print('価格：' + str(results['hits'][0]['price']))


if __name__ == "__main__":

    get_cheapest_price_item_yahoo()
