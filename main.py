from tokens import cmc_token
from flask import Flask,render_template
from flask import request
from flask import Response
import requests
import re
import json
app = Flask(__name__)


token = '929812427:AAGoq0s5R7emzjGCGeks9X0onOld_RIKjwU'


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'GBP'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}
    r = requests.get(url, headers=headers, params=params).json()
    write_json(r, '/var/www/pydev/response.json')
    #if (r.status_code == requests.codes.ok):
    price = r['data'][crypto]['quote']['GBP']['price']
   # else:
       # price = -1
    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    write_json(txt, '/var/www/pydev/txtmesg.txt')
    pattern = r'/[a-zA-Z]{2,4}'

    ticker = re.findall(pattern, txt)
    write_json(ticker, '/var/www/pydev/ticker.txt')
    if ticker:
        symbol = ticker[0][1:].upper()
        write_json(symbol, '/var/www/pydev/symbol_txt.txt')
    else:
        symbol = ''

    return chat_id, symbol    


def send_message(chat_id, text='bla-bla-bla'):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}


    r = requests.post(url, json=payload)
    print(r)
    return r



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        write_json(msg, '/var/www/pydev/msg.txt')
        chat_id, symbol = parse_message(msg)

        if not symbol:
            print(chat_id)
            write_json(chat_id, '/var/www/pydev/non_request.json')
            send_message(chat_id, 'I am a bot, I will give you limited information related to bitcoin at present, Thanks for contact us')
            return Response('ok', status=200)

        
        price = get_cmc_data(symbol)
        
        if (price < 0):
            send_message(chat_id, 'Please enter valid bitcoin symbol')
        else:
            send_message(chat_id, price)
        write_json(msg, '/var/www/pydev/telegram_request.json')
        return Response('ok', status=200)
    else:
        return '<h2>Welcome Arima</h2>'
     #return redirect("https://pydev.dqserv.com", code=302)
#    waat = '<h2>Welcome to Arima World</h2>' + str(print(cmc_data)) + 'This is new' 
#    return print(waat)

def main():
    print(get_cmc_data('BTC')) 
     

if __name__ == "__main__":
    app.run(debug=True)

   # main()
