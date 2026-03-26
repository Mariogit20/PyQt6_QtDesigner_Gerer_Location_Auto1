# -*- coding: utf-8 -*-
import re
import socket
import dns.resolver

def verifier_email_complet(email):
    """Vérifie le format (Niveau 1) et l'existence du nom de domaine (Niveau 3)"""
    
    # 1. Vérification du format (Niveau 1)
    regex_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex_email, email):
        return False, "Format d'email incorrect (ex: jean.dupont@gmail.com)."

    # 2. Vérification DNS (Niveau 3)
    domaine = email.split('@')[1]
    
    try:
        # Test de connexion Internet rapide
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        
        # Interrogation des serveurs mondiaux
        dns.resolver.resolve(domaine, 'MX')
        return True, "Email valide."
        
    except dns.resolver.NXDOMAIN:
        return False, f"Le domaine '{domaine}' n'existe pas sur Internet (Faute de frappe ?)."
    except dns.resolver.NoAnswer:
        return False, f"Le domaine '{domaine}' existe, mais ne possède aucun serveur de messagerie."
    except (dns.resolver.Timeout, OSError):
        # Mode hors-ligne : On laisse passer pour ne pas bloquer l'agence
        return True, "Mode hors-ligne : Vérification DNS suspendue."
    except Exception as e:
        return True, f"Vérification ignorée : {e}"