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
        snippets, bodies = transactions[0], transactions[1]
        for body in bodies:
            dfs = read_html(StringIO(body))
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
        df = df.rename(columns={'comercio': 'place', 'monto': 'amount'})
        return df
    
    def process_bancolombia(self, transactions: list) -> DataFrame:
        """
        Process the transactions from bancolombia to extract the transaction details.
        :param transactions: The transactions to be processed.
        :return: A DataFrame with the transaction details.
        """
        snippets, bodies = transactions[0], transactions[1]
        print(snippets[0])
        soup = BeautifulSoup(bodies[0], 'html.parser')
        print(soup.prettify())
        element = soup.find(text='Bancolombia le informa Compra por $18.200,00 en DROGUERIA INGLESA 11 19:32. 03/03/2024 T.Cred *6295. Inquietudes al 6045109095/018000931987')
        if element:
            print(element)
            raise Exception(element)
        else:
            print('No element found')


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

