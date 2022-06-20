from os import environ as env
from dotenv import load_dotenv
load_dotenv()
from datetime import date, datetime
import requests
from urllib.parse import quote

# APIs
def coingecko_symbol_history(symbol: str, start_date: datetime = datetime(2020,12,31), end_date: datetime = datetime.now()) -> str:
    """Coin history, in USD. 
    Symbol example: 'bitcoin' or 'ethereum'
    Default timestamps: Start (December 31, 2020), End (now)
    """
    s = quote(symbol)
    start = int(start_date.timestamp()*1000)
    end = int(end_date.timestamp()*1000)
    return f'https://api.coingecko.com/api/v3/coins/{s}/market_chart/range?vs_currency=usd&from={start}&to={end}'

def deribit_symbol_history(symbol: str, start_date: datetime = datetime(2020,12,31), end_date: datetime = datetime.now()) -> str:
    """Symbol price history. 
    Symbol example: 'BTC-1JUL22-12000-C'
    Default timestamps: Start (December 31, 2020), End (now)
    """
    s = quote(symbol)
    start = int(start_date.timestamp()*1000)
    end = int(end_date.timestamp()*1000)
    return f'https://www.deribit.com/api/v2/public/get_mark_price_history?start_timestamp={start}&end_timestamp={end}&instrument_name={s}'

def deribit_vol_index(symbol: str, resolution: str = '3600', start_date: datetime = datetime(2020,12,31), end_date: datetime = datetime.now()) -> str:
    """Volatility history.
    Symbol example: 'BTC'
    Resolution: int (seconds) or 1D
    Default timestamps: Start (December 31, 2020), End (now)
    """
    r = quote(str(resolution))
    s = quote(symbol)
    start = int(start_date.timestamp()*1000)
    end = int(end_date.timestamp()*1000)
    return f'https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={s}&start_timestamp={start}&end_timestamp={end}&resolution={r}'

def deribit_ticker(symbol: str) -> str:
    s = quote(symbol)
    # get_ticker
    return f''

def deribit_all_instruments(currency: str, kind: str = 'option', expired: bool = False) -> str:
    c = quote(currency)
    # get_instruments
    return f''




# Coin Gecko API. origin: 1643932800000
def correct_crypto_time(x):
    # TODO: what timestamp do we need?
    return int(datetime.timestamp(datetime.fromtimestamp(x[0]/1000).replace(hour=0)))

# Formatting raw input
def format_coingecko(jraw):
    data = jraw['prices']
    timestamps = [*map(correct_crypto_time, data)]
    prices = [*map(lambda x: x[1], data)]
    z_data = [*zip(timestamps, prices)]
    z_data.reverse()
    return z_data

def main() -> None:
    # welcome

    return

# Main save asset: chooses what to do
# def save_asset(asset, asset_api_id):
#     try:
#         api_url = get_api_coingecko(asset_api_id)
#         raw = requests.get(api_url) # this is the REST call
#         data = format_coingecko(raw.json())
        
#         # TODO: save data
#         print(asset, '-- Price -- Query successful')
#     except:
#         print(asset, '-- Price -- Query fail')
#         print(raw.json())