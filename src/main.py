import datetime

from handlers.gmail_getter import GmailGetter
from handlers.gsheets_handler import ws
from processors.email_processor import EmailProcessor


def main():
    #transactions = GmailGetter().get_transactions()
    #all_txs = EmailProcessor().process_transactions(transactions)
    #ws.append_rows(all_txs.values.tolist(), value_input_option='USER_ENTERED')
    print(len(ws.get_all_records()))
    

if __name__ == "__main__":
    main()
