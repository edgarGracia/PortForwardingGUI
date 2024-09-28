import argparse
import logging
import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets

from forms.main_ui import MainUI


def run(form_path: Path, dark_style: bool = False):
    os.environ["QT_API"] = "pyqt5"
    app = QtWidgets.QApplication(sys.argv)

    if dark_style:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))

    window = MainUI(form_path)
    app.exec_()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-d",
        "--dark-style",
        action="store_true"
    )
    ap.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )

    args = ap.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    run(
        form_path=Path(__file__).parent / "./forms/main.ui",
        dark_style=args.dark_style
    )
