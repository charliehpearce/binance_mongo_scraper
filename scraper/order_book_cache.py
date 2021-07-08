# Orderbook caching
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