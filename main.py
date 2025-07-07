
import sys, json, requests

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
    QWidget,
)

# Thread Worker to avoid app crash
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
        except Exception as e:
            data = (f"Error: {str(e)}", "نعتذر عن وجود خطأ في تفسير الآية، يرجى التأكد من توفر اتصال بالشبكة")
        self.response.emit(data)
        
        
# main app(GUI) class
class QuranInterpreterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مفسر القرآن الكريم")
        self.setFixedSize(900, 650)
        
        # Create main central widget
        central = QWidget()
        secondary_font_id = QFontDatabase.addApplicationFont('./assets/NotoKufiArabic.ttf')
        self.secondary_font = QFontDatabase.applicationFontFamilies(secondary_font_id)[0]

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
        title = QLabel("مفسر القرآن")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()    
        title_font.setFamily(self.secondary_font)
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
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
        self.cb_surah.addItems(["سورة: "+surah for surah in self.load_depends()["all_surah_names"]])
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
        
        # Ayah comboBox
        self.cb_aya = QComboBox()
        self.cb_aya.addItems([str(aya+1) for aya in range(self.get_surah_info(self.current_surah)["numberOfAyat"])])
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
        verse_font.setFamily(self.secondary_font)
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
        tafseer_font = QFont()
        tafseer_font.setFamily(self.secondary_font)
        tafseer_font.setPointSize(14)
        
        self.txt_tafseer.setFont(tafseer_font)
        frame_layout.addWidget(self.txt_tafseer)
        
        main_layout.addWidget(frame)
        
        # Footer
        footer = QLabel("ادعوا لأمي بالشفاء | Pray for my mother to heal")
        footer.setFont(QFont(self.secondary_font, 15, 700))
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
        
        # Apply global styles with Arabic font
        combo_style = f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #3a6186;
                border-radius: 8px;
                padding: 5px 15px;
                color: white;
                font-size: 14px;
                font-family: '{self.secondary_font}';
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #0c2a4a;
                color: white;
                selection-background-color: #3a6186;
                border: 1px solid #3a6186;
                border-radius: 5px;
                font-family: '{self.secondary_font}';
            }}
        """
        
        self.cb_surah.setStyleSheet(combo_style)
        self.cb_aya.setStyleSheet(combo_style)
        self.cb_tafseer.setStyleSheet(combo_style)
        
        self.setStyleSheet(f"""
            #centralWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #0a1929, stop:1 #0c2a4a);
                border-radius: 15px;
            }}
            #titleContainer {{
                background-color: rgba(12, 42, 74, 0.7);
                border-radius: 15px;
                border: 1px solid #3a6186;
            }}
            #contentFrame {{
                background-color: rgba(10, 25, 41, 0.7);
                border-radius: 15px;
                border: 1px solid #3a6186;
            }}
            #verseContainer {{
                background-color: #0c2a4a;
                border-radius: 10px;
                border: 1px solid #3a6186;
            }}
            #tafseerText {{
                background-color: rgba(12, 42, 74, 0.8);
                border-radius: 10px;
                border: 1px solid #3a6186;
                color: #e6e6e6;
                padding: 15px;
                font-size: 15px;
                font-family: '{self.secondary_font}';
            }}
            QLabel#titleLabel {{
                color: #c9a96e;
                padding: 5px 0;
                font-family: '{self.secondary_font}';
            }}
            QLabel#sectionLabel {{
                color: #c9a96e;
                font-size: 14px;
                font-weight: bold;
                font-family: '{self.secondary_font}';
            }}
            QLabel#verseLabel {{
                color: #ffffff;
                font-size: 18px;
                font-family: '{self.secondary_font}';
            }}
            QPushButton {{
                background-color: #c9a96e;
                border-radius: 10px;
                color: #0a1929;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 16px;
                font-family: '{self.secondary_font}';
            }}
            QPushButton:hover {{
                background-color: #d8b97c;
            }}
            QPushButton:pressed {{
                background-color: #ba984d;
            }}
            QLabel {{
                font-family: '{self.secondary_font}';
            }}
        """)
        
        footer.setStyleSheet("color: #5d8bbb; font-size: 12px; padding-top: 10px;")
        
        self.setCentralWidget(central)
        
    # load data from /data/dependencies.json
    def load_depends(self) -> dict:  # TODO: Edit The Name 
        with open("./assets/dependencies.json", "r") as file:
            all_surah = json.load(file)
        return {
            "all_surah_names":all_surah,
            
        }
        
    # get surah_info via surah name
    def get_surah_info(self, surah_name: str) ->  dict:
        with open("./assets/dependencies.json", "r") as file:
            all_surah = json.load(file)
        return all_surah[surah_name]
        
    # set the current surah and update ayat number field
    def set_current_surah(self, value: str):
        self.current_surah = value.split("سورة:")[-1].strip()    
        # update ayat comboBox
        self.cb_aya.clear()
        self.cb_aya.addItems([str(aya+1) for aya in range(self.get_surah_info(self.current_surah)["numberOfAyat"])])
        
        
    # send data to API to get the Tafseer
    def start_proccess(self, ):
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
        

        
    def update_gui(self, value):
        # update GUI elements 
        self.txt_tafseer.setText(f"{value[0]}")
        self.lbl_verse.setText(value[1])
        self.btn.setText("فسر")
        # reset btn to default state
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setEnabled(True)
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuranInterpreterUI()
    window.show()
    sys.exit(app.exec())


