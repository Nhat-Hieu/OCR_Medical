# ============================================================
# OCR - Medical (PySide6)
# ============================================================

import sys, os
from datetime import datetime
from typing import List
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QFontMetrics, QPainter, QPen, QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QSizePolicy, QLineEdit, QButtonGroup, QStackedWidget
)
from PySide6.QtCore import QThread, Signal, QObject
# =========================
# 1) HẰNG SỐ & THIẾT KẾ
# =========================

APP_BG   = "#e5e7eb"
PANEL_BG = "#ffffff"

GAP_OUTER   = 30
GAP_PANEL   = 26
GAP_CARD    = 22
GAP_INSIDE  = 14
GAP_BELOW_DROP = 20

LEFT_W   = 170
RIGHT_W  = 200
FILE_LIST_HEIGHT = 200
SIDE_MENU_ALIGN_WITH_DROP = 44

GREETING_ICONS = {
    "morning":   "n6_ocrmedical/resources/sun.png",
    "afternoon": "n6_ocrmedical/resources/cloud.png",
    "evening":   "n6_ocrmedical/resources/moon.png",
    "night":     "n6_ocrmedical/resources/night.png",
}

# =========================
# 2) HÀM TIỆN ÍCH
# =========================

def human_size(path: str) -> str:
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return "1 KB"
        kb = size // 1024
        if kb < 1024:
            return f"{kb} KB"
        mb = size / (1024 * 1024)
        return f"{mb:.1f} MB" if mb < 10 else f"{int(mb)} MB"
    except Exception:
        return "--"

def elide(text: str, widget: QWidget, width: int) -> str:
    fm = QFontMetrics(widget.font())
    return fm.elidedText(text, Qt.ElideRight, width)

# =========================
# 3) WIDGET TÁI DÙNG
# =========================

class HistoryItem(QWidget):
    def __init__(self, filename: str, size_text: str = "--"):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 5, 8, 5)
        lay.setSpacing(6)

        icon = QLabel("📄"); icon.setFixedWidth(16)
        name = QLabel(filename); name.setStyleSheet("font-weight:600; color:#2d3748;")
        size = QLabel(size_text); size.setStyleSheet("color:#6b7280; font-size:11px;")
        caret = QLabel("▾")
        caret.setStyleSheet("color:#9aa3af; font-size:14px;")
        caret.setFixedWidth(16); caret.setAlignment(Qt.AlignCenter)

        col = QVBoxLayout(); col.setSpacing(0)
        col.addWidget(name); col.addWidget(size)

        lay.addWidget(icon)
        lay.addLayout(col)
        lay.addStretch()
        lay.addWidget(caret)

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
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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

class DropZone(QWidget):
    def __init__(self, on_files_added, icon_path="n6_ocrmedical/resources/arrow.png",
                 icon_size=64, gap=2):
        super().__init__()
        self.on_files_added = on_files_added
        self.setAcceptDrops(True)
        self.setMinimumHeight(170)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(
            "QWidget{background:#eaf2ff; border-radius:12px;} "
            "QLabel{color:#1f2937;}"
        )

        v = QVBoxLayout(self)
        v.setContentsMargins(18, 24, 18, 24)
        v.setSpacing(gap)

        self.icon = QLabel()
        pix = QPixmap(icon_path).scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon.setPixmap(pix)
        self.icon.setAlignment(Qt.AlignHCenter)

        self.text = QLabel("Click hoặc kéo-thả file vào đây để trích xuất thông tin")
        self.text.setAlignment(Qt.AlignHCenter)
        self.text.setStyleSheet("margin-top:-4px;")

        v.addWidget(self.icon)
        v.addWidget(self.text)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#397fd7")); pen.setStyle(Qt.DashLine); pen.setWidth(2)
        p.setPen(pen)
        r = self.rect().adjusted(4, 4, -4, -4)
        p.drawRoundedRect(r, 12, 12)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(self, "Chọn file", "", "Tất cả (*.*)")
            if files:
                self.on_files_added(files)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls()]
        if files:
            self.on_files_added(files)
