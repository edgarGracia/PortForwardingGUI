from PyQt5 import QtCore, QtWidgets

from forms import strings
from src.SSHTunnel import SSHTunnel


class TunnelUI(QtWidgets.QDialog):

    def __init__(self, tunnel: SSHTunnel = None):
        """Show a form to set the parameters of an SSH tunnel.

        Args:
            tunnel (SSHTunnel, optional): Optional tunnel to edit.
                Defaults to None.
        """
        super().__init__()

        self._orig_tunnel = tunnel

        # Remove the question mark
        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
        )

        # Set the window title
        if tunnel is None:
            self.setWindowTitle(strings.NEW_TUNNEL)
        else:
            self.setWindowTitle(f"{strings.EDIT_TUNNEL} {tunnel.name}")

        # Create the QT layout
        self.layout = QtWidgets.QFormLayout()

        # Name
        label = QtWidgets.QLabel(strings.NAME)
        self.name_line_edit = QtWidgets.QLineEdit()
        self.layout.addRow(label, self.name_line_edit)
        if tunnel is not None:
            self.name_line_edit.setText(tunnel.name)

        # Local IP
        label = QtWidgets.QLabel(strings.LOCAL_IP)
        self.local_ip_line_edit = QtWidgets.QLineEdit()
        if tunnel is not None:
            self.local_ip_line_edit.setText(tunnel.local_ip)
        else:
            self.local_ip_line_edit.setText("127.0.0.1")
        self.layout.addRow(label, self.local_ip_line_edit)

        # Local port
        label = QtWidgets.QLabel(strings.LOCAL_PORT)
        self.local_port_spin = QtWidgets.QSpinBox()
        self.local_port_spin.setMinimum(1)
        self.local_port_spin.setMaximum(65_535)
        self.local_port_spin.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        if tunnel is not None:
            self.local_port_spin.setValue(tunnel.local_port)
        else:
            self.local_port_spin.setValue(1025)
        self.layout.addRow(label, self.local_port_spin)

        # Host IP
        label = QtWidgets.QLabel(strings.HOST_IP)
        self.dest_ip_line_edit = QtWidgets.QLineEdit()
        if tunnel is not None:
            self.dest_ip_line_edit.setText(tunnel.host_ip)
        else:
            self.dest_ip_line_edit.setText("127.0.0.1")
        self.layout.addRow(label, self.dest_ip_line_edit)

        # Host port
        label = QtWidgets.QLabel(strings.HOST_PORT)
        self.dest_port_spin = QtWidgets.QSpinBox()
        self.dest_port_spin.setMinimum(1)
        self.dest_port_spin.setMaximum(65_535)
        if tunnel is not None:
            self.dest_port_spin.setValue(tunnel.host_port)
        else:
            self.dest_port_spin.setValue(1025)
        self.dest_port_spin.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.layout.addRow(label, self.dest_port_spin)

        # Server IP
        label = QtWidgets.QLabel(strings.SSH_IP)
        self.server_ip_line_edit = QtWidgets.QLineEdit()
        if tunnel is not None:
            self.server_ip_line_edit.setText(tunnel.server_ip)
        else:
            self.server_ip_line_edit.setText("")
        self.layout.addRow(label, self.server_ip_line_edit)

        # Server port
        label = QtWidgets.QLabel(strings.SSH_PORT)
        self.server_port_spin = QtWidgets.QSpinBox()
        self.server_port_spin.setMinimum(1)
        self.server_port_spin.setMaximum(65_535)
        if tunnel is not None:
            self.server_port_spin.setValue(tunnel.server_port)
        else:
            self.server_port_spin.setValue(22)
        self.server_port_spin.setButtonSymbols(
            QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.layout.addRow(label, self.server_port_spin)

        # User
        label = QtWidgets.QLabel(strings.USER)
        self.user_line_edit = QtWidgets.QLineEdit()
        if tunnel is not None:
            self.user_line_edit.setText(tunnel.user)
        else:
            self.user_line_edit.setText("")
        self.layout.addRow(label, self.user_line_edit)

        # Password
        label = QtWidgets.QLabel(strings.PASSWORD)
        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password)
        if tunnel is not None:
            self.password_line_edit.setText(tunnel.password)
        else:
            self.password_line_edit.setText("")
        self.layout.addRow(label, self.password_line_edit)

        # Ok/Cancel buttons
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def get_tunnel(self) -> SSHTunnel:
        """Return a SSHTunnel object with the form data.
        """
        return SSHTunnel(
            name=self.name_line_edit.text(),
            local_ip=self.local_ip_line_edit.text(),
            local_port=self.local_port_spin.value(),
            host_ip=self.dest_ip_line_edit.text(),
            host_port=self.dest_port_spin.value(),
            server_ip=self.server_ip_line_edit.text(),
            server_port=self.server_port_spin.value(),
            user=self.user_line_edit.text(),
            password=self.password_line_edit.text()
        )

    def update_tunnel(self):
        """Updates the original SSHTunnel object with the form data.
        """
        self._orig_tunnel.name = self.name_line_edit.text()
        self._orig_tunnel.local_ip = self.local_ip_line_edit.text()
        self._orig_tunnel.local_port = self.local_port_spin.value()
        self._orig_tunnel.host_ip = self.dest_ip_line_edit.text()
        self._orig_tunnel.host_port = self.dest_port_spin.value()
        self._orig_tunnel.server_ip = self.server_ip_line_edit.text()
        self._orig_tunnel.server_port = self.server_port_spin.value()
        self._orig_tunnel.user = self.user_line_edit.text()
        self._orig_tunnel.password = self.password_line_edit.text()
