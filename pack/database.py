import sqlite3

def bdd(dbname):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    return conn,cursor