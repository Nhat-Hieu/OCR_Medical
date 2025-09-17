from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog,
    QTextEdit, QFrame, QButtonGroup, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
import os


PANEL_BG   = "#ffffff"
GAP_PANEL  = 26
SIDE_MENU_ALIGN_WITH_DROP = 44


class UploadRow(QWidget):
    def __init__(self, idx: int, filename: str, size_text: str, status: str = "Ready"):
        super().__init__()
        self.setStyleSheet("QLabel{background:transparent;}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(8)

        idx_lbl = QLabel(f"{idx:02d}")
        idx_lbl.setFixedWidth(26)
        idx_lbl.setAlignment(Qt.AlignCenter)
        idx_lbl.setStyleSheet("font-weight:700; color:#111827;")

        name_lbl = QLabel(filename)
        name_lbl.setStyleSheet("font-weight:600; color:#1f2937;")
        name_lbl.setToolTip(filename)

        status_lbl = QLabel(status)
        status_lbl.setStyleSheet("color:#2e7d32; font-weight:600;")
        status_lbl.setFixedWidth(84)

        size_lbl = QLabel(size_text)
        size_lbl.setStyleSheet("color:#6b7280;")
        size_lbl.setFixedWidth(70)

        lay.addWidget(idx_lbl)
        lay.addWidget(name_lbl, 2)
        lay.addWidget(status_lbl, 0)
        lay.addWidget(size_lbl, 0, Qt.AlignRight)


class ResultPage(QWidget):
    def __init__(self):
        super().__init__()

        root = QGridLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setHorizontalSpacing(24)
        root.setVerticalSpacing(24)

        # Grid 12x12
        for c in range(12):
            root.setColumnStretch(c, 1)
        for r in range(12):
            root.setRowStretch(r, 1)

        # Sidebar (3 cột)
        left_panel = self._build_left_panel()
        root.addWidget(left_panel, 0, 0, 12, 2)

        # Main (9 cột)
        mid_panel = self._build_middle_panel()
        root.addWidget(mid_panel, 0, 2, 12, 10)

    # ---------------- Sidebar ----------------
    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border:none; border-radius:12px;}}")

        l = QVBoxLayout(panel)
        l.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        l.setSpacing(8)

        # Logo
        brand = QLabel()
        logo = QPixmap("n6_ocrmedical/resources/logo/logo_ocr.png").scaledToWidth(140, Qt.SmoothTransformation)
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

        self.btn_home    = menu_btn("Home",    "n6_ocrmedical/resources/logo/home.png")
        self.btn_all     = menu_btn("All files","n6_ocrmedical/resources/logo/folder.png")
        self.btn_setting = menu_btn("Setting", "n6_ocrmedical/resources/logo/settings.png")
        self.btn_support = menu_btn("Support", "n6_ocrmedical/resources/logo/customer-support.png")
        self.btn_review  = menu_btn("Review",  "n6_ocrmedical/resources/logo/star.png")
        self.btn_result  = menu_btn("Result",  "n6_ocrmedical/resources/logo/scan.png", checked=True)

        for b in (self.btn_home, self.btn_all, self.btn_setting,
                  self.btn_support, self.btn_review, self.btn_result):
            l.addWidget(b)
        l.addStretch()

        # Avatar
        avatar = QLabel()
        av_pix = QPixmap("n6_ocrmedical/resources/logo/user.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar.setPixmap(av_pix)
        avatar.setAlignment(Qt.AlignHCenter)

        username = QLabel("User/Administrator")
        username.setAlignment(Qt.AlignHCenter)
        username.setStyleSheet("color:#6b7280; font-size:14px;")

        l.addWidget(avatar)
        l.addWidget(username)

        return panel

    # ---------------- Main ----------------
    def _build_middle_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.setFixedHeight(28)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background:#fff;
                border:1px solid #e5e7eb;
                border-radius:6px;
                padding:4px 10px;
                font-weight:600;
            }
            QPushButton:hover { background:#f3f4f6; }
        """)
        header.addWidget(self.back_btn, 0, Qt.AlignLeft)
        header.addStretch()
        layout.addLayout(header)

        # Main row
        main_row = QHBoxLayout()
        main_row.setSpacing(20)

        # Left side
        left = QVBoxLayout()

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(400, 350)
        self.preview.setStyleSheet("border:1px solid #e5e7eb; border-radius:8px; background:#f9fafb;")
        left.addWidget(self.preview)

        self.file_info_container = QVBoxLayout()
        left.addLayout(self.file_info_container)

        main_row.addLayout(left, 1)

        # Right side: OCR result
        right = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background:#f9fafb;
                border:1px solid #e5e7eb;
                border-radius:8px;
                padding:8px;
                font-size:13px;
            }
        """)
        right.addWidget(self.result_text)
        main_row.addLayout(right, 2)

        layout.addLayout(main_row, 1)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.download_btn = QPushButton("Save")
        self.download_btn.clicked.connect(self.on_download_clicked)
        for b in (self.download_btn,):
            b.setFixedHeight(32)
            b.setStyleSheet("""
                QPushButton {
                    background:#f3f4f6;
                    border:1px solid #d1d5db;
                    border-radius:6px;
                    padding:6px 20px;
                    font-weight:600;
                }
                QPushButton:hover { background:#e5e7eb; }
            """)
            btn_row.addWidget(b)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return panel

    # ---------------- Chức năng ----------------
    def set_result(self, text: str):
        self.result_text.setPlainText(text)

    def set_image_info(self, image_path: str):
        """Hiển thị ảnh input + file info giống Home."""
        if not os.path.exists(image_path):
            return

        # Preview ảnh
        pix = QPixmap(image_path).scaled(
            self.preview.width(), self.preview.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview.setPixmap(pix)

        # Thông tin file
        name = os.path.basename(image_path)
        size = f"{round(os.path.getsize(image_path)/1024,1)} KB"

        # Clear cũ
        while self.file_info_container.count():
            child = self.file_info_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Thêm UploadRow (giống Home)
        row = UploadRow(1, name, size, "Ready")
        self.file_info_container.addWidget(row)
    def on_download_clicked(self):
        text = self.result_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "No Content", "Không có nội dung để lưu.")
            return

        # Hộp thoại chọn nơi lưu
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save OCR Result",
            "ocr_result.txt",
            "Text Files (.txt);;All Files (.*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "Saved", f"Đã lưu kết quả vào:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Lỗi khi lưu file:\n{e}")

