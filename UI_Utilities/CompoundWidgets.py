from PySide6.QtGui import *
from PySide6.QtWidgets import (QWidget, QFileDialog, QLineEdit,
                               QComboBox, QCheckBox, QLabel, QSlider,
                               QPushButton, QSpinBox, QHBoxLayout, QVBoxLayout,
                               QRadioButton, QSplitter, QFrame, QButtonGroup, QDoubleSpinBox)

def save_path_widget()->tuple[QWidget, QLabel, QLineEdit, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Save Path')
    path_lnedit:QLineEdit = QLineEdit()
    path_lnedit.setPlaceholderText('Type the output path, or use the Browse button     ----->')
    browse_btn:QPushButton = QPushButton('Browse')
    open_fldr_btn:QPushButton = QPushButton('Open Folder')
    panel.layout().addWidget(lbl)
    panel.layout().addWidget(path_lnedit)
    panel.layout().addWidget(browse_btn)
    panel.layout().addWidget(open_fldr_btn)
    return panel, lbl, path_lnedit, browse_btn, open_fldr_btn

def fbx_options_widget()->tuple[QWidget, QLabel, QComboBox, QComboBox, QCheckBox, QCheckBox]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('FBX Options')
    fbx_type_cmb:QComboBox = QComboBox()
    up_axis_cmb:QComboBox = QComboBox()
    triangulate_ckbx:QCheckBox = QCheckBox('Triangulate')
    incl_anim_ckbx:QCheckBox = QCheckBox('Include Animation')
    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(fbx_type_cmb)
    panel.layout().addWidget(up_axis_cmb)
    panel.layout().addWidget(triangulate_ckbx)
    panel.layout().addWidget(incl_anim_ckbx)
    return panel, lbl, fbx_type_cmb, up_axis_cmb, triangulate_ckbx, incl_anim_ckbx

def animation_range_widget()->tuple[QWidget, QLabel, QSpinBox, QSpinBox, QCheckBox]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Animation Range')
    start_frame_spn:QSpinBox = QSpinBox()
    end_frame_spn:QSpinBox = QSpinBox()
    start_frame_spn.setRange(0, 10000000)
    end_frame_spn.setRange(0, 10000000)
    anim_only_ckbx:QCheckBox = QCheckBox('Animation Only')
    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(start_frame_spn)
    panel.layout().addWidget(end_frame_spn)
    panel.layout().addWidget(anim_only_ckbx)
    return panel, lbl, start_frame_spn, end_frame_spn, anim_only_ckbx

def animation_clips_widget()->tuple[QWidget, QLabel, QPushButton, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Clips')
    add_btn:QPushButton = QPushButton('+')

    from_bookmarks_btn:QPushButton = QPushButton('From Bookmarks')
    to_bookmarks_btn: QPushButton = QPushButton('To Bookmarks')

    panel.layout().addWidget(lbl)
    #panel.layout().addStretch()
    panel.layout().addWidget(add_btn)
    panel.layout().addStretch()
    panel.layout().addWidget(from_bookmarks_btn)
    panel.layout().addWidget(to_bookmarks_btn)
    return panel, lbl, add_btn, from_bookmarks_btn, to_bookmarks_btn

def configuration_options_widget()->tuple[QWidget, QPushButton, QPushButton]:

    panel: QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    first_lyt:QHBoxLayout = QHBoxLayout()
    first_lyt.setAlignment(Qt.AlignCenter)
    second_lyt:QHBoxLayout = QHBoxLayout()
    panel.layout().addLayout(first_lyt)
    panel.layout().addLayout(second_lyt)

    lbl: QLabel = QLabel('Configuration')
    save_btn: QPushButton = QPushButton('Save')
    load_btn: QPushButton = QPushButton('Load')
    first_lyt.addWidget(lbl)
    second_lyt.addWidget(save_btn)
    second_lyt.addWidget(load_btn)
    return panel, save_btn, load_btn

def static_exports_options()->tuple[QWidget, QLabel, QCheckBox, QCheckBox, QCheckBox]:
    panel: QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Static Meshes')
    parent_to_world_ckbx:QCheckBox = QCheckBox('Parent to World')
    to_center_ckbx:QCheckBox = QCheckBox('To Center')
    zero_rotations_ckbx:QCheckBox = QCheckBox('Zero Rotations')
    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(parent_to_world_ckbx)
    panel.layout().addWidget(to_center_ckbx)
    panel.layout().addWidget(zero_rotations_ckbx)
    return panel, lbl, parent_to_world_ckbx, to_center_ckbx, zero_rotations_ckbx

def export_widget()->tuple[QWidget, QPushButton, QCheckBox, QCheckBox, QCheckBox, QRadioButton, QRadioButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    first_lyt:QHBoxLayout = QHBoxLayout()
    second_lyt:QHBoxLayout = QHBoxLayout()
    panel.layout().addLayout(first_lyt)
    panel.layout().addLayout(second_lyt)

    lbl:QLabel = QLabel('Extra Export Options')
    first_lyt.addWidget(lbl)
    first_lyt.addStretch()

    export_btn:QPushButton = QPushButton('Export')
    embed_media_ckbx:QCheckBox = QCheckBox('Embed Media')
    export_as_takes_ckbx:QCheckBox = QCheckBox('Export As Takes')
    strip_namespaces_ckbx:QCheckBox = QCheckBox('Remove Namespaces')

    radio_lyt:QHBoxLayout = QHBoxLayout()
    sing_radio:QRadioButton = QRadioButton('Single File')
    sing_radio.setChecked(True)
    multi_radio:QRadioButton = QRadioButton('Multiple Files')
    radio_lyt.addWidget(sing_radio)
    radio_lyt.addWidget(multi_radio)

    first_lyt.addWidget(embed_media_ckbx)
    first_lyt.addWidget(export_as_takes_ckbx)
    first_lyt.addWidget(strip_namespaces_ckbx)
    #panel.layout().addStretch()
    second_lyt.addStretch()
    second_lyt.addLayout(radio_lyt)
    second_lyt.addWidget(export_btn)
    return panel, export_btn, embed_media_ckbx, export_as_takes_ckbx, strip_namespaces_ckbx, sing_radio, multi_radio

def world_axis_widgets()->tuple[QWidget, QLabel, QRadioButton, QRadioButton]:
    panel: QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl: QLabel = QLabel()
    Y_radio:QRadioButton = QRadioButton('Y Up')
    Z_radio:QRadioButton = QRadioButton('Z Up')

    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(Y_radio)
    panel.layout().addWidget(Z_radio)
    return panel, lbl, Y_radio, Z_radio

def config_selector_widget(config_items:list)->tuple[QWidget, QComboBox]:
    panel: QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl: QLabel = QLabel('Configurations')
    configs_combobox:QComboBox = QComboBox()
    configs_combobox.addItems(config_items)

    panel.layout().addWidget(lbl)
    panel.layout().addWidget(configs_combobox)
    panel.layout().addStretch()
    return panel, configs_combobox

def root_joint_options()->tuple[QWidget, QLabel, QComboBox, QPushButton]:
    panel: QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl: QLabel = QLabel('Root Joint')
    selector:QComboBox = QComboBox()
    items:list = ['Y Up', 'Z Up']
    selector.addItems(items)
    selector.setCurrentIndex(1)
    btn:QPushButton = QPushButton('Setup')

    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(selector)
    panel.layout().addWidget(btn)

    return panel, lbl, selector, btn

def create_splitter(widgets:list[QWidget], direction:str='vertical')->QSplitter:
    splitter:QSplitter = QSplitter()
    if len(widgets)==1:
        widgets.insert(0,QWidget())
    #widgets.append(QWidget())
    for wid in widgets:
        splitter.addWidget(wid)
    if direction == 'vertical':
        splitter.setOrientation(Qt.Vertical)
    return splitter

def create_separator(label:str|None=None, orientation:str='horizontal')->QWidget:
    orient_mapping:dict = {
        'vertical': QFrame.VLine,
        'horizontal': QFrame.HLine
    }
    panel: QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    line:QFrame = QFrame()
    line.setFrameShape(orient_mapping.get(orientation))
    line.setFrameShadow(QFrame.Sunken)
    panel.layout().addWidget(line)
    if label is not None:
        lbl: QLabel = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        line2 = QFrame()
        line2.setFrameShape(orient_mapping.get(orientation))
        line2.setFrameShadow(QFrame.Sunken)
        panel.layout().addWidget(lbl)
        panel.layout().addWidget(line2)
    return panel

def reorient_selected_guides_widget()->tuple[QWidget, QRadioButton, QRadioButton, QRadioButton,
                                            QRadioButton, QRadioButton, QRadioButton,
                                            QRadioButton, QRadioButton, QRadioButton,
                                            QComboBox, QPushButton, QComboBox, QPushButton]:

    panel: QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    panel.layout().setAlignment(Qt.AlignTop)
    # lbl: QLabel = QLabel('Orient Selected Guides')
    # lbl.setAlignment(Qt.AlignCenter)
    radios_lyt:QVBoxLayout = QVBoxLayout()

    primary_x_radio:QRadioButton = QRadioButton('X')
    primary_y_radio:QRadioButton = QRadioButton('Y')
    primary_z_radio:QRadioButton = QRadioButton('Z')

    secondary_x_radio:QRadioButton = QRadioButton('X')
    secondary_y_radio:QRadioButton = QRadioButton('Y')
    secondary_z_radio:QRadioButton = QRadioButton('Z')

    world_dir_combo:QComboBox = QComboBox()
    world_dir_combo.addItems(['+', '-'])
    world_x_radio: QRadioButton = QRadioButton('X')
    world_y_radio: QRadioButton = QRadioButton('Y')
    world_z_radio: QRadioButton = QRadioButton('Z')

    primary_x_radio.setChecked(True)
    secondary_z_radio.setChecked(True)
    world_x_radio.setChecked(True)

    primaries_lyt: QHBoxLayout = QHBoxLayout()
    primaries_lyt.addWidget(QLabel('Twist Axis'))
    primaries_lyt.addStretch()
    primaries_lyt.addWidget(primary_x_radio)
    primaries_lyt.addWidget(primary_y_radio)
    primaries_lyt.addWidget(primary_z_radio)

    secondaries_lyt:QHBoxLayout = QHBoxLayout()
    secondaries_lyt.addWidget(QLabel('Main Axis'))
    secondaries_lyt.addStretch()
    secondaries_lyt.addWidget(secondary_x_radio)
    secondaries_lyt.addWidget(secondary_y_radio)
    secondaries_lyt.addWidget(secondary_z_radio)

    world_axis_lyt:QHBoxLayout = QHBoxLayout()
    world_axis_lyt.addWidget(QLabel('Main Axis World Direction'))
    world_axis_lyt.addStretch()
    world_axis_lyt.addWidget(world_dir_combo)
    world_axis_lyt.addWidget(world_x_radio)
    world_axis_lyt.addWidget(world_y_radio)
    world_axis_lyt.addWidget(world_z_radio)

    primary_wid:QWidget = QWidget()
    primary_wid.setLayout(primaries_lyt)
    secondary_wid:QWidget = QWidget()
    secondary_wid.setLayout(secondaries_lyt)
    world_axis_wid:QWidget = QWidget()
    world_axis_wid.setLayout(world_axis_lyt)

    radios_lyt.addWidget(primary_wid)
    radios_lyt.addWidget(secondary_wid)
    radios_lyt.addWidget(world_axis_wid)

    # panel.layout().addWidget(lbl)
    panel.layout().addLayout(radios_lyt)

    orient_btn:QPushButton = QPushButton('Orient Selected Guides')
    mirror_dir_combo:QComboBox = QComboBox()
    mirror_dir_combo.addItems('XYZ')
    mirror_btn:QPushButton = QPushButton('Mirror Selected Guides')
    btns_lyt:QHBoxLayout = QHBoxLayout()
    btns_lyt.addWidget(mirror_dir_combo)
    btns_lyt.addWidget(mirror_btn)
    btns_lyt.addStretch()
    btns_lyt.addWidget(orient_btn)
    panel.layout().addLayout(btns_lyt)
    return (panel, primary_x_radio, primary_y_radio, primary_z_radio, secondary_x_radio, secondary_y_radio,
            secondary_z_radio, world_x_radio, world_y_radio, world_z_radio, world_dir_combo, orient_btn,
            mirror_dir_combo, mirror_btn)

def attach_appendages_to_limb_widget()->tuple[QWidget, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())

    snap_selected_btn:QPushButton = QPushButton('Snap Selected To Limb')
    attach_selected_btn:QPushButton = QPushButton('Attach Selected To Limb')

    panel.layout().addWidget(snap_selected_btn)
    panel.layout().addWidget(attach_selected_btn)
    return panel, snap_selected_btn, attach_selected_btn

def guides_template_file_widget()->tuple[QWidget, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    # lbl:QLabel = QLabel('Guides Template')
    # panel.layout().addWidget(lbl)
    # lbl.setAlignment(Qt.AlignCenter)

    btn_lyt:QHBoxLayout = QHBoxLayout()
    save_btn:QPushButton = QPushButton('Save Guides Template')
    load_btn:QPushButton = QPushButton('Load Guides Template')
    btn_lyt.addWidget(load_btn)
    btn_lyt.addWidget(save_btn)
    panel.layout().addLayout(btn_lyt)
    return panel, save_btn, load_btn

def add_twist_joints_widget()->tuple[QWidget, QSpinBox, QDoubleSpinBox]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Add Twist Joints')
    number_spinbox:QSpinBox = QSpinBox()
    fraction_spinbox:QDoubleSpinBox = QDoubleSpinBox()
    panel.layout().addWidget(lbl)
    panel.layout().addStretch()
    panel.layout().addWidget(number_spinbox)
    panel.layout().addWidget(fraction_spinbox)

    number_spinbox.setMinimum(1)
    fraction_spinbox.setMaximum(1.0)
    fraction_spinbox.setSingleStep(0.1)
    fraction_spinbox.setDecimals(1)
    fraction_spinbox.setValue(1.0)
    return panel, number_spinbox, fraction_spinbox

def update_guides_from_joints_widget()->tuple[QWidget, QPushButton, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    update_guides_btn:QPushButton = QPushButton('Start Guides Update')
    update_joints_btn:QPushButton = QPushButton('Start Joints Update')
    confirm_btn:QPushButton = QPushButton('Finish Guides Update')
    panel.layout().addWidget(update_guides_btn)
    panel.layout().addWidget(update_joints_btn)
    panel.layout().addWidget(confirm_btn)
    return panel, update_guides_btn, update_joints_btn, confirm_btn

def skinning_panel_widget()->tuple[QWidget, QSlider, QComboBox, QComboBox, QComboBox, QPushButton]:
    def update_label(lbl:QLabel, value:int)->None:
        txt:str = f'Max Influences: {value}'
        lbl.setText(txt)

    panel:QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    influences_number_slider:QSlider = QSlider(Qt.Orientation.Horizontal)
    influences_number_slider.setMinimum(1)
    influences_number_slider.setMaximum(8)
    influences_number_slider.setSingleStep(1)
    influences_number_slider.setValue(4)
    influence_lbl:QLabel = QLabel('Max Influences: ')
    influences_number_slider.valueChanged.connect(lambda: update_label(influence_lbl, influences_number_slider.value()))
    influences_number_slider.valueChanged.emit(1)

    slider_lyt:QVBoxLayout = QVBoxLayout()
    slider_lyt.addWidget(influence_lbl)
    slider_lyt.addWidget(influences_number_slider)
    slider_lyt.setAlignment(Qt.AlignTop)

    bind_to_combo:QComboBox = QComboBox()
    bind_to_combo.addItems(['Joints Hierarchy', 'Selected Joints'])
    bind_to_lbl:QLabel = QLabel('Bind To:')
    bind_to_lyt:QVBoxLayout = QVBoxLayout()
    bind_to_lyt.addWidget(bind_to_lbl)
    bind_to_lyt.addWidget(bind_to_combo)
    bind_to_lyt.setAlignment(Qt.AlignTop)

    bind_method_combo:QComboBox = QComboBox()
    bind_method_combo.addItems(['Closest Distance', 'Closest in Hierarchy'])
    bind_lbl:QLabel = QLabel('Bind Method')
    bind_lyt:QVBoxLayout = QVBoxLayout()
    bind_lyt.addWidget(bind_lbl)
    bind_lyt.addWidget(bind_method_combo)
    bind_lyt.setAlignment(Qt.AlignTop)

    skin_method_combo:QComboBox = QComboBox()
    skin_method_combo.addItems(['Classic Linear', 'Dual Quaternion'])
    skin_lbl:QLabel = QLabel('Skinning Method')
    skin_lyt:QVBoxLayout = QVBoxLayout()
    skin_lyt.addWidget(skin_lbl)
    skin_lyt.addWidget(skin_method_combo)
    skin_lyt.setAlignment(Qt.AlignTop)

    bind_btn:QPushButton = QPushButton('Bind Skin')

    general_lyt:QHBoxLayout = QHBoxLayout()
    general_lyt.addLayout(bind_to_lyt)
    general_lyt.addLayout(bind_lyt)
    general_lyt.addLayout(skin_lyt)
    general_lyt.setAlignment(Qt.AlignTop)

    panel.layout().addLayout(general_lyt)
    panel.layout().addLayout(slider_lyt)
    panel.layout().addWidget(bind_btn)
    panel.layout().setAlignment(Qt.AlignTop)

    return panel, influences_number_slider, bind_to_combo, bind_method_combo, skin_method_combo, bind_btn

def characterize_widget()->tuple[QWidget,QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QVBoxLayout())
    hik_btn:QPushButton = QPushButton('Characterize')
    panel.layout().addWidget(hik_btn)
    return panel, hik_btn

def guides_presets_widget()->tuple[QWidget, QComboBox, QPushButton, QPushButton]:
    panel:QWidget = QWidget()
    panel.setLayout(QHBoxLayout())
    lbl:QLabel = QLabel('Guides Presets')
    preset_combo:QComboBox = QComboBox()
    preset_btn:QPushButton = QPushButton('Load Preset')
    save_preset_btn:QPushButton = QPushButton('Save Preset')
    panel.layout().addWidget(lbl)
    panel.layout().addWidget(preset_combo)
    panel.layout().addStretch()
    panel.layout().addWidget(preset_btn)
    panel.layout().addWidget(save_preset_btn)
    return panel, preset_combo, preset_btn, save_preset_btn