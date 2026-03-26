from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from pack.affichage import AffichageGlobal
from pack.message import *
from pack.insertion import *
from pack.modification import *


class Ui_UserForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(767, 531)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")

        # Titre
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setStyleSheet("font: 18pt \"Times New Roman\"; color:rgb(85, 85, 127);")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        # Formulaire
        self.formLayout = QtWidgets.QFormLayout()
        self.label_2 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.input_nom = QtWidgets.QLineEdit(parent=Form)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.input_nom)

        self.label_3 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_3)
        self.input_prenom = QtWidgets.QLineEdit(parent=Form)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.input_prenom)

        self.label_6 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_6)
        self.input_age = QtWidgets.QLineEdit(parent=Form)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.input_age)

        self.label_7 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_7)
        self.select_sexe = QtWidgets.QComboBox(parent=Form)
        self.select_sexe.addItem('Masculin')
        self.select_sexe.addItem('Féminin')
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.select_sexe)

        self.label_4 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_4)
        self.input_email = QtWidgets.QLineEdit(parent=Form)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.input_email)

        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_5)
        self.input_telephone = QtWidgets.QLineEdit(parent=Form)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.input_telephone)

        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)

        # Boutons
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.btn_ajouter = QtWidgets.QPushButton(parent=Form)
        self.horizontalLayout.addWidget(self.btn_ajouter)
        self.btn_modifier = QtWidgets.QPushButton(parent=Form)
        self.horizontalLayout.addWidget(self.btn_modifier)
        self.btn_annuler = QtWidgets.QPushButton(parent=Form)
        self.horizontalLayout.addWidget(self.btn_annuler)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        # Barre de recherche
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.input_search = QtWidgets.QLineEdit(parent=Form)
        self.input_search.setPlaceholderText("Rechercher par Nom, Prénom ou Email...")
        self.horizontalLayout_3.addWidget(self.input_search)
        self.btn_search = QtWidgets.QPushButton(parent=Form)
        self.horizontalLayout_3.addWidget(self.btn_search)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)

        # Table
        self.table = QtWidgets.QTableView(parent=Form)
        header = ["id", "Nom", "Prenom", "Age", "Sexe", 'Email', "Télephone"]
        self.model = QStandardItemModel()
        self.model.setColumnCount(len(header))
        self.model.setHorizontalHeaderLabels(header)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setModel(self.model)
        self.gridLayout.addWidget(self.table, 4, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # Connexion des boutons
        self.btn_ajouter.clicked.connect(self.ui_insert)
        self.btn_search.clicked.connect(self.ui_search)

        # Charger les données initiales
        self.load_data()

    # Réinitialiser les champs
    def clear_input(self):
        self.input_nom.clear()
        self.input_prenom.clear()
        self.input_age.clear()
        self.input_email.clear()
        self.input_telephone.clear()

    # Charger les données dans le tableau
    def load_data(self):
        users = AffichageGlobal("user", "id", "DESC")
        self.model.setRowCount(len(users))
        for row, user in enumerate(users):
            for col, val in enumerate(user):
                self.model.setItem(row, col, QStandardItem(str(val)))

    # Insertion utilisateur
    def ui_insert(self):
        nom = self.input_nom.text()
        prenom = self.input_prenom.text()
        age = self.input_age.text()
        sexe = self.select_sexe.currentText()
        email = self.input_email.text()
        telephone = self.input_telephone.text()

        if nom == "" or prenom == "":
            error_message('Le champs Nom ou Prénom ne doivent pas être vides')
            return

        if age != "" and telephone != "":
            try:
                int(age)
                table = 'user'
                colonne = ['nom', 'prenom', 'age', 'sexe', 'email', 'telephone']
                info = [nom, prenom, age, sexe, email, telephone]
                insertion(table, colonne, info)
                info_message('Utilisateur enregistré avec succès')
                self.clear_input()
                self.load_data()
            except:
                error_message('L’âge doit être un nombre')
        else:
            error_message('Tous les champs sont obligatoires')

    # ✅ Fonction de recherche
    def ui_search(self):
        search_text = self.input_search.text().strip()
        if search_text == "":
            self.load_data()
            return

        users = AffichageGlobal("user", "id", "DESC")
        filtered_users = [u for u in users if
                          search_text.lower() in str(u[1]).lower() or
                          search_text.lower() in str(u[2]).lower() or
                          search_text.lower() in str(u[5]).lower()]

        self.model.setRowCount(len(filtered_users))
        for row, user in enumerate(filtered_users):
            for col, val in enumerate(user):
                self.model.setItem(row, col, QStandardItem(str(val)))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Gestion des Utilisateurs"))
        self.label.setText(_translate("Form", "Ajout d'un utilisateur"))
        self.label_2.setText(_translate("Form", "&Nom :"))
        self.label_3.setText(_translate("Form", "&Prénom :"))
        self.label_6.setText(_translate("Form", "&Age :"))
        self.label_7.setText(_translate("Form", "&Sexe :"))
        self.label_4.setText(_translate("Form", "&Email :"))
        self.label_5.setText(_translate("Form", "&Télephone :"))
        self.btn_ajouter.setText(_translate("Form", "Ajouter"))
        self.btn_modifier.setText(_translate("Form", "Modifier"))
        self.btn_annuler.setText(_translate("Form", "Annuler"))
        self.btn_search.setText(_translate("Form", "Recherche"))
