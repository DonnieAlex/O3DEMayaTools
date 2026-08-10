from PySide6.QtCore import QObject
from PySide6.QtGui import *
from PySide6.QtWidgets import (QWidget, QSplitter, QMainWindow, QLineEdit,
                               QComboBox, QCheckBox, QVBoxLayout,
                               QPushButton, QSpinBox, QRadioButton,
                               QScrollArea, QMenuBar, QMenu
                               )

import json, os

import FBX_Exporter.UI_Utils as uiu
import FBX_Exporter.ExportUtils as exut
import FBX_Exporter.AnimationClipPanel as acp

this_dir:str = os.path.dirname(os.path.abspath(__file__))
logo_path:str = os.path.join(this_dir, 'icons', 'o3de-logo.png')

win:QMainWindow | None = None

axis_map:dict = {
    'y':'Y UP',
    'z':'Z UP'
}

class FbxExportUI(QMainWindow):
    def __init__(self):
        super().__init__(parent=uiu.find_maya_window())

        win_icon:QIcon = QIcon(QPixmap(logo_path))
        self.setWindowIcon(win_icon)

        self.setWindowTitle("FBX Game Exporter")
        self.setObjectName("FbxExporter_window")

        self.main_widget:QWidget = QWidget()

        # self.main_widget: QSplitter = QSplitter()
        # self.main_widget.setOrientation(Qt.Vertical)

        self.setCentralWidget(self.main_widget)
        self.main_widget.setObjectName('main_widget')

        self.main_widget.setLayout(QVBoxLayout())

        self.widgets_dict:dict = dict()
        self.clip_widgets:list = list()

        exut.enable_plugins()

        self.build()
        self.connect_widgets()
        self.assign_object_names()
        self.assign_tooltips()

    def build(self):


        path_panel, _, path_lnedit, browse_btn, open_fldr_btn = uiu.save_path_widget()
        self.main_widget.layout().addWidget(path_panel)
        file_name_lnedit:QLineEdit = QLineEdit()
        file_name_lnedit.setPlaceholderText('Type file name here.')
        self.main_widget.layout().addWidget(file_name_lnedit)

        options_panel, _, fbx_type_cmb, up_axis_cmb, triangulate_ckbx, incl_anim_ckbx = uiu.fbx_options_widget()
        fbx_type_cmb.addItems(['Binary', 'Ascii'])
        up_axis_cmb.addItems(['Y UP', 'Z UP'])
        up_axis_cmb.setCurrentText(axis_map[uiu.get_up_axis()])

        self.main_widget.layout().addWidget(options_panel)


        anim_options_panel:QWidget = QWidget()
        anim_options_panel.setLayout(QVBoxLayout())
        anim_options_panel.setEnabled(False)
        self.main_widget.layout().addWidget(anim_options_panel)

        range_panel, _, start_frame_spn, end_frame_spn, anim_only_ckbx = uiu.animation_range_widget()
        anim_options_panel.layout().addWidget(range_panel)

        clips_options_panel, _, add_clip_btn, from_bookmarks_btn, to_bookmarks_btn = uiu.animation_clips_widget()
        from_bookmarks_btn.setEnabled(bool(uiu.get_timeslider_bookmarks()))
        to_bookmarks_btn.setEnabled(bool(len(self.clip_widgets)))
        anim_options_panel.layout().addWidget(clips_options_panel)

        anim_clips_scrollarea:QScrollArea = QScrollArea()
        anim_clips_scrollarea.setMinimumHeight(200)
        anim_clips_scrollarea.setWidgetResizable(True)
        anim_clips_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        clips_area_widget:QWidget = QWidget()
        clips_area_widget.setLayout(QVBoxLayout())
        clips_area_widget.layout().setAlignment(Qt.AlignTop)
        anim_clips_scrollarea.setWidget(clips_area_widget)
        anim_clips_scrollarea.setVisible(False)
        anim_options_panel.layout().addWidget(anim_clips_scrollarea)


        statics_panel, _, parent_to_world_ckbx, to_center_ckbx, zero_rotations_ckbx = uiu.static_exports_options()
        self.main_widget.layout().addWidget(statics_panel)

        export_panel, export_btn, export_as_takes_ckbx, strip_namespaces_ckbx, sing_file_radio, multi_file_radio = uiu.export_widget()
        export_as_takes_ckbx.setEnabled(False)
        self.main_widget.layout().addWidget(export_panel)

        self.main_widget.layout().addStretch()

        menu_bar:QMenuBar = QMenuBar(self.main_widget)
        config_menu:QMenu = QMenu('File', menu_bar)
        menu_bar.addMenu(config_menu)
        menu_bar.setNativeMenuBar(True)
        save_config_action:QAction = QAction('Save Configuration', config_menu)
        load_config_action:QAction = QAction('Load Configuration', config_menu)
        config_menu.addAction(save_config_action)
        config_menu.addAction(load_config_action)

        self.widgets_dict['folder_path'] = path_lnedit
        self.widgets_dict['fbx_type'] = fbx_type_cmb
        self.widgets_dict['up_axis'] = up_axis_cmb
        self.widgets_dict['triangulate'] = triangulate_ckbx
        self.widgets_dict['include_anim'] = incl_anim_ckbx
        self.widgets_dict['file_name'] = file_name_lnedit
        self.widgets_dict['start_frame'] = start_frame_spn
        self.widgets_dict['end_frame'] = end_frame_spn
        self.widgets_dict['anim_only'] = anim_only_ckbx

        self.widgets_dict['anim_panel'] = anim_options_panel

        self.widgets_dict['browse'] = browse_btn
        self.widgets_dict['open'] = open_fldr_btn
        self.widgets_dict['add_clip'] = add_clip_btn
        self.widgets_dict['from_bookmarks'] = from_bookmarks_btn
        self.widgets_dict['to_bookmarks'] = to_bookmarks_btn
        self.widgets_dict['clips_panel'] = clips_options_panel
        self.widgets_dict['anim_clips_area'] = anim_clips_scrollarea

        self.widgets_dict['save_config'] = save_config_action
        self.widgets_dict['load_config'] = load_config_action

        self.widgets_dict['parent_to_world'] = parent_to_world_ckbx
        self.widgets_dict['to_center'] = to_center_ckbx
        self.widgets_dict['zero_rotations'] = zero_rotations_ckbx

        self.widgets_dict['export'] = export_btn
        self.widgets_dict['as_takes'] = export_as_takes_ckbx
        self.widgets_dict['strip_namespaces'] = strip_namespaces_ckbx
        self.widgets_dict['sing_file'] = sing_file_radio
        self.widgets_dict['multi_file'] = multi_file_radio

    def assign_object_names(self)->None:
        for name, wid in self.widgets_dict.items():
            wid.setObjectName(name)

    def assign_tooltips(self):
        data:dict = None
        with open(os.path.join(this_dir, 'tooltips', 'tooltips.json'), 'r') as f:
            data = json.load(f)
        for name, tip in data.items():
            self.widgets_dict[name].setToolTip('\n'.join(tip))

    def collect_export_data(self)->dict:
        export_keys:list = [
            'folder_path',
            'file_name',
            'fbx_type',
            'up_axis',
            'triangulate',
            'include_anim',
            'start_frame',
            'end_frame',
            'as_takes',
            'anim_only',
            'strip_namespaces',
            'sing_file',
            'multi_file',
            'parent_to_world',
            'to_center',
            'zero_rotations'
        ]
        pruned_dict:dict = {
            k:v for (k,v) in self.widgets_dict.items() if k in export_keys
        }

        pruned_dict['clips_data'] = [
            acp.ClipData(clip).serialize()
            for clip in self.clip_widgets
        ] or None

        results: tuple[bool, list] = uiu.validate_export_data(pruned_dict)
        errors:bool = results[0]
        if errors:
            msg:str = 'Something went wrong with the overall setup of your export.\n'
            msg += '\n'.join(results[1])
            uiu.buildMsg(['Error:', 'Something went wrong while validating selection.','See script editor for more details.'],
                         ['red', 'orange', 'yellow'],
                         ['Arial', 12]
                         )
            raise Exception(msg)

        raw_data:dict = dict()
        for k, v in pruned_dict.items():
            # if k == 'clips':
            #     raw_data['clips_data'] = v

            if isinstance(v, (QCheckBox, QRadioButton)):
                raw_data[k] = v.isChecked()
            elif isinstance(v, QLineEdit):
                raw_data[k] = v.text()
            elif isinstance(v, QComboBox):
                raw_data[k] = v.currentText().split()[0]
            elif isinstance(v, QSpinBox):
                raw_data[k] = v.value()
            else:
                raw_data[k] = v


        raw_data['convert_world_axis_animation'] = True

        return raw_data


    def connect_widgets(self):
        incl_anim_ckbx:QCheckBox = self.widgets_dict['include_anim']
        anim_panel:QWidget = self.widgets_dict['anim_panel']
        incl_anim_ckbx.toggled.connect(lambda: anim_panel.setEnabled(incl_anim_ckbx.isChecked()))

        browse_btn:QPushButton = self.widgets_dict['browse']
        browse_btn.clicked.connect(self.set_path)

        open_fldr_btn:QPushButton = self.widgets_dict['open']
        open_fldr_btn.clicked.connect(self.open_path)

        file_name_lnedit:QLineEdit = self.widgets_dict['file_name']
        file_name_lnedit.editingFinished.connect(lambda x=file_name_lnedit: self.validate_file_name(x))

        add_clip_btn:QPushButton = self.widgets_dict['add_clip']
        add_clip_btn.clicked.connect(self.add_clip)

        to_bookmarks_btn:QPushButton = self.widgets_dict['to_bookmarks']
        to_bookmarks_btn.clicked.connect(self.clips_to_bookmarks)

        from_bookmarks_btn:QPushButton = self.widgets_dict['from_bookmarks']
        from_bookmarks_btn.clicked.connect(lambda: self.load_clips_settings(uiu.get_timeslider_bookmarks()))

        incl_anim_ckbx.toggled.connect(lambda: from_bookmarks_btn.setEnabled(bool(uiu.get_timeslider_bookmarks())))
        incl_anim_ckbx.toggled.connect(self.enable_takes)

        save_config_action:QAction = self.widgets_dict['save_config']
        save_config_action.triggered.connect(self.save_config)

        load_config_action:QAction = self.widgets_dict['load_config']
        load_config_action.triggered.connect(self.load_config)

        export_btn:QPushButton = self.widgets_dict['export']
        export_btn.clicked.connect(self.export_selection)

    def validate_file_name(self, line_edit:QLineEdit) -> None:
        txt:str = line_edit.text()
        if ' ' in txt:
            txt = txt.replace(' ', '_')
            line_edit.setText(txt)

    def export_selection(self):
        data:dict = self.collect_export_data()
        if self.clip_widgets:
            clips:list = data.get('clips_data') or list()
            pruned_clips:list = list()
            for clip in clips:
                if clip.get('clip_enabled'):
                    pruned_clips.append(clip)
            data['clips_data'] = pruned_clips

        del data['sing_file']
        del data['multi_file']
        del data['parent_to_world']
        del data['to_center']
        del data['zero_rotations']

        parent_to_world:bool = self.widgets_dict['parent_to_world'].isChecked()
        to_center:bool = self.widgets_dict['to_center'].isChecked()
        zero_rotations:bool = self.widgets_dict['zero_rotations'].isChecked()

        include_anim:bool = self.widgets_dict['include_anim'].isChecked()
        anim_only:bool = self.widgets_dict['anim_only'].isChecked()
        strip_namespaces:bool = self.widgets_dict['strip_namespaces'].isChecked()

        single_file:bool = self.widgets_dict['sing_file'].isChecked()
        #multi_file_radio:bool = self.widgets_dict['multi_file'].isChecked()

        selection:list = exut.get_exportable_selection()
        if not selection:
            uiu.buildMsg(['Error:', 'Selection is invalid.', ' Select only meshes please.'],
                         ['red', 'orange', 'blue'],
                         ['Arial', 12])
            raise Exception('Selection is invalid. Select only meshes please.')

        is_referenced:bool = exut.is_referenced(selection[0])
        with exut.undo_queue():
            # check whether the nodes are referenced, and if so, import them before
            # import them before doing anything else
            mesh_export:dict = dict()
            for mesh in selection:
                joints_to_export:list = list()
                skins_to_export:list = list()
                blendshapes_to_export:list = list()

                skin:list|None = exut.get_skin_cluster(mesh)
                blendshapes:list|None = exut.get_blendshapes(mesh)
                joints:list|None = exut.get_joints_from_skin(skin)
                mesh_export[mesh] = dict()
                if skin:
                    skins_to_export.extend(skin)
                if blendshapes:
                    blendshapes_to_export.extend(blendshapes)
                if joints:
                    joints_to_export.extend(exut.get_hierarchy_from_root(exut.get_skel_root(joints)))

                mesh_export[mesh]['skin'] = skins_to_export
                mesh_export[mesh]['blendshapes'] = blendshapes_to_export
                mesh_export[mesh]['joints'] = joints_to_export

            # craft our selection:
            output_selection:list = list()
            for mesh, inclusions in mesh_export.items():
                local_selection:list = list()
                local_selection.append(mesh)
                if inclusions['skin']:
                    local_selection.extend(inclusions['skin'])
                if inclusions['blendshapes']:
                    local_selection.extend(inclusions['blendshapes'])
                if inclusions['joints']:
                    local_selection.extend(inclusions['joints'])
                output_selection.append(local_selection)

            if single_file or len(list(mesh_export.keys())) == 1:
                single_selection:list = list()
                for sel in output_selection:
                    single_selection.extend(sel)
                data['add_obj_name'] = None

                if is_referenced and strip_namespaces:

                    joints_to_duplicate:list|None = exut.filter_selection_by_type(single_selection, 'joint') or None
                    meshes_to_duplicate:list|None = exut.filter_selection_by_type(single_selection, 'mesh') or None

                    dup_meshes, dup_joints = exut.duplicate_special(meshes_to_duplicate, joints_to_duplicate)

                    single_selection.clear()
                    single_selection.extend(dup_meshes)
                    single_selection.extend(dup_joints)
                    for m in dup_meshes:
                        skin:list = exut.get_skin_cluster(m)
                        bs:list = exut.get_blendshapes(m)
                        if skin and skin not in single_selection:
                            single_selection.extend(skin)
                        if bs and bs not in single_selection:
                            single_selection.extend(bs)
                    single_selection = list(set(single_selection))
                elif not is_referenced and strip_namespaces:
                    # just remove namespaces from everything and reconstruct selection
                    exut.remove_namespaces()
                    single_selection = exut.remove_namespaces_from_selection_list(single_selection)

                if exut.selection_includes_skins(single_selection) and (not include_anim):
                    exut.remove_constraints(exut.get_skel_root(exut.filter_selection_by_type(list(set(single_selection)), 'joint')))
                    exut.select_list(single_selection)
                    exut.go_to_bind_pose()

                elif exut.selection_includes_skins(single_selection) and include_anim:
                    if anim_only:
                        single_selection = exut.filter_selection_by_type(single_selection, 'joint')

                elif (not exut.selection_includes_skins(single_selection)) and (not exut.selection_includes_blendshapes(single_selection)):
                    # in this case the selection is only static meshes, no deformers at all anywhere in our selection as a whole
                    if parent_to_world:
                        # we need a safe way to ensure the object names and paths are unique and updated
                        # even after reparenting under world, so we use OpenMaya DagPath objects.
                        objs_dags:list = exut.get_dag_paths(single_selection)
                        exut.parent_to_world(single_selection)
                        single_selection.clear()
                        single_selection.extend(exut.get_paths_from_dags(objs_dags))
                    if to_center:
                        exut.to_center(single_selection)
                    if zero_rotations:
                        exut.zero_rotation(single_selection)

                if self.clip_widgets and (not data.get('as_takes')):
                    clips:list = data.get('clips_data')
                    for clip in clips:
                        data['add_obj_name'] = clip.get('clip_name')
                        data['start_frame'] = clip.get('clip_start_frame')
                        data['end_frame'] = clip.get('clip_end_frame')
                        exut.export_selection(single_selection, **data)
                else:
                    exut.export_selection(single_selection, **data)

            else:
                for sel in output_selection:

                    if is_referenced and strip_namespaces:

                        joints_to_duplicate: list | None = exut.filter_selection_by_type(sel, 'joint') or None
                        meshes_to_duplicate: list | None = exut.filter_selection_by_type(sel, 'mesh') or None

                        dup_meshes, dup_joints = exut.duplicate_special(meshes_to_duplicate, joints_to_duplicate)

                        sel.clear()
                        sel.extend(dup_meshes)
                        sel.extend(dup_joints)
                        for m in dup_meshes:
                            skin: list = exut.get_skin_cluster(m)
                            bs: list = exut.get_blendshapes(m)
                            if skin and skin not in sel:
                                sel.extend(skin)
                            if bs and bs not in sel:
                                sel.extend(bs)
                        sel = list(set(sel))

                    elif not is_referenced and strip_namespaces:
                        # just remove namespaces from everything and reconstruct selection
                        exut.remove_namespaces()
                        sel = exut.remove_namespaces_from_selection_list(sel)

                    mesh:str = exut.filter_selection_by_type(sel, 'mesh')[0]
                    obj_name:str = mesh.split('|')[-1]
                    data['add_obj_name'] = obj_name

                    if exut.selection_includes_skins(sel) and (not include_anim):
                        exut.remove_constraints(
                            exut.get_skel_root(exut.filter_selection_by_type(list(set(sel)), 'joint')))
                        exut.select_list(sel)
                        exut.go_to_bind_pose()

                    elif exut.selection_includes_skins(sel) and include_anim:
                        if anim_only:
                            sel = exut.filter_selection_by_type(sel, 'joint')

                    elif (not exut.selection_includes_skins(sel)) and (not exut.selection_includes_blendshapes(sel)):
                        # in this case the selection is only static meshes, no deformers at all anywhere in our selection as a whole
                        if parent_to_world:
                            # we need a safe way to ensure the object names and paths are unique and updated
                            # even after reparenting under world, so we use OpenMaya DagPath objects.
                            objs_dags: list = exut.get_dag_paths(sel)
                            exut.parent_to_world(sel)
                            sel.clear()
                            sel.extend(exut.get_paths_from_dags(objs_dags))
                        if to_center:
                            exut.to_center(sel)
                        if zero_rotations:
                            exut.zero_rotation(sel)

                    if self.clip_widgets and (not data.get('as_takes')):
                        clips: list = data.get('clips_data')
                        for clip in clips:
                            data['add_obj_name'] = f'{obj_name}_{clip.get("clip_name")}'
                            data['start_frame'] = clip.get('clip_start_frame')
                            data['end_frame'] = clip.get('clip_end_frame')
                            exut.export_selection(sel, **data)
                    else:
                        exut.export_selection(sel, **data)

                    if is_referenced:
                        exut.delete_selection(sel)
        uiu.buildMsg(['Success:', 'Selection exported successfully!'],
                     ['green', 'blue'],
                     ['Arial', 12])

    def enable_takes(self):
        export_as_takes_ckbx: QCheckBox = self.widgets_dict['as_takes']
        anim_only_ckbx: QCheckBox = self.widgets_dict['anim_only']
        incl_anim_ckbx: QCheckBox = self.widgets_dict['include_anim']

        if not incl_anim_ckbx.isChecked() and anim_only_ckbx.isChecked():
            anim_only_ckbx.setChecked(False)
        if self.clip_widgets and incl_anim_ckbx.isChecked():
            export_as_takes_ckbx.setEnabled(True)

        if (not self.clip_widgets) or (not incl_anim_ckbx.isChecked()):
            export_as_takes_ckbx.setEnabled(False)
            export_as_takes_ckbx.setChecked(False)

    def add_clip(self, data:dict | None = None):
        self.widgets_dict['to_bookmarks'].setEnabled(True)
        self.widgets_dict['as_takes'].setEnabled(True)

        anim_options_panel:QScrollArea = self.widgets_dict['anim_clips_area']
        anim_options_panel.setVisible(True)

        clip:acp.ClipPanel = acp.ClipPanel()
        clip.parent_class = self
        anim_options_panel.widget().layout().addWidget(clip)
        num:int = len(self.clip_widgets)
        clip.clip_name_lbl.setText(str(num+1))
        self.clip_widgets.append(clip)
        if data:
            clip.clip_enabled_ckbx.setChecked(data['clip_enabled'])
            clip.clip_name_lbl.setText(str(data['clip_position']))
            clip.clip_name_line.setText(data['clip_name'])
            clip.start_spin.setValue(data['clip_start_frame'])
            clip.end_spin.setValue(data['clip_end_frame'])
        self.enable_takes()

    def rename_clips_on_destroy(self, destroyed: acp.ClipPanel):
        self.clip_widgets.remove(destroyed)
        if not self.clip_widgets:
            self.widgets_dict['to_bookmarks'].setEnabled(False)
            self.widgets_dict['as_takes'].setEnabled(False)
            self.widgets_dict['anim_clips_area'].setVisible(False)
            self.enable_takes()
            return
        self.widgets_dict['from_bookmarks'].setEnabled(bool(uiu.get_timeslider_bookmarks()))
        for idx, clip in enumerate(self.clip_widgets):
            clip.clip_name_lbl.setText(str(idx+1))
        self.adjustSize()

    def set_path(self):
        path:str | None = uiu.folder_select(self, 'Choose Export Folder', uiu.get_workspace_path())
        if not path:
            return
        path_line:QLineEdit = self.widgets_dict['folder_path']
        path_line.setText(path)

    def open_path(self):
        path_line: QLineEdit = self.widgets_dict['folder_path']
        uiu.open_path(path_line.text())

    def save_config(self)->None:
        print('saving config')
        data:dict = self.collect_export_data()
        del data['convert_world_axis_animation']
        path: list | None = uiu.get_save_file_name(self,
                                                   'Save Window Configuration',
                                                   uiu.get_workspace_path(),
                                                   {
                                                       'Configuration File': ['config']
                                                   })
        if not path:
            return

        folder_path, file_name = path
        if not file_name.endswith('.config'):
            file_name += '.config'

        file_path: str = os.path.join(folder_path, file_name)
        print('Configuration saved to', file_path)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_config(self)->None:
        print('loading config')
        path: str | None = uiu.get_open_file_name(self,
                                                  'Load Window Configuration',
                                                  uiu.get_workspace_path(),
                                                  {
                                                      'Configuration File': ['config']
                                                  }
                                                  )
        if not path:
            return
        file_path: str = os.path.join(*path)

        data: dict = dict()
        with open(file_path, 'r') as f:
            data = json.load(f)

        for name, value in data.items():
            if not isinstance(value, list):
                wid:QObject = self.widgets_dict[name]
                if isinstance(wid, QLineEdit):
                    wid.setText(value)
                elif isinstance(wid, QComboBox):
                    mapped:str = axis_map.get(value.lower())
                    if mapped: wid.setCurrentText(mapped)
                    else: wid.setCurrentText(value)
                elif isinstance(wid, (QCheckBox, QRadioButton)):
                    wid.setChecked(value)
                elif isinstance(wid, QSpinBox):
                    wid.setValue(value)
            else:
                for clip in value:
                    self.add_clip(clip)

    def clips_to_bookmarks(self):
        out_list: list = list()
        for clip in self.clip_widgets:
            serializer: acp.ClipData = acp.ClipData(clip)
            out_list.append(serializer.serialize())
        uiu.create_timeslider_bookmarks_from_clips(out_list)

    def load_clips_settings(self, clips_list:list[dict]):
        for clip in self.clip_widgets:
            clip.deleteLater()
        self.clip_widgets.clear()

        for clip in clips_list:
            self.add_clip(clip)
        self.adjustSize()

    @classmethod
    def load_window(cls):
        global win
        if win:
            try:
                win.close()
                win.deleteLater()
            except Exception as e:
                print(str(e))
                win = None
        win = FbxExportUI()
        win.show()
        return win
