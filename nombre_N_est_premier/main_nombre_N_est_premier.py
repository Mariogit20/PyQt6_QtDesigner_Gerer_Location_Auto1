import sys
import math
# from PyQt6.QtWidgets import QApplication, QMessageBox

def est_ce_que_le_nombre_N_saisi_est_premier(n):
    """
    Teste si un nombre est premier.
    :param n: L'entier à tester.
    :return: True si n est premier, False sinon.
    """
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def check_and_show_dialog(n):
    """
    Vérifie si n est un nombre premier et affiche une boîte de dialogue
    avec le message et l'icône appropriés en utilisant PyQt6.
    :param n: L'entier à tester et afficher.
    """
#    msg_box = QMessageBox()
#    msg_box.setWindowTitle("Résultat du test")

    if est_ce_que_le_nombre_N_saisi_est_premier(n):
#        msg_box.setIcon(QMessageBox.Icon.Information)
#        msg_box.setText(f"Bravo ! Le nombre {n} est un nombre premier !")
        print(f"Bravo ! Le nombre {n} est un nombre premier !")
    else:
#        msg_box.setIcon(QMessageBox.Icon.Warning)
#        msg_box.setText(f"Désolé ! Le nombre {n} n'est pas un nombre premier !")
        print(f"Désolé ! Le nombre {n} n'est pas un nombre premier !")

#    msg_box.exec()

# Initialisation de l'application PyQt6
# app = QApplication(sys.argv)

# Exemple d'utilisation pour un nombre premier (17)
check_and_show_dialog(17)

# Exemple d'utilisation pour un nombre non premier (18)
check_and_show_dialog(18)

# Exécution de la boucle d'événements de l'application (nécessaire pour afficher les boîtes de dialogue)
# sys.exit(app.exec())