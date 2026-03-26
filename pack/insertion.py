from .database import bdd

db,cur = bdd('bdd.db')
#-------------user , {no,prenom,...},{RAkoto,lita,....}
def insertion(Table,colonnes,info):
    colonn_str = ','.join(colonnes)#nom,prenom,...
    info_str = ','.join(['?']*len(info))# ?,?,... 

    query = f'INSERT INTO {Table} ({colonn_str}) VALUES ({info_str})'
    cur.execute(query,info)
    db.commit()