from .database import bdd

# Connexion à la base de données
db, cur = bdd('bdd.db')

def suppression(table, colonne, valeur):

    global db, cur

    query = f"DELETE FROM {table} WHERE {colonne} = ?"
    cur.execute(query, (valeur,))
    db.commit()
