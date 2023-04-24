from flask import Flask, render_template, request
import yfinance as yf
import schedule
import os
import time
from flask_mail import Mail , Message
from cred import *
import threading
from twilio.rest import Client

def send_sms(to_):
    client = Client(twilio_data['account_sid'], twilio_data['auth_token'])
    message = client.messages.create(
        body = f"The stock price exceeds than threshold you provided. The new value of {ticker} is {stockdata['currentPrice']}",
        from_= twilio_data['twilio_phone'],
        to = to_
    )
    print("Message Sent to phone")


app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_data['email']
app.config['MAIL_PASSWORD'] = mail_data['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

def send_email(recepient):
    with app.app_context():
        sender = mail_data['email']
        receiver = [recepient]

        msg = Message('Stock Notifier', sender = sender, recipients = receiver)
        msg.body = f"The stock price exceeds than threshold you provided. The new value of {ticker} is {stockdata['currentPrice']}"
        mail.send(msg)
        print("Email sent")



# def check_stock_price(ticker_symbol, threshold, notification_type):
#     stock_data = yf.Ticker(ticker_symbol).info
#     current_price = stock_data['current_price']
#     if current_price >= threshold:
#         if notification_type == 'Email':
#             pass
#         if notification_type == 'Phone':
#             pass



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notification', methods = ['POST','GET'])
def form():
    if request.method == 'POST':
        global email
        email= request.form['email']
        global phone
        phone = request.form['number']
        global ticker
        ticker = request.form['ticker']
        global freq
        freq = request.form['frequency']
        freq =  int(freq)
        global threshold
        threshold = float(request.form['threshold'])
        global notification_method
        notification_method = request.form['notification']
        global stockdata 
        stockdata = yf.Ticker(ticker).info
        try:
            thread = threading.Thread(target= background_thread)
            thread.start()
            return "Successful"
        except:
            print("An exception occur")
       


def logic():
    if stockdata['currentPrice'] > threshold:
        print("Stock Price increases")
        if notification_method == 'Email':
            send_email(email)
        elif notification_method == 'Phone':
            send_sms(phone)
        else:
            print("Error")
    else:
        print("Stock price doesn't increase")

def background_thread():
    while True:
        # print(stockdata.keys())
        logic()
        time.sleep(int(freq))

if __name__ == "__main__":
    app.run(debug=True)