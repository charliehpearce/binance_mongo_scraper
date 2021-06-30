# Scrapy myscrapeface
from types import DynamicClassAttribute
from requests import status_codes
import pymongo
import websocket
import json
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
        self.bids = {}
        self.asks = {}
        self.get_depth_ss() #initialize OB 
        print(self.return_order_book())

    def get_depth_ss(self):
        url = f'https://api.binance.com/api/v3/depth?symbol={self.currency_pair}&limit={self.depth}'
        response = requests.get(url)
        print(f'response from server: {response.status_code}')

        book_dict = ast.literal_eval(response.content.decode('UTF-8'))
        for bid in book_dict['bids']:
            self.bids[bid[0]] = bid[1]
        for ask in book_dict['asks']:
            self.asks[ask[0]] = ask[1]
    
    def update_asks(self, updates):
        #update order book
        for upd in updates:
            if float(upd[1]) == 0:
                # check to see if the quantity is 0, remove if True
                self.asks.pop(upd[0])
            else:
                self.asks[upd[0]] = upd[1]

    def update_bids(self, updates):
        #update order book
        for upd in updates:
            if float(upd[1]) == 0:
                # check to see if the quantity is 0, remove if True
                self.bids.pop(upd[0])
            else:
                self.bids[upd[0]] = upd[1]
            
    def return_order_book(self):
        return {'bids':self.bids, 'asks':self.asks}

# Open socket to binance
class BinanceSocket:
    def __init__(self, currency_pair:str, LOB_depth:int) -> None:
        self.currency_pair = currency_pair
        self.LOB_depth = LOB_depth
        self.ob = OrderBook(currency_pair=currency_pair, depth=LOB_depth)
        self.endpoint = self.generate_endpoint() # order book cache
        self.consume()

    def generate_endpoint(self):
        return(f'wss://stream.binance.com:9443/ws/{self.currency_pair.lower()}@depth@100ms')
 
    def open_socket(self, ws):
        #ws.send(json.dumps(self.endpoint)) ##????
        print('socket opened')

    def on_message(self, ws, message):
        #print(message)
        # deal with message (add to mongodb)
        dict_response = ast.literal_eval(message)
        
        if dict_response['b'] != []:
            self.ob.update_bids(dict_response['b'])
        if dict_response['a'] != []:
            self.ob.update_asks(dict_response['a'])
        print(self.ob.return_order_book())

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

def send_ob_to_mongo(mongo_client, ob):
    pass

if __name__ == "__main__":
    currency_pairs = ['btcusdt','XRPUSDT']
    bs = BinanceSocket(currency_pair='BTCUSDT', LOB_depth=1000)

"""
Notes:
Will probably need to implement a Queue system not to overload the db 
connection
Quantity should be expressed as a float rather than the current string system

To Do:
Implement MongoDB connection.
Spawn different threads for each websocket cxn.
"""