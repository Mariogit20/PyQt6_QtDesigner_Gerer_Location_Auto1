from .database import bdd
db,cur = bdd("bdd.db")

def AffichageGlobal(Table,colonne,ordre):
    query = f'SELECT* FROM {Table} ORDER BY {colonne} {ordre}'
    result = cur.execute(query)
    data = result.fetchall()
    return data

def AffichageParDetail(Table,colonne,valeur):
    query = f'SELECT* FROM {Table} WHERE  {colonne} = ?'
    result = cur.execute(query,(valeur,))
    data = result.fetchone()
    return data
