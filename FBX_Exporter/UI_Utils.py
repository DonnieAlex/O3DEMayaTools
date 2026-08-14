
from PySide6.QtCore import QObject
from PySide6.QtGui import *
from PySide6.QtWidgets import (QWidget, QFileDialog, QLineEdit,
                               QComboBox, QCheckBox, QLabel,
                               QPushButton, QSpinBox, QHBoxLayout, QVBoxLayout,
                               QApplication, QRadioButton)

import maya.cmds as mc

import platform, subprocess, os
import random


colors = {
    'red':'FA0000',
    'green':'0FFA00',
    'yellow':'F6FA00',
    'orange':'FAA300',
    'gray':'C6C6C6',
    'blue':'00F2FA'

}

def buildMsg(msg_list:list,
             color_list:list=[],
             font_data:list[str,int]=['Utsaa', 12],
             pos:str='midCenter')->None:
    """
    accepted colors list:
    'red'
    'green'
    'yellow'
    'orange'
    'gray'
    'blue'
    font_data: type list[str, int]
        where:
        str: font name (must be installed on machine),
        int: font size
    pos: type str, always refers to the active viewport
        valid values:
            'topLeft'
            'topCenter'
            'topRight'
            'midLeft'
            'midCenter'
            'midCenterTop'
            'midCenterBot'
            'midRight'
            'botLeft'
            'botCenter'
            'botRight'

      """
    # make sure that each message has an associated color
    if len(msg_list) > len(color_list):
        length:int = len(color_list)
        # if not, we keep appending a default gray for each undefined message chunk's color
        while length < len(msg_list):
            color_list.append('gray')
            length = len(color_list)
    msg_color = zip(msg_list, color_list)
    output:str = str()
    # color tag template '<span style="color:#FA0000;\"> text <\span>'
    for msg, clr in msg_color:
        # note we also account for trailing whitespaces here, s no need to care about them when calling the function
        tmp:str = '<span style="color:#{};\">{} <\span>'.format(colors.get(clr), msg)
        output += tmp
    mc.inViewMessage(amg=output, font=font_data[0], fontSize=font_data[1], pos=pos, fade=True)



def find_window(window_name:str)->QWidget | None:
    win:list = [w for w in QApplication.allWidgets() if window_name.lower() in w.objectName().lower()]
    return win[0] if len(win) else None

def find_maya_window()->QWidget | None:
    """ Convenience method to retrieve the QObject pointer for the maya main window, instead of relying on
     shiboken2.wrapInstance. With Maya 2023 and the automatic loading process, shiboken2 was causing crashes
    at startup (wasn't ready/loaded yet), while PySide2 was well functioning and ready to perform this operation """
    maya_wids = [i for i in QApplication.topLevelWidgets() if 'mayawindow' in i.objectName().lower()]
    return maya_wids[0] if maya_wids else None

