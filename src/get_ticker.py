import pandas as pd
from requests import get
import json
import datetime
import hashlib
import time
from googleauthenticate import workbook

# Reading configuration
config = json.loads(open('config/config.json').read())

#Getting ticker URL
tickerurl = config.get('market').get('ticker').get('url')
tickercodes = config.get('tickercodes')

# Getting the google sheet object into which the data has to be inserted
rowlimit = config.get('googlesheetrowlimit')
columns = config.get('googlesheetcolumns')

def getworkbooksheet():
    allsheets = workbook.fetch_sheet_metadata().get('sheets')
    for sheetobj in allsheets:
        sheet = workbook.get_worksheet(sheetobj.get('properties').get('index'))
        try:
            if len(sheet.col_values(1))+len(tickercodes)<=rowlimit:
                return sheet
            else:
                 print(f'`{sheet.title}` sheet over limit. Ignoring...\n')

        except:
            return sheet
    
    print('Generating new worksheet...')
    sheet = workbook.add_worksheet('New_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S'),100,len(columns))
    return sheet


while True:
    # Getting ticker response
    refreshtimestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    tickerresponse = get(tickerurl)
    tickerdatadict = {}

    if tickerresponse.status_code == 200:
        tickeroutput = json.loads(tickerresponse.text)

        for ticker in tickercodes:
            tickerdatadict[ticker[0]]=tickeroutput.get(ticker[0])

    # Ticker data parsing functions

    # Generate unique key for each row
    def generatekey(tickercode):
        codestring = (tickercode+str(datetime.datetime.now())).encode()
        return hashlib.md5(codestring).hexdigest()[:-10]

    # Parse ticker response to data for the  tickers into rows
    def tickerparse(output,tickercode,currname):
        try:
            parse = {
                "insertid":str(generatekey(tickercode)),
                "crypt_curr_name":currname.upper(),
                "tickercode" : tickercode.upper(),
                "base_unit" : output.get('base_unit'),
                "quote_unit" : output.get('quote_unit'),
                "low_price_24_hr" : float(output.get('low')),
                "high_price_24_hr" : float(output.get('high')),
                "last_trade_price" : float(output.get('last')),
                "mkt_open_price" :float(output.get('open')),
                "trade_volume_24_hr" : float(output.get('volume')),
                "top_sell_price" : float(output.get('sell')),
                "top_buy_price" : float(output.get('buy')),
                "name" : output.get('name'),
                "ticker_timestamp" : datetime.datetime.fromtimestamp(output.get('at')).strftime('%Y-%m-%d %H:%M'),
                "refresh_timestamp" : refreshtimestamp,
                "timezone": str(datetime.datetime.now().astimezone().tzinfo)
            }

            # Inserting into google sheet
            valuelist = list(parse.values())
            return valuelist
        
        except EnvironmentError as e:
            return e

        

    # Generating dataset for the tickers
    ValuesToInsert = []
    for ticker in tickercodes:
        ValuesToInsert.append(tickerparse(tickerdatadict.get(ticker[0]),ticker[0],ticker[1]))

    sheet = getworkbooksheet()

    try:
        if sheet.cell(1,1).value == columns[0]:
            pass
        else:
            sheet.insert_row(columns,1)
    except Exception as e:
        print(e)

    sheet.append_rows(ValuesToInsert)

    time.sleep(30)
