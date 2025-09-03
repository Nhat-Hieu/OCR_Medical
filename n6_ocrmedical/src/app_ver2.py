import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFrame, QListWidgetItem,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QPixmap, QFontMetrics


# ========================== UPLOAD ITEM ==========================
class UploadItem(QWidget):
    def __init__(self, index, filename, size="--", status="Converted"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.setStyleSheet("""
            UploadItem {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QLabel { 
                background: transparent;
                padding-top: 2px;
                padding-bottom: 2px;
            }
        """)
        self.setMinimumHeight(55)

        # ====== Số thứ tự ======
        self.index_lbl = QLabel(str(index))
        self.index_lbl.setFixedWidth(30)
        self.index_lbl.setAlignment(Qt.AlignCenter)
        self.index_lbl.setStyleSheet("font-size:13px; font-weight:bold; color:#222;")

        # ====== Tên file ======
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(filename, Qt.ElideRight, 250)
        self.name_lbl = QLabel(elided)
        self.name_lbl.setStyleSheet("font-size:14px; font-weight:500; color:#333;")
        self.name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.name_lbl.setToolTip(filename)
        self.name_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # ====== Trạng thái ======
        self.status_lbl = QLabel(status)
        if "Converted" in status:
            self.status_lbl.setStyleSheet("font-size:13px; color:#28a745; font-weight:600;")
        elif "Converting" in status:
            self.status_lbl.setStyleSheet("font-size:13px; color:#ff9800; font-weight:600;")
        else:
            self.status_lbl.setStyleSheet("font-size:13px; color:gray; font-weight:600;")
        self.status_lbl.setFixedWidth(100)

        # ====== Kích thước ======
        self.size_lbl = QLabel(size)
        self.size_lbl.setStyleSheet("font-size:13px; color:#555;")
        self.size_lbl.setFixedWidth(80)

        # ====== Layout ======
        layout.addWidget(self.index_lbl)
        layout.addWidget(self.name_lbl, 2)
        layout.addWidget(self.status_lbl, 1)
        layout.addWidget(self.size_lbl, 0, Qt.AlignRight)


# ========================== HISTORY ITEM (Right) ==========================
class FileItem(QWidget):
    def __init__(self, filename, size="--", parent_list=None):
        super().__init__()
        self.parent_list = parent_list

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        text_layout = QVBoxLayout()
        self.name_lbl = QLabel(filename)
        self.name_lbl.setStyleSheet("font-weight:bold; color:#333;")
        self.size_lbl = QLabel(size)
        self.size_lbl.setStyleSheet("font-size:12px; color:gray;")
        text_layout.addWidget(self.name_lbl)
        text_layout.addWidget(self.size_lbl)

        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setStyleSheet("QPushButton { border:none; background:transparent; }")
        remove_btn.clicked.connect(self.delete_self)

        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(remove_btn)

    def delete_self(self):
        if self.parent_list:
            for i in range(self.parent_list.count()):
                if self.parent_list.itemWidget(self.parent_list.item(i)) == self:
                    self.parent_list.takeItem(i)
                    break


# ========================== DROP AREA ==========================
class DropArea(QLabel):
    def __init__(self, dashboard=None):
        super().__init__("")
        self.dashboard = dashboard
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #4a90e2;
                border-radius: 12px;
                font-size: 14px;
                color: #333;
                padding: 40px;
                background-color: #f0f7ff;
            }
        """)
        self.setText("☁️⬆️\nClick or drag your files here to convert")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "",
                "All Files (*);;Images (*.png *.jpg *.jpeg);;PDF Files (*.pdf);;Word Files (*.doc *.docx)"
            )
            if files and self.dashboard:
                self.dashboard.add_files(files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and self.dashboard:
            self.dashboard.add_files(files)


# ========================== DASHBOARD ==========================
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        wrapper = QHBoxLayout(self)
        wrapper.setContentsMargins(20, 20, 20, 20)
        wrapper.setSpacing(20)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # Sidebar (thu gọn)
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(80)
        sidebar_frame.setStyleSheet("""
            QFrame { background-color: #f0f0f0; border-radius: 16px; }
            QPushButton {
                border: none;
                background: transparent;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgba(74,144,226,0.15);
                border-radius: 12px;
            }
            QPushButton:checked {
                background: rgba(74,144,226,0.25);
                border-radius: 12px;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(20)

        # Icon menu
        btn_home = QPushButton()
        btn_home.setIcon(QIcon(r"C:\Users\ASUS\Downloads\home.png"))
        btn_home.setIconSize(QSize(25, 25))
        btn_home.setCheckable(True)
        btn_home.setChecked(True)

        btn_setting = QPushButton()
        btn_setting.setIcon(QIcon(r"C:\Users\ASUS\Downloads\setting.png"))
        btn_setting.setIconSize(QSize(25, 25))
        btn_setting.setCheckable(True)

        btn_folder = QPushButton()
        btn_folder.setIcon(QIcon(r"C:\Users\ASUS\Downloads\folder.png"))
        btn_folder.setIconSize(QSize(25, 25))
        btn_folder.setCheckable(True)

        sidebar_layout.addWidget(btn_home, alignment=Qt.AlignHCenter)
        sidebar_layout.addWidget(btn_setting, alignment=Qt.AlignHCenter)
        sidebar_layout.addWidget(btn_folder, alignment=Qt.AlignHCenter)
        sidebar_layout.addStretch()

        # Center
        center_frame = QFrame()
        center_frame.setStyleSheet("QFrame { background:#fff; border-radius:16px; padding:10px; }")
        center_layout = QVBoxLayout(center_frame)

# --- Title with logo ---
        title_layout = QHBoxLayout()
        logo_lbl = QLabel()
        logo_pix = QPixmap(r"C:\Users\ASUS\Downloads\logo.png")  # 👈 đường dẫn logo
        if not logo_pix.isNull():
            # Scale logo lớn hơn (ví dụ 48x48)
            logo_pix = logo_pix.scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(logo_pix)

        # KHÔNG setFixedSize để QLabel tự co theo ảnh
        logo_lbl.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel("OCR - Convert Medical Records")
        title_lbl.setStyleSheet("font-size:18px; font-weight:bold; margin-left:8px; color:#333;")

        title_layout.addWidget(logo_lbl, 0, Qt.AlignVCenter)
        title_layout.addWidget(title_lbl, 0, Qt.AlignVCenter)
        title_layout.addStretch()
        center_layout.addLayout(title_layout)



        self.drop_area = DropArea(dashboard=self)
        self.file_list = QListWidget()
        bottom_bar = QHBoxLayout()
        self.total_label = QLabel("Total: 0 files")
        self.download_all = QPushButton("⬇ Download All")
        self.download_all.setStyleSheet("""
            QPushButton { background:#4a90e2; color:white; border-radius:10px; padding:6px 12px; }
            QPushButton:hover { background:#357abd; }
        """)
        bottom_bar.addWidget(self.total_label)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.download_all)
        center_layout.addWidget(self.drop_area)
        center_layout.addWidget(self.file_list, 1)
        center_layout.addLayout(bottom_bar)

        # Right
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background:#f0f0f0; border-radius:16px; }")
        right_layout = QVBoxLayout(right_frame)

        converter_card = QFrame()
        converter_layout = QVBoxLayout(converter_card)
        lbl1 = QLabel("✨ AI Converter\nVectorize your images with AI\nExtract layers from PDF")
        lbl1.setWordWrap(True)
        try_btn = QPushButton("Try Now")
        converter_layout.addWidget(lbl1)
        converter_layout.addWidget(try_btn)
        converter_card.setStyleSheet("""
            QFrame { background:qlineargradient(x1:0, y1:0, x2:1, y2:1,
                     stop:0 #3f51b5, stop:1 #5a55ae);
                     border-radius:16px; color:white; padding:15px; }
            QPushButton { background:white; color:#3f3f66; border-radius:10px;
                          padding:6px 12px; font-weight:bold; }
        """)
        right_layout.addWidget(converter_card)

        history_label = QLabel("History")
        history_label.setStyleSheet("font-weight:bold; margin:5px;")
        self.history_list = QListWidget()
        right_layout.addWidget(history_label)
        right_layout.addWidget(self.history_list, 1)

        # User info dưới cùng
        user_name = QLabel("👤 Dr. Hieu")
        user_name.setAlignment(Qt.AlignCenter)
        user_name.setStyleSheet("font-size:13px; font-weight:bold; color:#333;")
        user_role = QLabel("Medical Data Manager")
        user_role.setAlignment(Qt.AlignCenter)
        user_role.setStyleSheet("font-size:12px; color:#555;")
        right_layout.addWidget(user_name)
        right_layout.addWidget(user_role)

        # Layout balance
        sidebar_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        center_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        main_layout.addWidget(sidebar_frame, 0)
        main_layout.addWidget(center_frame, 3)
        main_layout.addWidget(right_frame, 2)
        wrapper.addLayout(main_layout)

    def add_files(self, files):
        for f in files:
            try:
                size = f"{os.path.getsize(f)//1024} KB"
            except Exception:
                size = "--"

            # Center
            item = QListWidgetItem(self.file_list)
            filename = os.path.basename(f) if f else "Unnamed file"
            widget = UploadItem(self.file_list.count(), filename, size, "Converted")
            item.setSizeHint(widget.sizeHint())
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, widget)

            # Right history
            h_item = QListWidgetItem(self.history_list)
            h_widget = FileItem(filename, size, self.history_list)
            h_item.setSizeHint(h_widget.sizeHint())
            self.history_list.addItem(h_item)
            self.history_list.setItemWidget(h_item, h_widget)

        self.total_label.setText(f"Total: {self.file_list.count()} files")


# ========================== MAIN ==========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediOCR - Scan & Store Medical Records")
        self.resize(1200, 700)
        self.setCentralWidget(Dashboard())
        self.setStyleSheet("QWidget { background:#e0e0e0; font-family:'Segoe UI'; }")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
