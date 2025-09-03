import sys, os, mimetypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFrame, QListWidgetItem,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent


# ========================== UPLOAD ITEM (Center) ==========================
class UploadItem(QWidget):
    def __init__(self, filename, size="--", status="Converted"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(30)

        # Style cho toàn bộ item
        self.setStyleSheet("""
            UploadItem {
                background-color: #f5f5f5;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
            }
        """)
        self.setMinimumHeight(45)

        # Tên file
        self.name_lbl = QLabel(filename)
        self.name_lbl.setStyleSheet("font-size:14px; font-weight:500; color:#333;")
        self.name_lbl.setFixedWidth(250)   # cho cột tên file rộng cố định

        # Status
        self.status_lbl = QLabel(status)
        if "Converted" in status:
            self.status_lbl.setStyleSheet("font-size:13px; color:#28a745; font-weight:600;")
        elif "Converting" in status:
            self.status_lbl.setStyleSheet("font-size:13px; color:#ff9800; font-weight:600;")
        else:
            self.status_lbl.setStyleSheet("font-size:13px; color:gray; font-weight:600;")
        self.status_lbl.setFixedWidth(100)

        # File size
        self.size_lbl = QLabel(size)
        self.size_lbl.setStyleSheet("font-size:13px; color:#555;")
        self.size_lbl.setFixedWidth(80)

        # Download button
        self.download_btn = QPushButton("⬇")
        self.download_btn.setFixedSize(26, 26)
        self.download_btn.setStyleSheet("""
            QPushButton {
                border:none;
                background:transparent;
                font-size:14px;
            }
            QPushButton:hover {
                color:#4a90e2;
            }
        """)

        # Add vào layout
        layout.addWidget(self.name_lbl)
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.size_lbl)
        layout.addStretch()
        layout.addWidget(self.download_btn)



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
        wrapper.setContentsMargins(40, 20, 40, 20)
        wrapper.setSpacing(20)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # Sidebar
        sidebar_frame = QFrame()
        sidebar_frame.setStyleSheet("""
            QFrame { background-color: #f0f0f0; border-radius: 16px; }
            QListWidget { background: transparent; border:none; outline:0; font-size:14px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background:#d6e9ff; border-radius:6px; color:#004085; }
        """)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        self.menu = QListWidget()
        self.menu.addItem("🏠 Home")
        self.menu.addItem("📂 All files")
        self.menu.addItem("⚙ Settings")
        sidebar_layout.addWidget(self.menu)
        user_lbl = QLabel("👤 Dr. Hieu\nMedical Data Manager")
        user_lbl.setStyleSheet("font-size:12px; color:#555; margin:10px;")
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(user_lbl)

        # Center
        center_frame = QFrame()
        center_frame.setStyleSheet("QFrame { background:#fff; border-radius:16px; padding:10px; }")
        center_layout = QVBoxLayout(center_frame)
        title = QLabel("📝 OCR - Convert Medical Records")
        title.setStyleSheet("font-size:18px; font-weight:bold; margin:10px;")
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
        center_layout.addWidget(title)
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
        history_label = QLabel("History")
        history_label.setStyleSheet("font-weight:bold; margin:5px;")
        self.history_list = QListWidget()
        right_layout.addWidget(converter_card)
        right_layout.addWidget(history_label)
        right_layout.addWidget(self.history_list, 1)

        # Panel balance
        sidebar_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        center_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        main_layout.addWidget(sidebar_frame, 1)
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
            widget = UploadItem(os.path.basename(f), size, "Converted")
            item.setSizeHint(widget.sizeHint())
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, widget)

            # Right (History)
            h_item = QListWidgetItem(self.history_list)
            h_widget = FileItem(os.path.basename(f), size, self.history_list)
            h_item.setSizeHint(h_widget.sizeHint())
            self.history_list.addItem(h_item)
            self.history_list.setItemWidget(h_item, h_widget)

        self.total_label.setText(f"Total: {self.file_list.count()} files")


# ========================== MAIN WINDOW ==========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediOCR - Scan & Store Medical Records")
        self.resize(1200, 700)
        self.setCentralWidget(Dashboard())
        self.setStyleSheet("QWidget { background:#e0e0e0; font-family:'Segoe UI'; }")


# ========================== RUN ==========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
