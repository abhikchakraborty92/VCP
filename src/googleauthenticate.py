import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

config = json.loads(open('config/config.json').read())

# Google API scopes
scope = config.get('googlescope')

# Creating Google Client
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/google_credentials.json", scope)
    client = gspread.authorize(creds)
    print('Authenticated')

except:
    print('Authentication Failed')
# Getting the sheet where data has to be inserted

def googleworkbook():
    workbook = None
    try:
        workbook = client.open(config.get('googleworkbookname'))
        print("Workbook fetch successful")
    except Exception as e:
        print(e)

    return workbook

