
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ClipPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.parent_class:FbxExportUI = None

        self.main_panel:QWidget = QWidget()
        self.main_panel.setLayout(QHBoxLayout())
        self.layout().addWidget(self.main_panel)

        self.clip_enabled_ckbx:QCheckBox = QCheckBox()
        self.clip_enabled_ckbx.toggled.connect(self.status_toggle)
        self.clip_enabled_ckbx.setChecked(True)
        self.layout().addWidget(self.clip_enabled_ckbx)


        self.clip_name_lbl:QLabel = QLabel() # rename at spawn time
        self.clip_name_line:QLineEdit = QLineEdit()
        self.clip_name_line.editingFinished.connect(self.validate_clip_name)
        clip_name_lyt:QHBoxLayout = QHBoxLayout()
        clip_name_lyt.addWidget(self.clip_name_lbl)
        clip_name_lyt.addWidget(self.clip_name_line)

        self.start_spin:QSpinBox = QSpinBox()
        self.start_spin.setRange(0, 1000000)
        start_lbl:QLabel = QLabel('Start')
        start_lyt:QHBoxLayout = QVBoxLayout()
        start_lyt.addWidget(start_lbl)
        start_lyt.addWidget(self.start_spin)

        self.end_spin:QSpinBox = QSpinBox()
        self.end_spin.setRange(0, 1000000)
        end_lbl:QLabel = QLabel('End')
        end_lyt:QHBoxLayout = QVBoxLayout()
        end_lyt.addWidget(end_lbl)
        end_lyt.addWidget(self.end_spin)

        start_lyt.setAlignment(Qt.AlignTop)
        end_lyt.setAlignment(Qt.AlignTop)

        delete_btn:QPushButton = QPushButton('-')
        delete_btn.clicked.connect(self.self_destroy)

        self.main_panel.layout().addLayout(clip_name_lyt)
        self.main_panel.layout().addLayout(start_lyt)
        self.main_panel.layout().addLayout(end_lyt)
        self.main_panel.layout().addWidget(delete_btn)
        self.main_panel.layout().setAlignment(Qt.AlignTop)

        self.layout().setAlignment(Qt.AlignTop)

    def status_toggle(self):
        self.main_panel.setEnabled(self.clip_enabled_ckbx.isChecked())

    def validate_clip_name(self) -> None:
        txt:str = self.clip_name_line.text()
        if ' ' in txt:
            txt = txt.replace(' ', '_')
            self.clip_name_line.setText(txt)

    def self_destroy(self):
        self.parent_class.rename_clips_on_destroy(self)
        self.deleteLater()

class ClipData:
    def __init__(self, clip:ClipPanel):
        self.clip_enabled:bool = clip.clip_enabled_ckbx.isChecked()
        self.clip_position:int = int(clip.clip_name_lbl.text())
        self.clip_name:str = clip.clip_name_line.text()
        self.clip_start_frame:int = clip.start_spin.value()
        self.clip_end_frame:int = clip.end_spin.value()

    def serialize(self):
        return {
            'clip_enabled': self.clip_enabled,
            'clip_position':self.clip_position,
            'clip_name':self.clip_name,
            'clip_start_frame':self.clip_start_frame,
            'clip_end_frame':self.clip_end_frame
        }