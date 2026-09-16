
from PySide6.QtCore import QObject
from PySide6.QtGui import *
from PySide6.QtWidgets import (QWidget, QFileDialog, QLineEdit,
                               QComboBox, QCheckBox, QLabel,
                               QPushButton, QSpinBox, QHBoxLayout, QVBoxLayout,
                               QApplication, QRadioButton)

import maya.cmds as mc
import maya.OpenMaya as om

import platform, subprocess, os, random, json



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

def set_up_axis(axis:str)->None:
    mc.upAxis(axis=axis, rotateView=True)
    mc.viewSet(mc.modelEditor('modelPanel4', query=True, camera=True), persp=True)

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


def setWidgetPalette(widget, color_list, text_color=None):
    """ convenience method to change a widget color without using stylesheets
    arguments:
        widget: type PySide6 widget (any)
        color: list(int, int, int) 0-255 range | list(float, float, float) 0.0-1.0 range

    """
    # let's check whether we have a float set range for the color tuple and, if so, convert them
    # a 0-255 range for Qt to make use of it
    if isinstance(color_list[0], float):
        color_list = [
            int(i * 255)
            for i in color_list
        ]
    palette = QPalette()
    color = QColor(*color_list)
    palette.setColor(QPalette.Button, color)
    palette.setColor(QPalette.Window, color)
    palette.setColor(QPalette.Base, color)
    if text_color is not None:
        if isinstance(text_color[0], float):
            text_color = [
                int(i * 255)
                for i in text_color
            ]
        text_qColor = QColor(*text_color)
        palette.setColor(QPalette.Text, text_qColor)
        palette.setColor(QPalette.BrightText, text_qColor)
        palette.setColor(QPalette.ButtonText, text_qColor)
        palette.setColor(QPalette.WindowText, text_qColor)
        palette.setColor(QPalette.HighlightedText, text_qColor)
        palette.setColor(QPalette.Active, QPalette.Text, text_qColor)
        palette.setColor(QPalette.Active, QPalette.ButtonText, text_qColor)
        palette.setColor(QPalette.Active, QPalette.WindowText, text_qColor)
        try:
            palette.setColor(QPalette.Foreground, text_qColor)
            palette.setColor(QPalette.Active, QPalette.Foreground, text_qColor)
        except AttributeError:
            pass
        palette.setColor(QPalette.Active, QPalette.HighlightedText, text_qColor)

    widget.setAutoFillBackground(True)
    widget.setPalette(palette)

def create_guides_list_widget(member_name:str, data:dict) -> QWidget:
    out_wid:QWidget = QWidget()
    out_wid.setObjectName(f"{member_name}_widget")
    out_wid.setLayout(QHBoxLayout())
    ckbx:QCheckBox = QCheckBox(member_name)
    ckbx.setChecked(data[member_name][1] if member_name in data else True)
    out_wid.layout().addWidget(ckbx)
    if member_name in data:
        out_wid.layout().addStretch()
        spinbox:QSpinBox = QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setValue(data[member_name][0])
        out_wid.layout().addWidget(spinbox)
    return out_wid

def get_existing_section_guides(section:str)->list:
    locs:list = [mc.listRelatives(i, parent=True, fullPath=True)[0]
                 for i in mc.ls(type='locator')
                 ]
    section_guides:list = [i
                           for i in locs
                           if mc.attributeQuery('guidesSection', node=i, exists=True)
                           ]
    return [i for i in section_guides if mc.getAttr(f'{i}.guidesSection') == section]

def select_items(items:list)->None:
    mc.select(items, replace=True)

def list_selected_items(vtx_convert=False)->list:
    selection:list = mc.ls(orderedSelection=True, long=True)
    if vtx_convert and not len([i for i in selection if '.vtx[' in i]):
        mc.ConvertSelectionToVertices()
        selection = mc.ls(selection=True, long=True, flatten=True)
    return selection

def get_dag_paths(objs:list)->list[om.MDagPath]:
    dag_paths: list[om.MDagPath] = list()
    selList = om.MSelectionList()
    for obj in objs:
        selList.add(obj)
    it: om.MItSelectionList = om.MItSelectionList(selList)
    while not it.isDone():
        dag: om.MDagPath = om.MDagPath()
        it.getDagPath(dag)
        dag_paths.append(dag)
        it.next()
    return dag_paths

def rename(old_name:str, new_name:str)->None:
    mc.rename(old_name, new_name)

def dump_widgets_to_file_for_tool_tips(widgets_dict:dict, tooltips_path:str)->None:
    file_data:dict = dict()
    with open(tooltips_path, 'r') as f:
        file_data = json.load(f)

    out:dict = {
        k:'' if not file_data.get(k) else file_data.get(k) for k in widgets_dict.keys()
    }

    file_data.update(out)

    with open(tooltips_path, 'w') as f:
        json.dump(file_data, f, indent=4)

def text_input_prompt(message:str='Please enter a name for your preset')->str:
    prompt:str = mc.promptDialog(title='Preset Name',
                                 message=message,
                                 button=['OK', 'Cancel'],
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
    if prompt != 'Cancel':
        prompt = mc.promptDialog(query=True, text=True)
        if not prompt: prompt = 'Cancel'
    return prompt

def confirm_dialog(title:str, message:str)->str:
    conf:str = mc.confirmDialog(title=title,
                                message=message,
                                button=['OK', 'Cancel'],
                                cancelButton='Cancel',
                                dismissString='Cancel',
                                defaultButton='OK')
    return conf

def track_selection_order():
    if not mc.selectPref(query=True, trackSelectionOrder=True):
        mc.selectPref(trackSelectionOrder=True)
        buildMsg(['INFO:', 'Selection order tracking was disabled, enabling it now.', 'Selection order dependant features may not work as expected until next Maya restart.'],
                 ['yellow', 'orange', 'red'],
                 ['Arial', 22])

def get_attribute(obj:str, attribute_name:str, kwargs:dict={}):
    if not kwargs:
        return mc.getAttr(f'{obj}.{attribute_name}')
    else:
        return mc.getAttr(f'{obj}.{attribute_name}', **kwargs)

def attribute_exists(obj:str, attribute_name:str)->bool:
    return mc.attributeQuery(attribute_name, node=obj, exists=True)

def set_attribute(obj:str, attribute_name:str, value, kwargs:dict={})->None:
    mc.setAttr(f'{obj}.{attribute_name}', value, **kwargs)