class OCRWorker(QObject):
    finished = Signal(str)   # emit khi xong OCR (trả về text)

    def __init__(self, image_path, prompt):
        super().__init__()
        self.image_path = image_path
        self.prompt = prompt

    def run(self):
        from lmstudio_client import call_qwen_ocr
        try:
            result = call_qwen_ocr(self.image_path, self.prompt)
        except Exception as e:
            result = f"[ERROR] {e}"
        self.finished.emit(result)
# =========================
# 4) MÀN HÌNH CHÍNH
# =========================
from lmstudio_client import call_qwen_ocr
class Dashboard(QWidget):
    result_requested = Signal()
    def __init__(self):
        super().__init__()

        root = QHBoxLayout(self)
        root.setContentsMargins(GAP_OUTER, GAP_OUTER, GAP_OUTER, GAP_OUTER)
        root.setSpacing(GAP_OUTER)

        left_panel = self._build_left_panel()
        mid_container = self._build_middle_panel()
        right_container = self._build_right_panel()

        root.addWidget(left_panel, 0)
        root.addWidget(mid_container, 1)
        root.addWidget(right_container, 0)

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFixedWidth(LEFT_W)
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        panel.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border:none; border-radius:12px;}}")

        l = QVBoxLayout(panel)
        l.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        l.setSpacing(8)

        brand = QLabel()
        logo = QPixmap("n6_ocrmedical/resources/logo_ocr.png").scaledToWidth(140, Qt.SmoothTransformation)
        brand.setPixmap(logo); brand.setAlignment(Qt.AlignHCenter)
        l.addWidget(brand)
        l.addSpacing(SIDE_MENU_ALIGN_WITH_DROP)

        group = QButtonGroup(self); group.setExclusive(True)
        def menu_btn(text, icon_path, checked=False):
            b = QPushButton(text)
            b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            b.setIcon(QIcon(icon_path)); b.setIconSize(QSize(20, 20))
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

        # chỉ 1 nút Home
        self.btn_home = menu_btn("Home", "n6_ocrmedical/resources/home.png", checked=True)
        l.addWidget(self.btn_home)

        l.addWidget(menu_btn("All files","n6_ocrmedical/resources/folder.png"))
        l.addWidget(menu_btn("Setting", "n6_ocrmedical/resources/settings.png"))
        l.addWidget(menu_btn("Support", "n6_ocrmedical/resources/customer-support.png"))
        l.addWidget(menu_btn("Review",  "n6_ocrmedical/resources/star.png"))
        self.btn_result = menu_btn("Result", "n6_ocrmedical/resources/scan.png")
        l.addWidget(self.btn_result)

        l.addStretch()

        avatar = QLabel()
        av_pix = QPixmap("n6_ocrmedical/resources/user.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar.setPixmap(av_pix); avatar.setAlignment(Qt.AlignHCenter)
        username = QLabel("User/Administrator"); username.setAlignment(Qt.AlignHCenter)
        username.setStyleSheet("color:#6b7280; font-size:14px;")
        l.addWidget(avatar); l.addWidget(username)
        return panel

    def _build_middle_panel(self) -> QWidget:
        mid_layout = QVBoxLayout()
        mid_layout.setSpacing(GAP_CARD)

        top_card = QFrame()
        top_card.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")
        m = QVBoxLayout(top_card)
        m.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        m.setSpacing(GAP_INSIDE)

        header = QHBoxLayout()
        title = QLabel("OCR - Medical")
        title.setStyleSheet("font-size:25px; font-weight:900;")

        search = QLineEdit()
        search.setPlaceholderText("Search files, patients IDs…")
        search.setFixedHeight(28)
        search.setStyleSheet(
            "QLineEdit{border:1px solid #e5e7eb; border-radius:8px; padding-left:22px; background:#f9fafb;}"
            "QLineEdit:focus{border-color:#93c5fd; background:#fff;}"
        )
        search.addAction(QIcon("n6_ocrmedical/resources/search.png"), QLineEdit.LeadingPosition)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(search, 0)
        m.addLayout(header)

        sep = QFrame()
        sep.setStyleSheet("background:#e5e7eb; min-height:2px; max-height:2px; border:none;")
        m.addWidget(sep)

        def pill(text, icon_path, minw=210):
            b = QPushButton(text)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(30) 
            b.setMinimumWidth(minw)
            b.setIcon(QIcon(icon_path))
            b.setIconSize(QSize(16, 16))
            b.setStyleSheet(
                "QPushButton{background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:6px 14px; font-weight:600;}"
                "QPushButton:hover{background:#f3f4f6;}"
            )
            return b

        row_actions = QHBoxLayout()
        row_actions.addWidget(pill("Scan from Folder",   "n6_ocrmedical/resources/new-folder.png", 220), 0, Qt.AlignLeft)
        row_actions.addStretch()
        row_actions.addWidget(pill("Capture with Camera","n6_ocrmedical/resources/camera.png",      240), 0, Qt.AlignCenter)
        row_actions.addStretch()
        row_actions.addWidget(pill("Fetch from URL",     "n6_ocrmedical/resources/link.png",        220), 0, Qt.AlignRight)
        m.addLayout(row_actions)

        self.drop = DropZone(self.add_files)
        m.addWidget(self.drop)
        m.addSpacing(GAP_BELOW_DROP)

        path_row = QHBoxLayout(); path_row.setSpacing(8)
        self.pick_btn = QPushButton("Storage Directory"); self.pick_btn.setFixedHeight(28)
        self.pick_btn.setIcon(QIcon("n6_ocrmedical/resources/folder.png")); self.pick_btn.setIconSize(QSize(16, 16))

        self.path_edit = QLineEdit("C:\\Users\\MY COMPUTER\\HIS\\OCR-Medical\\database")

        more = QPushButton("⋯"); more.setFixedSize(28, 28)

        path_row.addWidget(self.pick_btn)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(more)
        m.addLayout(path_row)

        self.total_lbl = QLabel("Total files: 0")
        m.addWidget(self.total_lbl)

        self.file_list = QListWidget()
        self.file_list.setFixedHeight(FILE_LIST_HEIGHT)
        m.addWidget(self.file_list)

        self.result_btn = QPushButton("Result")
        self.result_btn.setCursor(Qt.PointingHandCursor)
        self.result_btn.setFixedHeight(34)
        self.result_btn.setEnabled(False)

        self.result_btn.setStyleSheet("""
            QPushButton {
                border-radius:16px;
                padding:6px 20px;
                font-weight:600;
            }
            QPushButton:enabled {
                background-color:#4f46e5;
                color:white;
            }
            QPushButton:enabled:hover {
                background-color:#4338ca;
                color:white;
            }
            QPushButton:disabled {
                background-color:#d1d5db;
                color:#9ca3af;
            }
        """)

        self.result_btn.clicked.connect(self.on_result_clicked)
        m.addWidget(self.result_btn, 0, Qt.AlignHCenter)

        self.file_list.itemSelectionChanged.connect(self.update_result_btn_state)

        mid_layout.addWidget(top_card)

        intro_card = QFrame()
        intro_card.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")
        i = QVBoxLayout(intro_card)
        i.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)
        i.setSpacing(10)

        i_title = QLabel("Introduction"); i_title.setStyleSheet("font-weight:900;")
        i.addWidget(i_title)
        # Intro giữ nguyên
        row = QHBoxLayout(); row.setSpacing(16)
        def info_block(title, body):
            wrapper = QFrame(); wrapper.setStyleSheet("QFrame{background:#eef2ff; border-radius:10px;}")
            vl = QVBoxLayout(wrapper); vl.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title); t.setStyleSheet("font-weight:800;")
            b = QLabel(body); b.setStyleSheet("color:#4b5563;"); b.setWordWrap(True)
            vl.addWidget(t); vl.addWidget(b)
            return wrapper

        row.addWidget(info_block("Language", "Choose Vietnamese/English for extraction and UI."), 1)
        row.addWidget(info_block("Extract information", "Automatic text & entity extraction from medical records."), 1)
        row.addWidget(info_block("Table extractor", "Detect and parse tables to structured CSV/JSON."), 1)
        i.addLayout(row)

        mid_layout.addWidget(intro_card)

        mid_container = QFrame()
        mid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mid_container.setStyleSheet("QFrame{border:none;}")
        mid_container.setLayout(mid_layout)

        # Sự kiện: chọn thư mục → load danh sách
        self.pick_btn.clicked.connect(self.choose_storage_dir)

        return mid_container

    def _build_right_panel(self) -> QWidget:
        right_layout = QVBoxLayout(); right_layout.setSpacing(GAP_CARD)

        # --- Card lời chào
        greeting = QFrame()
        greeting.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")
        greeting.setMinimumHeight(200)

        rg = QVBoxLayout(greeting)
        rg.setAlignment(Qt.AlignCenter)

        # Hai dòng chữ: "Good ... ," | "Doctor."
        self.greet_lbl1 = QLabel()
        self.greet_lbl1.setAlignment(Qt.AlignCenter)
        self.greet_lbl1.setStyleSheet("font-size:20px; font-weight:700;")

        self.greet_lbl2 = QLabel("Doctor.")
        self.greet_lbl2.setAlignment(Qt.AlignCenter)
        self.greet_lbl2.setStyleSheet("font-size:20px; font-weight:700;")

        # Ảnh minh hoạ
        self.greet_img = QLabel(); self.greet_img.setAlignment(Qt.AlignCenter)

        rg.addWidget(self.greet_lbl1)
        rg.addWidget(self.greet_lbl2)
        rg.addWidget(self.greet_img)

        # Cập nhật và hẹn giờ cập nhật
        self._greet_timer = QTimer(greeting)
        self._greet_timer.setInterval(30 * 60 * 1000)      # 30 phút
        self._greet_timer.timeout.connect(self.update_greeting)
        self.update_greeting()
        self._greet_timer.start()

        right_layout.addWidget(greeting)

        # --- Card lịch sử
        history_card = QFrame()
        history_card.setStyleSheet(f"QFrame{{background:{PANEL_BG}; border-radius:12px;}}")
        rh = QVBoxLayout(history_card)
        rh.setContentsMargins(GAP_PANEL, GAP_PANEL, GAP_PANEL, GAP_PANEL)

        h_title = QLabel("History"); h_title.setStyleSheet("font-size:18px; font-weight:700;")
        self.history = QListWidget()

        rh.addWidget(h_title)
        rh.addWidget(self.history, 1)

        right_layout.addWidget(history_card, 1)

        right_container = QFrame()
        right_container.setFixedWidth(RIGHT_W)
        right_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        right_container.setStyleSheet("QFrame{border:none;}")
        right_container.setLayout(right_layout)
        return right_container


    # ====== NGHIỆP VỤ ======
    def update_greeting(self):
        """Đặt text + ảnh phù hợp theo giờ hiện tại."""
        h = datetime.now().hour
        if 5 <= h <= 11:
            text, img = "Good morning,", GREETING_ICONS["morning"]
        elif 12 <= h <= 16:
            text, img = "Good afternoon,", GREETING_ICONS["afternoon"]
        elif 17 <= h <= 21:
            text, img = "Good evening,", GREETING_ICONS["evening"]
        else:
            text, img = "Good night,", GREETING_ICONS["night"]

        self.greet_lbl1.setText(text)
        self.greet_lbl2.setText("Doctor.")

        pix = QPixmap(img).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.greet_img.setPixmap(pix)

    def choose_storage_dir(self):
        """Mở hộp thoại chọn thư mục, sau đó nạp danh sách file."""
        start_dir = self.path_edit.text().strip()
        base = start_dir if os.path.isdir(start_dir) else ""
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu trữ", base)
        if folder:
            self.path_edit.setText(folder)
            self.populate_from_directory(folder)

    def add_files(self, files: List[str]):
        for f in files:
            name = os.path.basename(f) if f else "Unnamed"
            self._append_file_item(self.file_list.count() + 1, name, f)
        self._update_total_label()

    def _append_file_item(self, idx: int, name: str, full_path: str):
        size = human_size(full_path)
        row = UploadRow(idx, name, size, "Ready")
        it = QListWidgetItem(self.file_list)
        it.setSizeHint(row.sizeHint())
        self.file_list.addItem(it)
        self.file_list.setItemWidget(it, row)

        hrow = HistoryItem(elide(name, self, 180), size)
        hit = QListWidgetItem(self.history)
        hit.setSizeHint(hrow.sizeHint())
        self.history.addItem(hit)
        self.history.setItemWidget(hit, hrow)
        it.setData(Qt.UserRole, full_path)   # lưu đường dẫn thật vào item


    def _update_total_label(self):
        self.total_lbl.setText(f"Total files: {self.file_list.count()}")

    def update_result_btn_state(self):
        self.result_btn.setEnabled(len(self.file_list.selectedItems()) > 0)
    def on_result_clicked(self):
        selected = self.file_list.selectedItems()
        if not selected:
            return

        item = selected[0]
        full_path = item.data(Qt.UserRole)

        # 👉 Chuyển ngay sang ResultPage, hiển thị "Loading..."
        main_win = self.window()
        if hasattr(main_win, "result_page"):
            main_win.result_page.set_result("⏳ Đang chạy OCR với Qwen... vui lòng chờ.")
            main_win.show_result_page()

        # 👉 Tạo thread để gọi model
        self.thread = QThread()
        self.worker = OCRWorker(full_path, "Please extract text from this medical test image.")
        self.worker.moveToThread(self.thread)

        # Kết nối tín hiệu
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start thread
        self.thread.start()

    def on_ocr_finished(self, result_text):
        # Khi có kết quả thì update vào ResultPage
        main_win = self.window()
        if hasattr(main_win, "result_page"):
            main_win.result_page.set_result(result_text)



