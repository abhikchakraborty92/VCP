import hashlib
import datetime

def getworkbooksheet(workbook,tickercodes,rowlimit,columns):
    allsheets = workbook.fetch_sheet_metadata().get('sheets')
    
    # Checking and adding sheet if the workbook has no sheets
    if len(allsheets) == 0:
        workbook.add_worksheet('TickerData')
    
    # Checking worksheets to see where the data can be inserted
    for sheetobj in allsheets:
        sheet = workbook.get_worksheet(sheetobj.get('properties').get('index'))
        try:
            if len(sheet.col_values(1))+len(tickercodes)<=rowlimit:
                print(f'Inserting data into the sheet: `{sheet.title}`... ')
                return sheet
            else:
                 print(f'`{sheet.title}` sheet over limit. Ignoring... ')

        except:
            return sheet
    
    # If all the sheets are over limit, generating new worksheet
    print('Generating new worksheet...')
    sheet = workbook.add_worksheet('TickerData_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S'),len(tickercodes)+1,len(columns))
    return sheet

# Generate unique key for each row
def generatekey(tickercode):
    codestring = (tickercode+str(datetime.datetime.now())).encode()
    return hashlib.md5(codestring).hexdigest()[:-10]

# Parse ticker response to data for the  tickers into rows
def tickerparse(output,tickercode,currname,refreshtimestamp):
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