import functools
import logging
import traceback
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QLineEdit

from forms import error_dialog, strings
from forms.tunnel_ui import TunnelUI
from src.SSHTunnel import SSHTunnel, load_tunnels, save_tunnels

logger = logging.getLogger(__name__)


def log_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f"Error on {func.__name__}: {traceback.format_exc()}"
            )
            error_dialog.show_error(str(e))
    return wrapper


@dataclass
class TunnelItem:
    tunnel: SSHTunnel
    check_box: QtWidgets.QCheckBox


class MainUI(QtWidgets.QMainWindow):

    def __init__(self, form_path: Path):
        """Run the main user interface.

        Args:
            form_path (Path): Path to the QT ".ui" file.
        """
        super().__init__()
        uic.loadUi(form_path, self)
        self._tunnels_items: List[TunnelItem] = []
        self._init_widgets()
        self._bind()
        self.show()

    def _init_widgets(self):
        """Initialize the QT widgets.
        """
        self.tree_model = QtGui.QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels([
            strings.TOGGLE,
            strings.NAME,
            strings.LOCAL_IP,
            strings.LOCAL_PORT,
            strings.HOST_IP,
            strings.HOST_PORT,
            strings.SSH_IP,
            strings.SSH_PORT
        ])
        self.treeView.setModel(self.tree_model)
        self.treeView.header().resizeSection(0, 60)
        self.tree_root = self.tree_model.invisibleRootItem()

    def _bind(self):
        """Bind widgets to functions.
        """
        self.pushButton_add.clicked.connect(self._on_add_button_click)
        self.pushButton_edit.clicked.connect(self._on_edit_button_click)
        self.pushButton_duplicate.clicked.connect(self._on_duplicate_button_click)
        self.pushButton_delete.clicked.connect(self._on_delete_button_click)
        self.pushButton_start.clicked.connect(self._on_start_all_button_click)
        self.pushButton_stop.clicked.connect(self._on_stop_all_button_click)
        self.actionSave.triggered.connect(self._on_action_save)
        self.actionLoad.triggered.connect(self._on_action_load)
        self.actionExit.triggered.connect(self._on_action_exit)
        self.treeView.keyPressEvent = self._on_tree_key_press
        self.treeView.doubleClicked.connect(self._on_tree_double_clicked)

    @log_errors
    def _add_tree_item(self, tunnel: SSHTunnel) -> QtWidgets.QCheckBox:
        """Add a new row on the tunnels treeView.

        Args:
            tunnel (SSHTunnel): A SSHTunnel object.

        Returns:
            QtWidgets.QCheckBox: The associated toggle check box.
        """
        buttonItem = QtGui.QStandardItem("")
        name_item = QtGui.QStandardItem(tunnel.name)
        local_ip_item = QtGui.QStandardItem(tunnel.local_ip)
        local_port_item = QtGui.QStandardItem(str(tunnel.local_port))
        host_ip_item = QtGui.QStandardItem(tunnel.host_ip)
        host_port_item = QtGui.QStandardItem(str(tunnel.host_port))
        server_ip_item = QtGui.QStandardItem(tunnel.server_ip)
        server_port_item = QtGui.QStandardItem(str(tunnel.server_port))

        name_item.setEditable(False)
        local_ip_item.setEditable(False)
        local_port_item.setEditable(False)
        host_ip_item.setEditable(False)
        host_port_item.setEditable(False)
        server_ip_item.setEditable(False)
        server_port_item.setEditable(False)

        self.tree_root.appendRow([
            buttonItem,
            name_item,
            local_ip_item,
            local_port_item,
            host_ip_item,
            host_port_item,
            server_ip_item,
            server_port_item
        ])
        button = QtWidgets.QCheckBox()
        button.clicked.connect(partial(self._toggle_tunnel, tunnel, button))
        self.treeView.setIndexWidget(buttonItem.index(), button)
        return button
    
    @log_errors
    def _toggle_tunnel(
        self,
        tunnel: SSHTunnel,
        checkBox: QtWidgets.QCheckBox,
        value: bool
    ):
        """Toggle a tunnel.

        Args:
            tunnel (SSHTunnel): The tunnel to toggle.
            checkBox (QtWidgets.QCheckBox): The checkBox associated to the
                tunnel.
            value (bool): The new value of the checkBox
        """
        try:
            if value:
                if not tunnel.is_active():
                    tunnel.start()
            else:
                if tunnel.is_active():
                    tunnel.stop()
        except Exception as e:
            error_dialog.show_error(f"{tunnel.name}: {e}")
        checkBox.setChecked(tunnel.is_active())

    @log_errors
    def _edit_tree_item(self, indexes: list, tunnel: SSHTunnel):
        """Edit a tunnel tree item.

        Args:
            indexes (list): Tree column indexes to edit.
            tunnel (SSHTunnel): The SSHTunnel object that will be used to
                update the tree item.
        """
        values = [
            tunnel.name,
            tunnel.local_ip,
            str(tunnel.local_port),
            tunnel.host_ip,
            str(tunnel.host_port),
            tunnel.server_ip,
            str(tunnel.server_port)
        ]
        for i, v in zip(indexes[1:], values):
            self.tree_model.itemFromIndex(i).setText(v)

    @log_errors
    def _ui_edit_tunnel_row(self, indexes: List[QtCore.QModelIndex]):
        """Show a dialog to edit a tunnel row.

        Args:
            indexes (List[QtCore.QModelIndex]): The indexes of the row to edit.
        """
        row = self.tree_model.itemFromIndex(indexes[0]).row()
        tunnel = self._tunnels_items[row].tunnel
        check_box = self._tunnels_items[row].check_box
        ui = TunnelUI(tunnel)
        if ui.exec():
            tunnel.stop()
            ui.update_tunnel()
            self._edit_tree_item(indexes, tunnel)
            check_box.setChecked(tunnel.is_active())
    
    @log_errors
    def _ui_duplicate_tunnel_row(self, indexes: List[QtCore.QModelIndex]):
        """Duplicate a tunnel row and show a dialog to edit it.

        Args:
            indexes (List[QtCore.QModelIndex]): The indexes of the row to
                duplicate.
        """
        row = self.tree_model.itemFromIndex(indexes[0]).row()
        tunnel = self._tunnels_items[row].tunnel
        ui = TunnelUI(tunnel)
        if ui.exec():
            tunnel = ui.get_tunnel()
            check_box = self._add_tree_item(tunnel)
            self._tunnels_items.append(TunnelItem(tunnel, check_box))

    @log_errors
    def _delete_tunnel_row(self, indexes: List[QtCore.QModelIndex]):
        """Delete a tunnel row.

        Args:
            indexes (List[QtCore.QModelIndex]): The indexes of the row to
                delete.
        """
        index = self.tree_model.itemFromIndex(indexes[0]).row()
        self.tree_model.takeRow(index)
        self._tunnels_items[index].tunnel.stop()
        del (self._tunnels_items[index])

    @pyqtSlot()
    @log_errors
    def _on_tree_double_clicked(self):
        indexes = self.treeView.selectedIndexes()
        if indexes:
            self._ui_edit_tunnel_row(indexes)

    @log_errors
    def _on_tree_key_press(self, event):
        if event.key() == Qt.Key_Delete:
            indexes = self.treeView.selectedIndexes()
            if indexes:
                self._delete_tunnel_row(indexes)

    @log_errors
    def _add_tunnel(self, tunnel: SSHTunnel):
        check_box = self._add_tree_item(tunnel)
        self._tunnels_items.append(TunnelItem(tunnel, check_box))
        
    @pyqtSlot()
    @log_errors
    def _on_add_button_click(self):
        ui = TunnelUI()
        if ui.exec():
            tunnel = ui.get_tunnel()
            self._add_tunnel(tunnel)

    @pyqtSlot()
    @log_errors
    def _on_edit_button_click(self):
        indexes = self.treeView.selectedIndexes()
        if indexes:
            self._ui_edit_tunnel_row(indexes)

    @pyqtSlot()
    @log_errors
    def _on_duplicate_button_click(self):
        indexes = self.treeView.selectedIndexes()
        if indexes:
            self._ui_duplicate_tunnel_row(indexes)

    @pyqtSlot()
    @log_errors
    def _on_delete_button_click(self):
        indexes = self.treeView.selectedIndexes()
        if indexes:
            self._delete_tunnel_row(indexes)

    @pyqtSlot()
    @log_errors
    def _on_start_all_button_click(self):
        for tunnel_item in self._tunnels_items:
            try:
                tunnel_item.tunnel.start()
            except Exception as e:
                error_dialog.show_error(f"{tunnel_item.tunnel.name}: {e}")
            tunnel_item.check_box.setChecked(tunnel_item.tunnel.is_active())

    @pyqtSlot()
    @log_errors
    def _on_stop_all_button_click(self):
        for tunnel_item in self._tunnels_items:
            try:
                tunnel_item.tunnel.stop()
            except Exception as e:
                error_dialog.show_error(f"{tunnel_item.tunnel.name}: {e}")
            tunnel_item.check_box.setChecked(tunnel_item.tunnel.is_active())

    @pyqtSlot()
    @log_errors
    def _on_action_save(self):
        password = self._show_password_dialog()
        if password is None:
            return
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save session",
            "",
            "Encrypted JSON (*.json.enc);;All Files (*)",
            options=options
        )
        if file_name:
            save_tunnels(
                [i.tunnel for i in self._tunnels_items],
                Path(file_name),
                password
            )

    @pyqtSlot()
    @log_errors
    def _on_action_load(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open session",
            "",
            "Encrypted JSON (*.json.enc);;JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_name:
            password = self._show_password_dialog()
            if password is None:
                return

            # Stop current tunnels
            for tunnel_item in self._tunnels_items:
                try:
                    tunnel_item.tunnel.stop()
                except:
                    pass
            
            # Delete tunnels
            self.tree_model.removeRows(0, self.tree_model.rowCount())
            self._tunnels_items = []
            self.treeView.clearSelection()

            # Load tunnels
            tunnels = load_tunnels(Path(file_name), password)
            for t in tunnels:
                self._add_tunnel(t)

    @pyqtSlot()
    @log_errors
    def _on_action_exit(self):
        self._on_stop_all_button_click()
        QtCore.QCoreApplication.quit()

    @log_errors
    def _show_password_dialog(self):
        password, ok = QInputDialog.getText(
            self,
            "Enter password",
            "Password:",
            echo=QLineEdit.Password
        )
        if ok:
            return password
        return None