# =========================
# 5) MAIN WINDOW
# =========================
from result_page import ResultPage
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR - Medical")
        self.resize(1180, 700)

        self.stacked = QStackedWidget()
        self.dashboard = Dashboard()
        self.result_page = ResultPage()

        self.stacked.addWidget(self.dashboard)   # index 0
        self.stacked.addWidget(self.result_page) # index 1
        self.setCentralWidget(self.stacked)

        # 🔹 Nút Result trong sidebar Dashboard
        self.dashboard.btn_result.clicked.connect(self.show_result_page)
        # 🔹 Nút Result ở giữa Dashboard
        self.dashboard.result_requested.connect(self.show_result_page)
        # 🔹 Nút Back trong ResultPage
        self.result_page.back_btn.clicked.connect(self.show_dashboard)
        # 🔹 Nút Home trong sidebar ResultPage
        self.result_page.btn_home.clicked.connect(self.show_dashboard)

    def show_result_page(self):
        self.stacked.setCurrentIndex(1)
        # ép sidebar ResultPage highlight đúng
        if hasattr(self.result_page, "btn_result"):
            self.result_page.btn_result.setChecked(True)
        if hasattr(self.result_page, "btn_home"):
            self.result_page.btn_home.setChecked(False)

    def show_dashboard(self):
        self.stacked.setCurrentIndex(0)
        # ép sidebar Dashboard highlight đúng
        if hasattr(self.dashboard, "btn_home"):
            self.dashboard.btn_home.setChecked(True)
        if hasattr(self.dashboard, "btn_result"):
            self.dashboard.btn_result.setChecked(False)



# =========================
# 6) CHẠY ỨNG DỤNG
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
