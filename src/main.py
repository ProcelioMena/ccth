import datetime

from handlers.gmail_getter import GmailGetter
from processors.email_processor import EmailProcessor


def main():
    transactions = GmailGetter().get_transactions()
    all_txs = EmailProcessor().process_transactions(transactions)


if __name__ == "__main__":
    main()
