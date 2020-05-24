import sqlite3


class Connector:
    def __init__(self, database_url):
        conn = sqlite3.connect(database_url)
        self.cursor = conn.cursor()

    def execute(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def create_table(self, name, *args):
        conn.excute('INSERT {0}, ({1})'.format(name, *args))
