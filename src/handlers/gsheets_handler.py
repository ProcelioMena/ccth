import gspread

client_gs = gspread.service_account(filename='ccth.json')
sh = client_gs.open('Expenses')
ws = sh.worksheet('tracker')

