import pandas as pd
from requests import get
import json
import datetime
import pytz
import sqlalchemy
import time

# Reading configuration
config = json.loads(open('config/config.json').read())

#Getting ticker URL
tickerurl = config.get('market').get('ticker').get('url')
tickercodes = config.get('tickercodes')

while 1:
    # Getting ticker response
    refreshtimestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    tickerresponse = get(tickerurl)
    tickerdatadict = {}

    if tickerresponse.status_code == 200:
        tickeroutput = json.loads(tickerresponse.text)

        for ticker in tickercodes:
            tickerdatadict[ticker]=tickeroutput.get(ticker)


    # Creating database connection and output dataset
    cryptodb = sqlalchemy.create_engine('sqlite:///output/cryptoinfo.db')

    # Ticker data parsing functions
    def tickerparse(output,tickercode):
        try:
            parse = {
                "tickercode" : [tickercode],
                "base_unit" : [output.get('base_unit')],
                "quote_unit" : [output.get('quote_unit')],
                "low_price_24_hr" :[ output.get('low')],
                "high_price_24_hr" : [output.get('high')],
                "last_trade_price" : [output.get('last')],
                "mkt_open_price" : [output.get('open')],
                "trade_volume_24_hr" : [output.get('volume')],
                "top_sell_price" : [output.get('sell')],
                "top_buy_price" : [output.get('buy')],
                "name" : [output.get('name')],
                "ticker_timestamp" : [datetime.datetime.fromtimestamp(output.get('at')).strftime('%Y-%m-%d %H:%M')],
                "refresh_timestamp" : [refreshtimestamp],
                "timezone": str(datetime.datetime.now().astimezone().tzinfo)
            }
            ticker_dataset = pd.DataFrame(parse)
            #print(datetime.datetime.fromtimestamp(output.get('at')))
            ticker_dataset.to_sql('tickerinfo',cryptodb,if_exists='append',index=False)
            return f"Ticker inserted for {tickercode} at {refreshtimestamp}"
        
        except Exception as e:
            return e

        

    # Generating dataset for the tickers
    for key,value in tickerdatadict.items():
        print(tickerparse(value,key))
    
    time.sleep(60)

