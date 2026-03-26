from PyQt6.QtWidgets import QMessageBox


def info_message(sms):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(sms)
    msg.setWindowTitle('info')
    msg.exec()


def error_message(sms):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(sms)
    msg.setWindowTitle('error')
    msg.exec()

def warning_message(sms):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText(sms)
    msg.setWindowTitle('Warning')
    msg.exec