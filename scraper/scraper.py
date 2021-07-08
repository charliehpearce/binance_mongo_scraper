# Scrapy myscrapeface
import websocket
import json
import ast
import datetime
from pymongo import MongoClient
import threading
import requests

class MongoDBClient:
    def __init__(self, host, port, db_name) -> None:
        self.client = MongoClient(host=host, port=port)
        self.db_name = db_name
    
    def post_item(self, item:dict, collection:str):
        db = self.client[self.db_name]
        colxn = db[collection]
        id = colxn.insert_one(item).inserted_id
        print(id)

# Open socket to binance
class BinanceSocket:
    def __init__(self, currency_pair:str, LOB_depth:int) -> None:
        self.currency_pair = currency_pair
        self.LOB_depth = LOB_depth
        self.endpoint = self.generate_endpoint() 
        self.mdb_client = MongoDBClient(host="host.docker.internal", port=27017, db_name='binance')
        self.get_ob_ss()
        
        self.consume()

    def get_ob_ss(self):
        url = f'https://api.binance.com/api/v3/depth?symbol={self.currency_pair}&limit={self.LOB_depth}'
        response = requests.get(url)
        print(f'response from server: {response.status_code}')
        book_dict = ast.literal_eval(response.content.decode('UTF-8'))
        self.mdb_client.post_item(book_dict, f'{self.currency_pair}_fullbooks')

    def generate_endpoint(self):
        return(f'wss://stream.binance.com:9443/ws/{self.currency_pair.lower()}@depth@100ms')
 
    def open_socket(self, ws):
        print('socket opened')

    def on_message(self, ws, message):
        dict_response = ast.literal_eval(message)

        payload = {'timestamp':datetime.datetime.utcnow(),\
            'bids':dict_response['b'],'asks':dict_response['a']}
        
        print(payload['timestamp'])
        self.mdb_client.post_item(payload, 'BTCUSDT')

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


if __name__ == "__main__":
    currency_pairs = ['btcusdt','','']    
    bs = BinanceSocket(currency_pair='BTCUSDT', LOB_depth=1000)

"""
Notes:
Will probably need to implement a Queue system not to overload the db 
connection
Quantity should be expressed as a float rather than the current string system

To Do:
Think about how to handle order book caching
- periodically get order book snapshot
- crontab backup files to GCS (per day? then reset db?)
"""