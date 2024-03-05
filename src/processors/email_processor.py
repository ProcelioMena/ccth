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

            tx_data = tx.split('$')[1].split('. ')[:-1]
            first_split, last_ = tx_data[0].split(' '), tx_data[-1]
            amount = first_split[0].split(',')[0].replace('.', '')
            if 'compra' in tx.lower():
                card, date = last_.split('*')[-1], last_.split(' ')[0]
                hour = first_split[-1]
                place = ' '.join(first_split[2:-1])
                txs.append([place, amount, date, hour, card, 'buy'])
            elif 'Transferencia' in tx:
                amount = first_split[0].split('.')[0].replace(',', '')
                datetime_ = last_.split(' ')
                date, hour = datetime_[0], datetime_[1]
                to = int(first_split[-1])
                card = tx_data[0].split('*')[-1].split(' ')[0]
                txs.append([to, amount, date, hour, card, 'transfer'])
            elif 'Avance' in tx:
                tx_data = tx_data[0].split(' ')
                amount = tx_data[0].split(',')[0].replace('.', '')
                card = tx_data[-1].split('*')[-1]
                to = tx_data[2]
                date, hour = tx_data[-3], tx_data[-4]
                txs.append([to, amount, date, hour, card, 'cash'])
            elif 'Recibiras' in tx:
                print(tx)
                print(tx_data)
                amount = int(tx_data[0].split(' ')[0].replace('.', '').split(',')[0])
                card = tx_data[-1].split('*')[-1].split(' ')[0]
                datetime = tx_data[-1].split(' ')
                date, hour = datetime[0], datetime[1]
                from_ = tx_data[0].split(' ')
                print(from_, -amount, card, date, hour)
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