def folder_select(parent, dialog_title, start_path)->str | None:
    """ convenience method to summon a QFileDialog that parents itself to a control, gets a title and a start path
    in one go, eliminating the need for a QObject string translation wherever this function is needed. Contains
    a nested utility function to perform this translation.
    Returns None instead of an empty string as the default Qt implementation would. Easier for type-checked behaviours.
    """
    def tr(text):
        return QObject.tr(text)

    dialog = QFileDialog()
    path_to_folder = dialog.getExistingDirectory(parent,
                                               tr(dialog_title),
                                               tr(start_path),
                                               QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    if not path_to_folder:
        return None
    return path_to_folder

def get_open_file_name(parent, dialog_title:str, start_path:str, file_types_dict:dict):
    def tr(text):
        return QObject.tr(text)

    file_types_str = str()
    for key, values in file_types_dict.items():
        file_types_str += key
        file_types_str += '({})'.format(' '.join(['*.{}'.format(i) for i in values]))
        file_types_str += ';;'
    dialog = QFileDialog()
    path_to_file = dialog.getOpenFileName(
        parent,
        tr(dialog_title),
        tr(start_path),
        tr(file_types_str)
    )
    if path_to_file[0] == '':
        return None

    path_to_file = path_to_file[0]
    file_name = path_to_file.split('/')[-1]
    path = path_to_file.replace(file_name, '')

    return path, file_name

def get_save_file_name(parent, dialog_title, start_path, file_types_dict):
    """ convenience method to summon a QFileDialog that parents itself to a control, gets a title and a start path
    in one go, eliminating the need for a QObject string translation wherever this function is needed. Contains
    a nested utility function to perform this translation.
    Returns None instead of tuple containing empty strings as the default Qt implementation would. Easier for type-checked behaviours.
    Returns a tuple(str, str) where
        tuple[0] = path,
        tuple[1] = file_name
        file_name removes any whitespace and replaces them with an underscore
        as opposed to the native Qt implementation where
            tuple[0] = file_path,
            tuple[1] = file type as fed to the QFileDialog (i.e.: "Images (*.png *.tga *.jpg)")
        defaults to the first extension in the file extensions tuple if non is supplied in the dialog
    """

    def tr(text):
        return QObject.tr(text)

    file_types_str = str()
    for key, values in file_types_dict.items():
        file_types_str += key
        file_types_str += '({})'.format(' '.join(['*.{}'.format(i) for i in values]))
        file_types_str += ';;'
    dialog = QFileDialog()
    path_to_file = dialog.getSaveFileName(
        parent,
        tr(dialog_title),
        tr(start_path),
        tr(file_types_str)
    )
    if path_to_file[0] == '':
        return None

    path_to_file = path_to_file[0]
    file_name = path_to_file.split('/')[-1]
    path = path_to_file.replace(file_name, '')
    file_name = file_name.replace(' ', '_')

    return path, file_name

def get_workspace_path()->str:
    return mc.workspace(query=True, rootDirectory=True)

def get_up_axis()->str:
    return mc.upAxis(query=True, axis=True)

def get_platform_open_cmd()->str:
    name:str = platform.system()
    cmd:str
    if name == 'Windows':
        cmd = 'os.startfile({})'
    elif name == 'Linux':
        cmd = 'xdg-open'
    else:
        cmd = 'open'
    return cmd

def open_path(path:str)->None:
    cmd: str = get_platform_open_cmd()
    path = path.strip()
    if '{}' in cmd:  # Windows
        cmd = cmd.format(path)
        eval(cmd)
    else:
        path = f'"{path}"' if ' ' in path else path
        cmd += f' {path} &'
        xx = subprocess.Popen(cmd, shell=True, bufsize=-1, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        lines_iterator = iter(xx.stdout.readline, b'')
        while xx.poll() is None:
            for line in lines_iterator:
                nline:bytes = line.rstrip()
                print(nline.decode())
        print('TODO: find out why it won\'t work')

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

def static_exports_options()->tuple[QWidget, QCheckBox, QCheckBox, QCheckBox]:
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

def get_timeslider_bookmarks()->list | None:
    bookmarks:list = mc.ls(type='timeSliderBookmark')
    if not bookmarks:
        return
    bookmarks.sort(key=lambda x: mc.getAttr(f'{x}.timeRangeStart'))
    out_data:list[dict] = list()
    for idx, clip in enumerate(bookmarks):
        data:dict = dict()
        data['clip_position'] = idx
        data['clip_name'] = mc.getAttr(f'{clip}.name')
        data['clip_start_frame'] = mc.getAttr(f'{clip}.timeRangeStart')
        data['clip_end_frame'] = mc.getAttr(f'{clip}.timeRangeStop')
        out_data.append(data)
    return out_data

def create_timeslider_bookmarks_from_clips(clips:list[dict])->None:
    #mc.createNode('timeSliderBookmark')
    low:int|None = None
    high:int = 0
    for clip in clips:
        start_frame:int = clip['clip_start_frame']
        end_frame:int = clip['clip_end_frame']

        if low is None:
            low = start_frame
        if start_frame < low:
            low = start_frame
        if end_frame > high:
            high=end_frame
        clip_name = clip['clip_name']
        if mc.objExists(clip_name):
            if mc.nodeType(clip_name) == 'timeSliderBookmark':
                continue
        node = mc.createNode('timeSliderBookmark', name=clip_name)
        mc.setAttr(f'{node}.timeRangeStart', start_frame)
        mc.setAttr(f'{node}.timeRangeStop', end_frame)
        mc.setAttr(f'{node}.name', clip_name, type='string')
        color:list = [random.random() for _ in range(3)]
        mc.setAttr(f'{node}.color', *color, type='double3')

    mc.playbackOptions(minTime=low, maxTime=high)

def validate_export_data(export_data:dict)->tuple[bool, list]:

    clips_data:list[dict] | None = export_data.get('clips')
    validation_dict:dict = export_data.copy()

    errors:list = list()
    frame_range:list | None = None
    if not validation_dict['folder_path'].text():
        errors.append('Missing Save Path')
    if not os.path.exists(validation_dict['folder_path'].text()):
        errors.append('Save Path does not exist')
    if not validation_dict['file_name'].text():
        errors.append('Missing File Name')

    if validation_dict['include_anim'].isChecked():
        start:int = validation_dict['start_frame'].value()
        end:int = validation_dict['end_frame'].value()
        if start > end or start == end:
            errors.append('Unsupported combination in Start and End frame')
        frame_range = [start, end]
    if clips_data:
        for clip in clips_data:
            pos:str = clip['clip_position']
            name:str = clip['clip_name']
            start_frame:int = clip['clip_start_frame']
            end_frame:int = clip['clip_end_frame']
            if start_frame > end_frame or start_frame == end_frame:
                errors.append(f'Unsupported combination in Start and End frame in clip {name} at position {pos}')
            if not name:
                errors.append(f'Missing Clip Name at position {pos}')
            if start_frame < frame_range[0] or end_frame > frame_range[1]:
                errors.append(f'Check the frame ranges of clip {name} at position {pos}, mismatch with overall animation range.')
    if errors:
        return True, errors
    return False, ['All good to go.']
