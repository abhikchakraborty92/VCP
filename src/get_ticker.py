import pandas as pd
from requests import get
import json
import datetime
import time


# Importing the packages in a try block because some local environments need the src. format and the others work with default
try:
    from src.helperfunctions import *
    from src.googleauthenticate import googleworkbook   # writing like this to enable __init__ file
except:
    from helperfunctions import *
    from googleauthenticate import googleworkbook

# Reading configuration from the config folder. Replace the file location whenever there is new file/folder
config = json.loads(open('config/config.json').read())

# Getting ticker URL from the configuration file. The ticker URL has been provided by www.wazirx.com 
tickerurl = config.get('market').get('ticker').get('url')
tickercodes = config.get('tickercodes')

# Getting google worksheet to write the data
workbook = googleworkbook()

# Getting ticker response
refreshtimestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') # Getting refresh timestamp to insert the data along with it
tickerresponse = get(tickerurl)         # Getting raw response
tickerdatadict = {}  # Ticker dictionary to store the API response for further processing



# Checking if the response received from the API is a success with status code 200 and proceeding with the next steps
if tickerresponse.status_code == 200:
    tickeroutput = json.loads(tickerresponse.text)

    # Getting tickers from the tickercodes list of the config file and fetching relevant data out of the API response for our ticker
    for ticker in tickercodes:
        tickerdatadict[ticker[0]]=tickeroutput.get(ticker[0])

    # Generating dataset for the tickers
    ValuesToInsert = []   # List that will hold all our ticker data values. Each ticker will have a list of its values  which would be appended into this
    
    
    for ticker in tickercodes:
        ValuesToInsert.append(tickerparse(tickerdatadict.get(ticker[0]),ticker[0],ticker[1],refreshtimestamp)) # Parsing and generating the ticker value list and appending it into the master list

    # Getting the google sheet object into which the data has to be inserted
    rowlimit = config.get('googlesheetrowlimit')  # Getting the row limit to ensure limited data is loaded into a sheet and it doesn't overflow the sheet limit
    columns = config.get('googlesheetcolumns')   # Getting the list of column headers to add if the sheet doesn't have a column header. This will happen when a new sheet is generated to insert the data

    sheet = getworkbooksheet(workbook,tickercodes,rowlimit,columns) # Getting the sheet where data has to be inserted

    # Checking if the first row, first cell is equal to the value of our first column. If not, we insert the header column
    try:
        if sheet.cell(1,1).value == columns[0]:
            pass
        else:
            sheet.insert_row(columns,1)
    except Exception as e:
        print(e)

    # Inserting all the values of the ticker into the sheet
    sheet.append_rows(ValuesToInsert)

    print(f'Data inserted on {refreshtimestamp}')
