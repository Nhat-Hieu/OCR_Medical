from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap

# Constants (giống Dashboard)
PANEL_BG   = "#ffffff"
GAP_PANEL  = 26
LEFT_W     = 170
RIGHT_W    = 200
SIDE_MENU_ALIGN_WITH_DROP = 44


class ResultPage(QWidget):
    def __init__(self):
        super().__init__()

        root = QHBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.setSpacing(30)

        left_panel   = self._build_left_panel()
        mid_panel    = self._build_middle_panel()
        right_panel  = self._build_right_panel()

        root.addWidget(left_panel, 0)
        root.addWidget(mid_panel, 1)
        root.addWidget(right_panel, 0)

    # ---------------- Sidebar (giống Dashboard) ----------------
    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFixedWidth(LEFT_W)
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border:none; border-radius:12px;}}")

        l = QVBoxLayout(panel)
        l.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        l.setSpacing(8)

        # Logo
        brand = QLabel()
        logo = QPixmap("n6_ocrmedical/resources/logo_ocr.png").scaledToWidth(140, Qt.SmoothTransformation)
        brand.setPixmap(logo)
        brand.setAlignment(Qt.AlignHCenter)
        l.addWidget(brand)
        l.addSpacing(SIDE_MENU_ALIGN_WITH_DROP)

        group = QButtonGroup(self); group.setExclusive(True)
        def menu_btn(text, icon_path, checked=False):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setIcon(QIcon(icon_path))
            b.setIconSize(QSize(20, 20))
            b.setStyleSheet("""
                QPushButton{ background:transparent; border:1px solid transparent;
                    text-align:left; padding:6px 8px; border-radius:10px;
                    font-weight:600; color:#374151;}
                QPushButton:hover{ background:#f3f4f6; }
                QPushButton:checked{ background:#eef2ff; border:1px solid #c7d2fe;}
            """)
            if checked: b.setChecked(True)
            group.addButton(b)
            return b

        # Menu items
        self.btn_home    = menu_btn("Home",    "n6_ocrmedical/resources/home.png")
        self.btn_all     = menu_btn("All files","n6_ocrmedical/resources/folder.png")
        self.btn_setting = menu_btn("Setting", "n6_ocrmedical/resources/settings.png")
        self.btn_support = menu_btn("Support", "n6_ocrmedical/resources/customer-support.png")
        self.btn_review  = menu_btn("Review",  "n6_ocrmedical/resources/star.png")
        self.btn_result  = menu_btn("Result",  "n6_ocrmedical/resources/result.png", checked=True)

        l.addWidget(self.btn_home)
        l.addWidget(self.btn_all)
        l.addWidget(self.btn_setting)
        l.addWidget(self.btn_support)
        l.addWidget(self.btn_review)
        l.addWidget(self.btn_result)
        l.addStretch()

        # Avatar
        avatar = QLabel()
        av_pix = QPixmap("n6_ocrmedical/resources/user.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar.setPixmap(av_pix)
        avatar.setAlignment(Qt.AlignHCenter)

        username = QLabel("User/Administrator")
        username.setAlignment(Qt.AlignHCenter)
        username.setStyleSheet("color:#6b7280; font-size:14px;")

        l.addWidget(avatar)
        l.addWidget(username)
        return panel

    # ---------------- Middle (nội dung chính Result) ----------------
    def _build_middle_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(QPixmap("n6_ocrmedical/resources/result.png").scaled(28, 28, Qt.KeepAspectRatio))
        title = QLabel("Kết quả OCR")
        title.setStyleSheet("font-size:22px; font-weight:700; margin-left:6px;")
        header.addWidget(icon_lbl, 0, Qt.AlignLeft)
        header.addWidget(title, 0, Qt.AlignLeft)
        header.addStretch()
        layout.addLayout(header)

        # Result box
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background:#f9fafb;
                border:1px solid #e5e7eb;
                border-radius:8px;
                padding:8px;
                font-family:'Courier New';
                font-size:13px;
            }
        """)
        layout.addWidget(self.result_text, 1)

        # Hint text
        hint = QLabel("💡 Bạn có thể chọn và copy nội dung văn bản.")
        hint.setStyleSheet("color:#6b7280; font-size:12px;")
        layout.addWidget(hint)

        # Buttons row
        btn_row = QHBoxLayout()
        self.back_btn = QPushButton("⬅ Back")
        self.export_btn = QPushButton("💾 Xuất CSV/JSON")

        for b in (self.back_btn, self.export_btn):
            b.setStyleSheet("""
                QPushButton {
                    background:#fff;
                    border:1px solid #e5e7eb;
                    border-radius:8px;
                    padding:6px 14px;
                    font-weight:600;
                }
                QPushButton:hover { background:#f3f4f6; }
            """)

        btn_row.addWidget(self.back_btn, 0, Qt.AlignLeft)
        btn_row.addStretch()
        btn_row.addWidget(self.export_btn, 0, Qt.AlignRight)
        layout.addLayout(btn_row)

        self.export_btn.clicked.connect(self.export_result)
        return panel

    # ---------------- Right panel ----------------
    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFixedWidth(RIGHT_W)
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")

        l = QVBoxLayout(panel)
        l.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        l.setSpacing(12)

        lbl = QLabel("Result Tools / Options")
        lbl.setStyleSheet("color:#374151; font-weight:600;")
        l.addWidget(lbl)

        # Placeholder buttons
        btn_pdf = QPushButton("📄 Xuất PDF")
        btn_copy = QPushButton("📋 Copy Text")
        for b in (btn_pdf, btn_copy):
            b.setStyleSheet("""
                QPushButton {
                    background:#fff;
                    border:1px solid #e5e7eb;
                    border-radius:8px;
                    padding:6px 10px;
                    font-weight:600;
                }
                QPushButton:hover { background:#f3f4f6; }
            """)
            l.addWidget(b)

        l.addStretch()
        return panel

    # ---------------- Chức năng ----------------
    def set_result(self, text: str):
        self.result_text.setPlainText(text)

    def export_result(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu kết quả OCR", "",
            "Text Files (*.txt);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.result_text.toPlainText())
