from .database import bdd

db,cur = bdd('bdd.db')

def modification(table,colonnes,info,cols,id):
    global db,cur

    jointure = ','.join([f"{col} = ?"for col in colonnes])
    query = f"UPDATE {table} SET {jointure} WHERE {cols} = ?"

    deta = tuple(info) + (id,)
    cur.execute(query,deta)
    db.commit()