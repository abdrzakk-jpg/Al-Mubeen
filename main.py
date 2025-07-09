# Developed By abdrzakk-jpg

import sys, json, requests, os 
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QLayout,
    QWidget,
    QMessageBox
)

# *Thread Worker to avoid app crash
class Worker(QThread):
    # prepare signal to emit response 
    response = Signal(tuple)
    def __init__(self, tafseer_id, surah_id, aya_number):
        super().__init__()
        self.tafseer_id = tafseer_id
        self.surah_id = surah_id
        self.aya_number = aya_number
        
    #
    def run(self):
        try:
            tefseer_req = requests.get(f"http://api.quran-tafseer.com/tafseer/{self.tafseer_id}/{self.surah_id}/{self.aya_number}")
            ayah_req = requests.get(f"http://api.quran-tafseer.com/quran/{self.surah_id}/{self.aya_number}/")
            data = (tefseer_req.json()["text"], ayah_req.json()["text"])
            self.response.emit(data)
        except Exception :
            data = ("يرجى التأكد من الاتصال بالشبكة", "نعتذر عن وجود خطأ في تفسير الآية، يرجى التأكد من توفر اتصال بالشبكة")
        self.response.emit(data)
        
        
# *main app(GUI) class
class QuranInterpreterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مفسر القرآن الكريم")
        self.setFixedSize(900, 650)
        
        
        # get file path by part of the given path
        self.get_path = lambda file: os.path.join(os.path.abspath((os.path.dirname(__file__))), file)
        
        
        
        self.PALETTE = {
            "base": "#0F172A",
            "surface": "#1E293B",
            "overlay": "#334155",
            "accent": "#818CF8",
            "text": "#F8FAFC",
            "subtext": "#94A3B8"
        }
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PALETTE["accent"]}, stop:1 #6366F1);
                color: {self.PALETTE["text"]};
                border-radius: 8px;
                padding: 10px 25px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PALETTE["accent"]}, stop:1 #4F46E5);
            }}
        """)

        # Create main central widget
        central = QWidget()
        central.setStyleSheet(f"""
            #centralWidget {{
                background: {self.PALETTE["base"]};
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        font_file_path = self.get_path('./assets/NotoKufiArabic.ttf')
        self.default_font = "Arial"
        if not os.path.exists(font_file_path):
            self.send_err_message('خطأ', "تعذر تحميل ملف الخط 'NotoKufiArabic' يرجى اعادة تحميل البرنامج لحل المشكلة")
        else:
            default_font_id = QFontDatabase.addApplicationFont(font_file_path)
            # *change the default_font to "NotoKufiArabic"
            self.default_font = QFontDatabase.applicationFontFamilies(default_font_id)[0]

        central.setObjectName("centralWidget")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        self.current_surah: str = "الفاتحة"
        self.tafseer_of: str = "الميسر"
        
        # Set background style
        central.setStyleSheet("""
            #centralWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #0a1929, stop:1 #0c2a4a);
                border-radius: 15px;
            }
        """)
        
        # Title with decorative elements 
        title_container = QWidget()
        title_container.setObjectName("titleContainer")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("مُفَسِّرُ القُرْآنِ")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setFamily(self.default_font)
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"""
            color: {self.PALETTE["accent"]};
            background: rgba(30, 41, 59, 0.7);
            border-radius: 15px;
            padding: 15px 0;
            border: 1px solid rgba(129, 140, 248, 0.2);
        """)
        title_layout.addWidget(title)
        
        main_layout.addWidget(title_container)
        
        # Controls row
        controls = QHBoxLayout()
        controls.setSpacing(15)
        
        

        
        # Surah combobox
        surah_container = QWidget()
        surah_layout = QVBoxLayout(surah_container)
        surah_layout.setContentsMargins(0, 0, 0, 0)
        surah_layout.setSpacing(5)
        
        surah_label = QLabel("السورة:")
        surah_label.setObjectName("sectionLabel")
        surah_layout.addWidget(surah_label)
        
        # Surah comboBox
        self.cb_surah = QComboBox()
        self.cb_surah.currentTextChanged.connect(self.set_current_surah)
        self.cb_surah.setFixedHeight(40)
        surah_layout.addWidget(self.cb_surah)
        
        controls.addWidget(surah_container)
        
        # Ayah range container
        ayah_container = QWidget()
        ayah_layout = QHBoxLayout(ayah_container)
        ayah_layout.setContentsMargins(0, 0, 0, 0)
        ayah_layout.setSpacing(10)
        
        # From Ayah
        from_container = QWidget()
        from_layout = QVBoxLayout(from_container)
        from_layout.setContentsMargins(0, 0, 0, 0)
        from_layout.setSpacing(5)
        
        from_label = QLabel("الآية:")
        from_label.setObjectName("sectionLabel")
        from_layout.addWidget(from_label)
        
        # Ayat comboBox
        self.cb_aya = QComboBox()
        self.cb_aya.setFixedHeight(40)
        from_layout.addWidget(self.cb_aya)
        
        ayah_layout.addWidget(from_container)
        controls.addWidget(ayah_container)
        
        # Tafseer combobox
        tafseer_container = QWidget()
        tafseer_layout = QVBoxLayout(tafseer_container)
        tafseer_layout.setContentsMargins(0, 0, 0, 0)
        tafseer_layout.setSpacing(5)
        
        tafseer_label = QLabel("تفسير")
        tafseer_label.setObjectName("sectionLabel")
        tafseer_layout.addWidget(tafseer_label)
        
        self.cb_tafseer = QComboBox()
        self.cb_tafseer.addItems(["الميسر", "ابن كثير", "الطبري", "السعدي", "القرطبي"])
        self.cb_tafseer.setFixedHeight(40)
        tafseer_layout.addWidget(self.cb_tafseer)
        controls.addWidget(tafseer_container)
        
        # Interpret button
        self.btn = QPushButton("فسر")
        self.btn.setEnabled(True)
        self.btn.setFont(QFont(self.default_font))
        self.btn.setFixedHeight(40)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.start_proccess)
        controls.addWidget(self.btn)
        
        main_layout.addLayout(controls)
        
        # Bottom frame
        frame = QFrame()
        frame.setObjectName("contentFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        frame.setStyleSheet(f"""
            #contentFrame {{
                background: rgba(30, 41, 59, 0.5);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                
            }}
        """)
        
        # Verse label with decorative background
        verse_container = QFrame()
        verse_container.setObjectName("verseContainer")
        verse_layout = QVBoxLayout(verse_container)
        verse_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_verse = QLabel("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
        self.lbl_verse.setObjectName("verseLabel")
        self.lbl_verse.setAlignment(Qt.AlignCenter)
        self.lbl_verse.setWordWrap(True)
        verse_font = QFont()
        verse_font.setFamily(self.default_font)
        verse_font.setPointSize(18)
        self.lbl_verse.setFont(verse_font)
        verse_layout.addWidget(self.lbl_verse)
        frame_layout.addWidget(verse_container)
        
        # Tafseer section
        tafseer_label = QLabel("التفسير:")
        tafseer_label.setObjectName("sectionLabel")
        frame_layout.addWidget(tafseer_label)
        
        self.txt_tafseer = QTextEdit()
        self.txt_tafseer.setObjectName("tafseerText")
        self.txt_tafseer.setReadOnly(True)
        self.txt_tafseer.setPlaceholderText("التفسير سيظهر هنا ...")
        self.txt_tafseer.setStyleSheet(f"""
            #tafseerText {{
                background: rgba(30, 41, 59, 0.7);
                color: {self.PALETTE["text"]};
                border-radius: 12px;
                border: 1px solid {self.PALETTE["overlay"]};
            }}
        """)
        tafseer_font = QFont()
        tafseer_font.setFamily(self.default_font)
        tafseer_font.setPointSize(14)
        
        self.txt_tafseer.setFont(tafseer_font)
        frame_layout.addWidget(self.txt_tafseer)
        
        main_layout.addWidget(frame)
        
        # Footer
        footer = QLabel("ادعوا لأمي بالشفاء | Pray for my mother to heal")
        footer.setFont(QFont(self.default_font, 15, 700))
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
        footer.setStyleSheet(f"color: {self.PALETTE['subtext']};")

        
        # Apply global styles with Arabic font
        combo_style = f"""
            QComboBox {{
                background: {self.PALETTE["surface"]};
                border: 1px solid {self.PALETTE["overlay"]};
                color: {self.PALETTE["text"]};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox QAbstractItemView {{
                background: {self.PALETTE["surface"]};
                color: {self.PALETTE["text"]};
                border: 1px solid {self.PALETTE["overlay"]};
                border-radius: 8px;
            }}
        """
        
        self.cb_surah.setStyleSheet(combo_style)
        self.cb_aya.setStyleSheet(combo_style)
        self.cb_tafseer.setStyleSheet(combo_style)
        
        self.setStyleSheet(f"""
            #centralWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A1B26, stop:1 #16161E);
                border-radius: 15px;
            }}
            #titleContainer {{
                background-color: rgba(26, 27, 38, 0.9);
                border-radius: 15px;
                border: 1px solid #3B3D5B;
            }}
            #contentFrame {{
                background-color: rgba(26, 27, 38, 0.8);
                border-radius: 15px;
                border: 1px solid #3B3D5B;
            }}
            #verseContainer {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(72, 52, 106, 0.4), stop:1 rgba(42, 62, 114, 0.4));
                border-radius: 10px;
                border: 1px solid #3B3D5B;
            }}
            #tafseerText {{
                background-color: rgba(26, 27, 38, 0.9);
                border-radius: 10px;
                border: 1px solid #3B3D5B;
                color: #A9B1D6;
                padding: 20px;
                font-size: 14px;
                line-height: 1.6;
            }}
            QLabel#titleLabel {{
                color: #BB9AF7;
                padding: 8px 0;
                font-size: 26px;
                letter-spacing: 1px;
            }}
            QLabel#sectionLabel {{
                color: #7AA2F7;
                font-size: 15px;
                font-weight: 600;
            }}
            QLabel#verseLabel {{
                color: whitesmoke;
                font-size: 20px;
                line-height: 1.8;
            }}
            QPushButton {{
                background-color: #BB9AF7;
                border-radius: 10px;
                color: #1A1B26;
                padding: 8px 20px;
                font-size: 16px;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #7AA2F7;
            }}
            QPushButton:pressed {{
                background-color: #6272A4;
            }}
            QComboBox {{
                background-color: rgba(59, 61, 91, 0.4);
                border: 1px solid #3B3D5B;
                color: #A9B1D6;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #24283B;
                border: 1px solid #3B3D5B;
                color: #A9B1D6;
                selection-background-color: #7AA2F7;
            }}
            QComboBox QAbstractItemView:hover {{
                background-color: #15396B;
            }}
            QLabel {{
                color: #565F89;
            }}
        """)
        
        footer.setStyleSheet("color: #5d8bbb; font-size: 12px; padding-top: 10px;")
        
        self.setCentralWidget(central)
        
        self.set_combo_box_content()
        
    
    
    
    def set_combo_box_content(self):
        if self.load_suar_file() is None:
            self.send_err_message("خطأ", "تعذر تحميل ملف معلومات الصور, يرجى اعادة تثبيت البرنامج لحل المشكلة")
            exit(404)
        else:
            self.cb_aya.addItems([str(aya+1) for aya in range(self.get_surah_info(self.current_surah)["numberOfAyat"])])
            self.cb_surah.addItems(["سورة: "+surah for surah in self.get_all_suar()])
        
        
    # load data from /data/suar.json
    def load_suar_file(self)-> dict | None:
        file_path = self.get_path("assets/suar.json")
        if os.path.exists(file_path):
            
            with open(file_path, "r") as json_file:
                return json.load(json_file)
        else:
            return None
        
    def get_all_suar(self):
        return self.load_suar_file()
    
    
    # get surah_info via surah name
    def get_surah_info(self, surah_name: str) ->  dict:
        all_suar = self.load_suar_file()
        return all_suar[surah_name]
        
    # set the current surah and update ayat number field
    def set_current_surah(self, value: str)-> None:
        self.current_surah = value.split("سورة:")[-1].strip()    
        # update ayat comboBox
        self.cb_aya.clear()
        self.cb_aya.addItems([str(aya+1) for aya in range(self.get_surah_info(self.current_surah)["numberOfAyat"])])
        
        
    # send data to API to get the Tafseer
    def start_proccess(self, )-> None:
        # disbale button until get the data from API
        self.btn.setText("󰂭")
        self.btn.setCursor(Qt.CursorShape.BusyCursor)
        self.btn.setEnabled(False)
        
        # initilaize data to api request
        aya_number = self.cb_aya.currentText()
        surah = self.cb_surah.currentText().removeprefix("سورة:").strip()
        surah_id = self.get_surah_info(surah)["id"]
        tafseer_type = self.cb_tafseer.currentText()
        tafseer_id = 1
        if tafseer_type == "ابن كثير": tafseer_id = 4
        if tafseer_type == "الطبري": tafseer_id = 8
        if tafseer_type == "القرطبي": tafseer_id = 7
        if tafseer_type == "السعدي": tafseer_id = 3
        
    
        self.worker = Worker(tafseer_id, surah_id, aya_number)
        self.worker.response.connect(self.update_gui)
        self.worker.start()
        

        
    def update_gui(self, value)-> None:
        # update GUI elements 
        self.txt_tafseer.setText(f"{value[0]}")
        self.lbl_verse.setText(value[1])
        self.btn.setText("فسر")
        # reset btn to default state
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setEnabled(True)
        
        
    def send_err_message(self, title:str, text:str)-> None:
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Icon.Critical)
        msgbox.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        
        msgbox.setText(text)
        msgbox.setStyleSheet(f"""
                            QPushButton {{
                                background-color: #BB9AF7;
                                border:none;
                                color: #1A1B26;
                                padding:3px 6px;
                                font-weight: 600;
                                font-family:{self.default_font}
                            }}
                            QLabel{{
                                font-family:{self.default_font};
                                min-width: 300px; 
                            }}
                            QPushButton:hover {{
                                background-color: #7AA2F7;
                            }}
                             """)
        msgbox.addButton("حسنا", QMessageBox.ButtonRole.AcceptRole)

        msgbox.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msgbox.setWindowTitle(title)

        msgbox.exec()
        
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuranInterpreterUI()
    window.show()
    sys.exit(app.exec())
