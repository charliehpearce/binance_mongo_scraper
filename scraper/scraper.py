# Scrapy myscrapeface
import websocket
import json
import ast
import datetime
from pymongo import MongoClient
import threading

class MongoDBClient:
    def __init__(self, host, port, db_name, db_collection) -> None:
        self.client = MongoClient(host=host, port=port)
        self.db_name = db_name
        self.db_collection = db_collection
    
    def post_item(self, item:dict):
        db = self.client[self.db_name]
        colxn = db[self.db_collection]
        id = colxn.insert_one(item).inserted_id
        print(id)

# Open socket to binance
class BinanceSocket:
    def __init__(self, currency_pair:str, LOB_depth:int) -> None:
        self.currency_pair = currency_pair
        self.LOB_depth = LOB_depth
        self.endpoint = self.generate_endpoint() 
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
        print('response recieved')
        
        """
        if dict_response['b'] != []:
            self.ob.update_bids(dict_response['b'])
        if dict_response['a'] != []:
            self.ob.update_asks(dict_response['a'])        
        """
        payload = {'timestamp':datetime.datetime.utcnow(),\
            'bids':dict_response['b'],'asks':dict_response['a']}
        
        print(payload['timestamp'])
        #mdb_client.post_item(payload)

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
    currency_pairs = ['btcusdt',]
    
    mdb_client = MongoDBClient(host="host.docker.internal", port=27017, db_name='binance10'\
            , db_collection='BTCUSDT')
    
    bs = BinanceSocket(currency_pair='BTCUSDT', LOB_depth=1000)

"""
Notes:
Will probably need to implement a Queue system not to overload the db 
connection
Quantity should be expressed as a float rather than the current string system

To Do:
Think about how to handle order book caching
- periodically get order book snapshot
- updates between snapshots
- collect data per day and dump at end of period
"""