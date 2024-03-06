import re
from bs4 import BeautifulSoup
from io import StringIO
from pandas import DataFrame, concat, read_html


class EmailProcessor:

    def process_colpatria(self, transactions: list) -> DataFrame:
        """
        Process the transactions from colpatria to extract the transaction details.
        :param transactions: The transactions to be processed.
        :return: A DataFrame with the transaction details.
        """
        txs = []
        for transaction in transactions:
            dfs = read_html(StringIO(transaction))
            tx = dfs[-1]
            tx = tx.iloc[1, :]
            if len(tx) == 4: 
                txs.append(tx.to_list())
        df = DataFrame(txs, columns=['comercio', 'monto', 'fecha', 'hora'])
        df[['year', 'month', 'day']] = df['fecha'].str.split('/', expand=True).astype(int)
        df[['hour', 'minute', 'second']] = df['hora'].str.split(':', expand=True).astype(int)
        df = df.drop(columns=['fecha', 'hora', 'second'])
        df['card'] = 4489
        df['bank'] = 'colpatria'
        df['type'] = 'buy'
        df = df.rename(columns={'comercio': 'to', 'monto': 'amount'})
        return df
    
    def process_bancolombia(self, transactions: list) -> DataFrame:
        """
        Process the transactions from bancolombia to extract the transaction details.
        :param transactions: The transactions to be processed.
        :return: A DataFrame with the transaction details.
        """
        txs = []
        i = 0
        for transaction in transactions:

            soup = BeautifulSoup(transaction, 'html.parser')
            soup = soup.prettify().splitlines()
            tx = [line for line in soup if '$' in line][0]
            print(tx)
            amount = re.search('([0-9,.]+)', tx).group(1)
            am1, am2 = amount.split(',')[0].replace('.', ''), amount.split('.')[0].replace(',', '')
            hour = re.search('([0-9]{2}):([0-9]{2})', tx).group(0)
            date = re.search('([0-9]{2})/([0-9]{2})/([0-9]{4})', tx).group(0)
            card = re.search('\*([0-9]+)', tx).group(0)[1:]

            if 'compra' in tx.lower():
                to = re.search('?<=en\s)(.*?)(?= 0\d:\d{2})', tx).group(0)
                print(to)
                pass
            elif 'Transferencia' in tx:
                pass
            elif 'Avance' in tx:
                to = re.search('?<=en\s)(.*?)(?= 0\d:\d{2})', tx).group(0)
                print(to)
                pass
            elif 'Recibiras' in tx:
                pass
            else:
                print('Transaction not supported')

            i += 1

        df = DataFrame(txs, columns=['to', 'amount', 'date', 'hour', 'card', 'type'])
        df[['day', 'month', 'year']] = df['date'].str.split('/', expand=True).astype(int)
        df[['hour', 'minute']] = df['hour'].str.split(':', expand=True).astype(int)
        df['bank'] = 'bancolombia'
        df = df.drop(columns=['date'])
        raise Exception(df)

        return df

    def process_transactions(self, transactions: dict) -> DataFrame:
        """
        Process the transactions to extract all the transaction details.
        :param transactions: The transactions to be processed.
        :return: A DataFrame with the transaction details.
        """
        all_txs = []
        for bank, bank_snippets in transactions.items():
            if bank == 'colpatria':
                all_txs.append(self.process_colpatria(bank_snippets))
            elif bank == 'bancolombia':
                all_txs.append(self.process_bancolombia(bank_snippets))
            else:
                print(f'Bank {bank} not supported')
        return concat(all_txs)

