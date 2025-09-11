from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

class FileLogPage(QWidget):
    def __init__(self):
        super().__init__()

        root = QGridLayout(self)
        root.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        root.setHorizontalSpacing(GUTTER)
        root.setVerticalSpacing(GUTTER)

        # Panel trái (sidebar)
        left_panel = self._build_left_panel()
        # Panel giữa (File Log)
        mid_panel = self._build_mid_panel()
        # Panel phải (Greeting + History)
        right_panel = self._build_right_panel()

        root.addWidget(left_panel, 0, 0, 12, 2)
        root.addWidget(mid_panel, 0, 2, 12, 8)
        root.addWidget(right_panel, 0, 10, 12, 2)

    def _build_left_panel(self):
        panel = QFrame()
        l = QVBoxLayout(panel)
        l.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)

        logo = QLabel()
        logo.setPixmap(QPixmap("n6_ocrmedical/resources/logo/logo_ocr.png").scaledToWidth(140))
        logo.setAlignment(Qt.AlignHCenter)
        l.addWidget(logo)
        l.addSpacing(30)

        # Sidebar menu
        def menu_btn(text, icon_path, checked=False):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setIcon(QIcon(icon_path))
            b.setIconSize(QSize(20,20))
            b.setStyleSheet("QPushButton{padding:6px; text-align:left;}")
            if checked: b.setChecked(True)
            return b

        l.addWidget(menu_btn("Home", "icons/home.png"))
        l.addWidget(menu_btn("File Log", "icons/folder.png", checked=True))
        l.addWidget(menu_btn("Extract Info", "icons/scan.png"))
        l.addWidget(menu_btn("Setting", "icons/settings.png"))
        l.addWidget(menu_btn("Review", "icons/star.png"))
        l.addStretch()

        return panel

    def _build_mid_panel(self):
        panel = QFrame()
        v = QVBoxLayout(panel)
        v.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)

        # Header
        header = QHBoxLayout()
        title = QLabel("OCR - Medical"); title.setStyleSheet("font-size:22px; font-weight:900;")
        search = QLineEdit(); search.setPlaceholderText("Search files, patients IDs…")
        search.setFixedHeight(28)
        header.addWidget(title); header.addStretch(); header.addWidget(search)
        v.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        for text, icon in [("New","icons/add.png"),("Copy","icons/copy.png"),
                           ("Share","icons/share.png"),("Delete","icons/delete.png")]:
            b = QPushButton(); b.setIcon(QIcon(icon)); b.setToolTip(text)
            toolbar.addWidget(b)
        v.addLayout(toolbar)

        # File list (folders)
        file_list = QListWidget()
        for i in range(6):
            item = QListWidgetItem(QIcon("icons/folder.png"), "09/10/2025")
            file_list.addItem(item)
        v.addWidget(file_list)

        return panel

    def _build_right_panel(self):
        panel = QFrame()
        v = QVBoxLayout(panel)

        # Greeting
        greet = QLabel("Good morning, Doctor ☀️🌈")
        greet.setAlignment(Qt.AlignCenter)
        greet.setStyleSheet("font-size:18px; font-weight:700;")
        v.addWidget(greet)

        # History
        h_title = QLabel("History"); h_title.setStyleSheet("font-size:16px; font-weight:700;")
        v.addWidget(h_title)
        history = QListWidget()
        for i in range(5):
            item = QListWidgetItem(QIcon("icons/file.png"), "file_280...25.text   3.5Mb")
            history.addItem(item)
        v.addWidget(history)

        return panel
