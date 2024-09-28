from PyQt5 import QtWidgets


def show_error(message: str, title: str = ""):
    """Show an error dialog.

    Args:
        message (str): Message to show.
        title (str, optional): Title of the dialog. Defaults to "".
    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(title)
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.exec_()
