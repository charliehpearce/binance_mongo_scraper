# Scrapy myscrapeface
from requests import status_codes
import pymongo
import websocket
import json
import os
import threading
import requests
import ast

# Orderbook to store info coming in from binance
class OrderBook:
    """
    Creates a locally cached order book for a pair
    """
    def __init__(self, currency_pair, depth) -> None:
        self.currency_pair = currency_pair
        self.depth = depth
        self.bids = []
        self.asks = []
        self.get_depth_ss() #initialize OB 
        

    def get_depth_ss(self):
        url = f'https://api.binance.com/api/v3/depth?symbol={self.currency_pair}&limit={self.depth}'
        response = requests.get(url)
        print(f'response from server: {response.status_code}')

        book_dict = ast.literal_eval(response.content.decode('UTF-8'))
        self.bids = [{i[0]:i[1]} for i in book_dict['bids']] # turn these into a dictionary for easy updating
        self.asks = [{i[0]:i[1]} for i in book_dict['asks']]
    
    def update_book(self, update):
        #update order book
        pass

    def return_order_book(self):
        return {'bids':self.bids, 'asks':self.asks}

# Open socket to binance
class BinanceSocket:
    def __init__(self, currency_pair:str, LOB_depth:int) -> None:
        self.currency_pair = currency_pair
        self.LOB_depth = LOB_depth
        self.endpoint = self.generate_endpoint()
        self.ob = OrderBook(currency_pair=currency_pair, depth=LOB_depth)
        self.consume()

    def generate_endpoint(self):
        return(f'wss://stream.binance.com:9443/ws/{self.currency_pair.lower()}@depth{self.LOB_depth}@100ms')
 
    def open_socket(self, ws):
        #ws.send(json.dumps(self.endpoint)) ##????
        print('socket opened')

    def on_message(self, ws, message):
        # deal with message (add to mongodb)
        print(message)

    @staticmethod
    def on_ping(ws, message):
        print(f'ping: {json.dumps(message)}')

    @staticmethod
    def on_pong(ws, message):
        print(f'pong {json.dumps(message)}')
    
    def consume(self):
        # open websocket
        print(self.endpoint)
        socket_app = websocket.WebSocketApp(self.endpoint, on_message=self.on_message, \
            on_ping=self.on_ping, on_pong= self.on_pong, on_open=self.open_socket)
        socket_app.run_forever()

# Open mongoDB client 
def create_mongoDB_client(host:str, port:int):
    return pymongo.MongoClient(host, port)

if __name__ == "__main__":
    currency_pairs = ['btcusdt','XRPUSDT']
    bs = BinanceSocket(currency_pair='BTCUSDT', LOB_depth=20)

    #add queue system to add to DB
"""
Notes:
Will probably need to implement a Queue system not to overload the db 
connection
"""