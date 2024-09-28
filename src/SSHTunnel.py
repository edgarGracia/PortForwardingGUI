import json
import logging
from pathlib import Path
from typing import List

from sshtunnel import SSHTunnelForwarder

from .encryption import decrypt, encrypt

logger = logging.getLogger(__name__)


class SSHTunnel:

    def __init__(
        self,
        local_port: int,
        host_ip: str,
        host_port: int,
        user: str,
        password: str,
        name: str = "",
        local_ip: str = "127.0.0.1",
        server_ip: str = None,
        server_port: int = 22
    ):
        """Create an SSH tunnel.

        Args:
            local_port (int): The local port number to listen on for incoming
                connections.
            host_ip (str): The IP address of the remote host to connect to.
            host_port (int): The port number on the remote host to connect to.
            user (str): The username for SSH authentication on the remote server.
            password (str): The password for SSH authentication on the remote server.
            name (str, optional): An optional name for the tunnel instance.
                Defaults to "".
            local_ip (str, optional): The local IP address to bind the tunnel to.
                Defaults to "127.0.0.1".
            server_ip (str, optional): The IP address of the SSH server.
                If None, uses the host_ip. Defaults to None.
            server_port (int, optional): The port number of the SSH server.
                Defaults to 22.
        """
        self.name = name
        self.local_ip = local_ip
        self.local_port = local_port
        self.host_ip = host_ip
        self.host_port = host_port
        self.server_port = server_port
        self.user = user
        self.password = password
        self.server_ip = host_ip if not server_ip else server_ip
        self._tunnel: SSHTunnelForwarder = None

    def start(self):
        """Start the SSH tunnel.
        """
        # Create SSH tunnel
        if self._tunnel is None:
            logger.debug(f"Creating tunnel: {str(self)}")
            self._tunnel = SSHTunnelForwarder(
                ssh_address_or_host=(self.server_ip, self.server_port),
                remote_bind_address=(self.host_ip, self.host_port),
                local_bind_address=(self.local_ip, self.local_port),
                ssh_username=self.user,
                ssh_password=self.password,
            )
        
        # Start the tunnel
        if not self.is_active():
            logger.debug(f"Starting tunnel: {str(self)}")
            self._tunnel.start()
        
        logger.info(f"Tunnel started: {str(self)}")

    def stop(self):
        """Stop the SSH tunnel.
        """
        logger.debug(f"Stopping tunnel: {str(self)}")
        if self.is_active():
            self._tunnel.stop(force=True)
        self._tunnel = None
        logger.info(f"Tunnel stopped {str(self)}")

    def is_active(self) -> bool:
        if self._tunnel is None:
            return False
        return self._tunnel.is_active

    def __str__(self) -> str:
        return (
            f"{self.name}: {self.local_ip}:{self.local_port} -> "
            f"{self.host_ip}:{self.host_port} ~ "
            f"{self.user}@{self.server_ip}:{self.server_port} | "
            f"active: {self.is_active()}"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "local_ip": self.local_ip,
            "local_port": self.local_port,
            "host_ip": self.host_ip,
            "host_port": self.host_port,
            "server_port": self.server_port,
            "user": self.user,
            "password": self.password,
            "server_ip": self.server_ip
        }


def save_tunnels(
    tunnels: List[SSHTunnel],
    path: Path,
    password: str,
):
    """Save a list of tunnels to an encrypted JSON.

    Args:
        tunnels (List[SSHTunnel]): List of SSHTunnel objects.
        path (Path): Path to the output file.
        password (str): Password to encrypt the data.
    """
    logger.debug(f"Saving tunnels to {path}")
    data = [t.to_dict() for t in tunnels]
    json_str = json.dumps(data)
    json_enc = encrypt(json_str, password)
    path.write_text(json_enc)


def load_tunnels(
    path: Path,
    password: str,
) -> List[SSHTunnel]:
    """Load a list of tunnels from an encrypted JSON.

    Args:
        path (Path): Path to an encrypted JSON.
        password (str): Password to decrypt the data.

    Returns:
        List[SSHTunnel]: A list of SSHTunnel objects.
    """
    logger.debug(f"Loading tunnels from {path}")
    data = path.read_text()
    data = decrypt(data, password)
    data = json.loads(data)
    return [SSHTunnel(**d) for d in data]
