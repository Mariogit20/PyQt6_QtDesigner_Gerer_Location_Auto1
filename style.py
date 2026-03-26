# -*- coding: utf-8 -*-

STYLE_GLOBAL = """
/* --- STYLE DE BASE --- */
QWidget {
    background-color: #f4f6f9;
    color: #2c3e50;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* --- STYLE DES BOUTONS GÉNÉRIQUES --- */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1f618d;
}

/* --- FORMULAIRES ET SAISIE --- */
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 5px;
    color: #34495e;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #3498db;
}

/* --- TABLEAUX ET LISTES --- */
QTreeWidget, QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f9fbfd;
    border: 1px solid #bdc3c7;
    border-radius: 5px;
}
QHeaderView::section {
    background-color: #34495e;
    color: white;
    font-weight: bold;
    padding: 5px;
}

/* --- ONGLETS (STYLE ULTRA-COMPACT) --- */
QTabWidget::pane {
    border: 1px solid #bdc3c7;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #ecf0f1;
    padding: 6px 8px; /* Marge interne extrêmement réduite */
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 12px; /* Police un peu plus petite juste pour faire tenir tous les onglets */
}
QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
    font-weight: bold;
}

/* --- 🎯 FOCUS : BOUTON DE CONNEXION (Login.py) --- */
/* On utilise !important pour être certain de gagner contre tout autre style */

QPushButton#pushButton_connexion {
    background-color: #2ecc71 !important; 
    color: #000000 !important; /* Texte en NOIR pour une visibilité parfaite */
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    border: 2px solid #27ae60;
    min-height: 45px;
    min-width: 200px;
    padding: 0px; 
}

QPushButton#pushButton_connexion:hover {
    background-color: #27ae60 !important;
    color: #ffffff !important; /* Devient blanc au survol */
}

QPushButton#pushButton_connexion:pressed {
    background-color: #1e8449 !important;
}
"""