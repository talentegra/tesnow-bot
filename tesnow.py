from tokens import cmc_token
from tokens import auth_token
from tokens import telegram_token
from flask import Flask,render_template
from flask import request
from flask import Response
import requests
import re
import json
import jsonify
app = Flask(__name__)




def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_serial_data(sno):
    url = 'http://posiflex.dqserv.com/Api_ticket/get_serial'
    headers = {'X-TES_PRO_API_KEY': auth_token, 'serial_no': sno}
    r = requests.get(url, headers=headers).json()
    try:
        billing_name = r['serial_data']['billing_name']
    except:
        billing_name = ''

    return billing_name, r


def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'GBP'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}
    r = requests.get(url, headers=headers, params=params).json()
    if r.status_code == 200:
        write_json(r, '/var/www/pydev/response.json')
        price = r['data'][crypto]['quote']['GBP']['price']
    else:
        price = -1
        
    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    pattern = r'/[a-zA-Z]{2,4}'
    #pattern = r'/PCID[0-9]{4,6}' 
   # pattern = r'/[a-zA-z]{2,10}'    
    ticker_data = re.findall(pattern, txt)
    
    if ticker_data:
    #    symbol = ticker[0][1:].upper()
        ticker = ticker_data[0][1:].upper()
        chat_txt = txt.replace('/','')
    else:
        #symbol = ''
        pattern = r'/'
        ticker_data = re.findall(pattern, txt)
        #write_json(ticker_data, '/var/www/pydev/check_else_ticker_data.json')

        if ticker_data:
           ticker = 'NONTIK'
           chat_txt = txt.replace('/','')
          # write_json(ticker, '/var/www/pydev/check_else_ticker.json') 
        else:
            ticker  = ''
            chat_txt = txt
            #write_json(ticker, '/var/www/pydev/check_else_last_ticker.json')
   # return chat_id, symbol
    return chat_id, chat_txt, ticker   



def get_ticket_status(ticket_no):
    url = 'http://posiflex.dqserv.com/Api_ticket/get_ticket_status'
    headers = {'X-TES_PRO_API_KEY': auth_token, 'ticket_no': ticket_no}
    r = requests.get(url, headers=headers).json()

    try:
        ticket_stats = r['ticket_data']['name']
        

    except:
        ticket_stats = ''

    return ticket_stats



def send_message(chat_id, text='bla-bla-bla'):
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=payload)
    return r



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, chat_txt, ticker  = parse_message(msg)
        #write_json(ticker, '/var/www/pydev/parse_ticker.json')
        if not ticker:   
            send_message(chat_id, """ Iam a bot, having limited AI to process your data, 
                                    
            Please format your query as below \n
            To check ticket use /<ticket-number>, 
                Example : /PCID005515 
             To check serial information /<serialno>, 
                Example : /FT286413 
             Thanks for contact us""")
            return Response('ok', status=200)
        else:
            if 'PCID' in ticker:
                ticket_data = get_ticket_status(chat_txt)
                if not ticket_data:
                    send_message(chat_id, 'Wrong ticket number, Please enter correct ticket details')
                    return Response('ok', status=200)
                send_message(chat_id, ticket_data)
                return Response('ok', status=200)
            else:
                billing_name, serial_data = get_serial_data(chat_txt)
                #write_json(serial_data, '/var/www/pydev/parse_serial_data_fn.json') 
                if not billing_name:
                    send_message(chat_id, 'No Serial Found')
                    return Response('ok', status=200)
                invoice_no = serial_data['serial_data']['invoice_no']
                invoice_date = serial_data['serial_data']['invoice_date']
                model_no = serial_data['serial_data']['model_no']
                manufacturer = serial_data['serial_data']['manufacturer']
                warranty_status = serial_data['serial_data']['warranty_status'] 
                manufacturer = serial_data['serial_data']['manufacturer']                
                billing_address = serial_data['serial_data']['billing_address']
                send_message(chat_id, "Model No: " + model_no + "\nManufacturer:" + manufacturer + "\nInvoice no: " + invoice_no + "\nInvoice Date: " + invoice_date + "\nBilling Name: " + billing_name + " ")

               # send_message(chat_id, serial_data)
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

   # main():
