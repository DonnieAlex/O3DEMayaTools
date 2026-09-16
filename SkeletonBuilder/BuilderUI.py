import os, json

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import UI_Utilities.UI_Utils as uiu
import UI_Utilities.CompoundWidgets as cw
import UI_Utilities.SkeletonUtils as su

from UI_Utilities.CustomWidgets import (CollapsibleWidgetContainer, GuidesLists, PosingSetup, PosesListWidget)

this_dir:str = os.path.abspath(os.path.dirname(__file__))
config_dir:str = os.path.join(this_dir, 'configuration')
input_names_path:str = os.path.join(config_dir, 'input_names.json')
joints_names_configs_path:str = os.path.join(config_dir, 'joints_names_configuration.json')
tooltips_path:str = os.path.join(config_dir, 'tooltips.json')
presets_path:str = os.path.join(config_dir, 'guide_presets.json')

skel_win = None

class SkeletonBuilderUI(QMainWindow):
    _up_axis:str = str()
    _input_names:dict = dict()
    _joints_names:dict = dict()
    _config_names:list = list()
    _guides_hik_map:dict = dict()
    _hik_list:list = list()
    _hik_joints_ids:dict = dict()
    _hik_to_joints:dict = dict()
    _hik_sides_map:dict = dict()
    _guides_presets:dict = dict()

    def __init__(self):
        super().__init__(parent=uiu.find_maya_window())
        self.setWindowTitle("Skeleton Builder")
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setAlignment(Qt.AlignTop)

        self.widgets_in_splitter:list = list()
        # plug in
        su.hik_plugin_check()
        uiu.track_selection_order()
        # plug in end
        # data variables
        self.widgets_dict:dict = dict()
        self.get_hik_list()
        self.read_input_names()
        self.read_configs_names()
        self.read_joints_names()
        self.read_presets()
        #end of data variables


        self.build_ui()
        self.connect_widgets()

        self.populate_guides_container_widget()
        self.populate_joints_container_widget()
        self.populate_posing_container_widget()

        self.add_tool_tips()

        self.resize(600, 250)

    @property
    def guides_presets(self):
        return self._guides_presets

    @guides_presets.setter
    def guides_presets(self, value:dict):
        # self._guides_presets = value
        self._guides_presets.update(value)

    @property
    def input_names(self):
        return self._input_names

    @input_names.setter
    def input_names(self, value:dict):
        # self._input_names = value
        self._input_names.update(value)

    @property
    def joints_names_config(self):
        return self._joints_names

    @joints_names_config.setter
    def joints_names_config(self, value:dict):
        # self._joints_names = value
        self._joints_names.update(value)

    @property
    def configurations_names(self):
        return self._config_names

    @property
    def up_axis(self):
        self._up_axis = uiu.get_up_axis()
        return self._up_axis

    @up_axis.setter
    def up_axis(self, value:str):
        self._up_axis = value
        uiu.set_up_axis(value)

    @property
    def guides_hik_map(self):
        return self._guides_hik_map

    @guides_hik_map.setter
    def guides_hik_map(self, value:dict):
        # self._guides_hik_map = value
        self._guides_hik_map.update(value)

    @property
    def hik_joints_names(self):
        return self._hik_list

    @hik_joints_names.setter
    def hik_joints_names(self, value:list):
        self._hik_list = value

    @property
    def hik_joints_ids(self):
        return self._hik_joints_ids

    @hik_joints_ids.setter
    def hik_joints_ids(self, value:dict):
        # self._hik_joints_ids = value
        self._hik_joints_ids.update(value)

    @property
    def hik_to_joints_map(self):
        return self._hik_to_joints

    @hik_to_joints_map.setter
    def hik_to_joints_map(self, value:dict):
        # self._hik_to_joints = value
        self._hik_to_joints.update(value)

    @property
    def hik_sides_map(self):
        return self._hik_sides_map

    @hik_sides_map.setter
    def hik_sides_map(self, value:dict):
        # self._hik_sides_map = value
        self._hik_sides_map.update(value)

    def get_hik_list(self):
        self.hik_joints_ids = su.get_hik_joints_ids()
        self.hik_joints_names = list(self.hik_joints_ids.keys())

    def read_presets(self)->None:
        with open(presets_path, 'r') as f:
            self.guides_presets = json.load(f)

    def save_preset(self)->None:
        data: dict | None = su.get_all_guides_hierarchies()
        if not data:
            return
        name:str = uiu.text_input_prompt().replace(' ', '_')
        if name == 'Cancel':
            return
        if name in self.guides_presets:
            overwrite:str = uiu.confirm_dialog(title='Overwrite Entry Confirmation', message='Entry exist, proceed anyway?')
            if overwrite == 'Cancel':
                return
        new_data:dict = {
            name:data
        }
        self.guides_presets.update(new_data)
        with open(presets_path, 'w') as f:
            json.dump(self.guides_presets, f, indent=4)

        combo:QComboBox = self.widgets_dict.get('guides_preset_combo')
        combo.clear()
        combo.addItems(list(self.guides_presets.keys()))


    def read_guides_hik_map(self, config_data:dict):
        self.guides_hik_map:dict = config_data.get('guides_to_hik_map')

    def read_input_names(self):
        data:dict = dict()
        with open(input_names_path, 'r') as f:
            data = json.load(f)
        self.input_names = data

    def read_configs_names(self)->None:
        data: dict = dict()
        with open(joints_names_configs_path, 'r') as f:
            data = json.load(f)
        self.guides_hik_map:dict = data.get('guides_to_hik_map')
        self.hik_sides_map:dict = data.get('hik_sides_map')
        names:list = [i
                      for i in list(data.keys())
                      if '_map' not in i
                      ]
        self._config_names = names

    def read_joints_names(self, specifier_key:str='default')->None:
        #TODO: add an optionVar group to store this information for next spawn
        # and automatically apply it at init time
        data:dict = dict()
        with open(joints_names_configs_path, 'r') as f:
            data = json.load(f)
        self.joints_names_config = data.get(specifier_key)
        self.map_joints_to_hik_names(self.joints_names_config)

    def map_joints_to_hik_names(self, joints_data:dict)->None:
        guides_to_joint:dict = joints_data.get('guides_to_joint_map')

        guides_to_hik:dict = self.guides_hik_map
        self.hik_to_joints_map:dict = {
            v:guides_to_hik.get(k)
            for k, v in guides_to_joint.items()
            if guides_to_hik.get(k)
        }

    def build_ui(self)->None:
        axis_up_panel, axis_up_lbl, y_radio, z_radio = cw.world_axis_widgets()
        self.widgets_dict['axis_up_label'] = axis_up_lbl
        self.widgets_dict['Y'] = y_radio
        self.widgets_dict['Z'] = z_radio
        self.set_axis_text()
        self.widgets_dict[self.up_axis.upper()].setChecked(True)
        self.centralWidget().layout().addWidget(axis_up_panel)

        self.build_guides_tools_ui()

        self.build_joints_tools_ui()

        self.build_posing_tools_ui()

        guides_widget:CollapsibleWidgetContainer = CollapsibleWidgetContainer('Skeleton Shape Guides',
                                                                              header_bkg_color=[71,170,181])
        guides_widget.collapseWidget(True)
        self.widgets_in_splitter.append(guides_widget)
        self.widgets_dict['guides_tools'] = guides_widget
        #self.centralWidget().layout().addWidget(guides_widget)

        joints_widget:CollapsibleWidgetContainer = CollapsibleWidgetContainer('Skeleton Joints Tools',
                                                                              header_bkg_color=[224,109,65])
        joints_widget.collapseWidget(True)
        self.widgets_in_splitter.append(joints_widget)
        self.widgets_dict['joints_tools'] = joints_widget

        posing_widget: CollapsibleWidgetContainer = CollapsibleWidgetContainer('Posing Tools',
                                                                               header_bkg_color=[95,172,135])
        posing_widget.collapseWidget(True)
        self.widgets_in_splitter.append(posing_widget)
        self.widgets_dict['pose_tools'] = posing_widget


        root_panel_splitter = cw.create_splitter(self.widgets_in_splitter)
        self.centralWidget().layout().addWidget(root_panel_splitter)

    def build_guides_tools_ui(self):

        guides_lists_wid:GuidesLists = GuidesLists()
        self.widgets_dict.update(guides_lists_wid.widgets_dict)
        guides_lists_wid.tooltips_path = tooltips_path
        guides_lists_wid.multi_joints_data = self.input_names[list(self.input_names.keys())[-1]]
        guides_lists_wid.category_list_add_data(list(self.input_names.keys())[:-1])
        guides_lists_wid.category_members_add_data(self.input_names)

        preset_panel, preset_combo, load_preset_btn, save_preset_btn = cw.guides_presets_widget()
        preset_combo.addItems(list(self.guides_presets.keys()))

        (reorient_panel, primary_x_radio, primary_y_radio, primary_z_radio,
         secondary_x_radio, secondary_y_radio, secondary_z_radio,
         world_x_radio, world_y_radio, world_z_radio, world_dir_combo, orient_btn, mirror_dir_combo, mirror_btn) = cw.reorient_selected_guides_widget()

        snap_panel, snap_selected_btn, attach_selected_btn = cw.attach_appendages_to_limb_widget()

        template_panel, save_templ_btn, load_templ_btn = cw.guides_template_file_widget()

        self.widgets_dict['guides_lists'] = guides_lists_wid
        self.widgets_dict['guides_preset_panel'] = preset_panel
        self.widgets_dict['guides_preset_combo'] = preset_combo
        self.widgets_dict['guides_load_preset_btn'] = load_preset_btn
        self.widgets_dict['guides_save_preset_btn'] = save_preset_btn
        self.widgets_dict['reorient_panel'] = reorient_panel
        self.widgets_dict['primary_x_radio'] = primary_x_radio
        self.widgets_dict['primary_y_radio'] = primary_y_radio
        self.widgets_dict['primary_z_radio'] = primary_z_radio
        self.widgets_dict['secondary_x_radio'] = secondary_x_radio
        self.widgets_dict['secondary_y_radio'] = secondary_y_radio
        self.widgets_dict['secondary_z_radio'] = secondary_z_radio
        self.widgets_dict['world_x_radio'] = world_x_radio
        self.widgets_dict['world_y_radio'] = world_y_radio
        self.widgets_dict['world_z_radio'] = world_z_radio
        self.widgets_dict['world_direction'] = world_dir_combo
        self.widgets_dict['orient_btn'] = orient_btn
        self.widgets_dict['mirror_btn'] = mirror_btn
        self.widgets_dict['mirror_direction'] = mirror_dir_combo
        self.widgets_dict['snap_panel'] = snap_panel
        self.widgets_dict['snap_selected'] = snap_selected_btn
        self.widgets_dict['attach_selected'] = attach_selected_btn
        self.widgets_dict['template_panel'] = template_panel
        self.widgets_dict['save_templ_btn'] = save_templ_btn
        self.widgets_dict['load_templ_btn'] = load_templ_btn

    def build_joints_tools_ui(self):
        config_panel, config_combo = cw.config_selector_widget(self.configurations_names)

        root_panel, _, root_orient_selector, create_root_btn = cw.root_joint_options()
        root_panel.setMaximumHeight(50)

        build_skeleton_btn:QPushButton = QPushButton('Build Skeleton')

        twist_panel, number_spinbox, fraction_spinbox = cw.add_twist_joints_widget()

        update_panel, update_guides_btn, update_joints_btn, confirm_btn = cw.update_guides_from_joints_widget()

        skinning_panel, influences_number_slider, bind_to_combo, bind_method_combo, skin_method_combo, bind_btn = cw.skinning_panel_widget()

        self.widgets_dict['root_panel'] = root_panel
        self.widgets_dict['root_orient'] = root_orient_selector
        self.widgets_dict['create_root'] = create_root_btn
        self.widgets_dict['config_panel'] = config_panel
        self.widgets_dict['config_combo'] = config_combo
        self.widgets_dict['build_skeleton_btn'] = build_skeleton_btn
        self.widgets_dict['twist_panel'] = twist_panel
        self.widgets_dict['number_spinbox'] = number_spinbox
        self.widgets_dict['fraction_spinbox'] = fraction_spinbox
        self.widgets_dict['update_panel'] = update_panel
        self.widgets_dict['update_guides_btn'] = update_guides_btn
        self.widgets_dict['update_joints_btn'] = update_joints_btn
        self.widgets_dict['confirm_btn'] = confirm_btn
        self.widgets_dict['skinning_panel'] = skinning_panel
        self.widgets_dict['influences_number_slider'] = influences_number_slider
        self.widgets_dict['bind_to_combo'] = bind_to_combo
        self.widgets_dict['bind_method_combo'] = bind_method_combo
        self.widgets_dict['skin_method_combo'] = skin_method_combo
        self.widgets_dict['bind_btn'] = bind_btn

    def build_posing_tools_ui(self):
        hik_panel, hik_btn = cw.characterize_widget()

        posing_tools_wid:PosingSetup = PosingSetup(template=self.joints_names_config)
        self.widgets_dict.update(posing_tools_wid.widgets_dict)

        poses_list_wid:PosesListWidget = PosesListWidget(template=self.joints_names_config)
        self.widgets_dict.update(poses_list_wid.widgets_dict)

        self.widgets_dict['hik_panel'] = hik_panel
        self.widgets_dict['hik_btn'] = hik_btn
        self.widgets_dict['posing_tools_wid'] = posing_tools_wid
        self.widgets_dict['poses_list_wid'] = poses_list_wid

    def populate_guides_container_widget(self)->None:
        guides_widget:CollapsibleWidgetContainer = self.widgets_dict['guides_tools']
        guides_lists_wid:GuidesLists = self.widgets_dict['guides_lists']

        guides_widget.appendContent(cw.create_separator('Guides Setup'))

        guides_widget.appendContent(guides_lists_wid)

        guides_widget.appendContent(cw.create_separator('Guides Presets'))

        guides_widget.appendContent(self.widgets_dict['guides_preset_panel'])

        guides_widget.appendContent(cw.create_separator(label='Orientation'))

        guides_widget.appendContent(self.widgets_dict['reorient_panel'])

        guides_widget.appendContent(cw.create_separator(label='Appendages'))

        guides_widget.appendContent(self.widgets_dict['snap_panel'])

        guides_widget.appendContent(cw.create_separator(label='Templates'))

        guides_widget.appendContent(self.widgets_dict['template_panel'])

    def populate_joints_container_widget(self)->None:
        joints_widget:CollapsibleWidgetContainer = self.widgets_dict['joints_tools']

        joints_widget.appendContent(cw.create_separator('Skeleton Setup'))

        config_panel:QComboBox = self.widgets_dict['config_panel']
        joints_widget.appendContent(config_panel)

        build_skeleton_btn:QPushButton = self.widgets_dict['build_skeleton_btn']
        joints_widget.appendContent(build_skeleton_btn)

        root_panel:QWidget = self.widgets_dict['root_panel']
        joints_widget.appendContent(root_panel)

        twist_panel:QWidget = self.widgets_dict['twist_panel']
        joints_widget.appendContent(twist_panel)

        update_panel:QWidget = self.widgets_dict['update_panel']
        joints_widget.appendContent(update_panel)

        joints_widget.appendContent(cw.create_separator('Skinning'))

        skinning_panel:QWidget = self.widgets_dict['skinning_panel']
        joints_widget.appendContent(skinning_panel)

    def populate_posing_container_widget(self)->None:
        pose_widget: CollapsibleWidgetContainer = self.widgets_dict['pose_tools']

        pose_widget.appendContent(cw.create_separator(label='T-Pose Setup'))

        posing_tools_wid:PosingSetup = self.widgets_dict['posing_tools_wid']
        pose_widget.appendContent(posing_tools_wid)

        pose_widget.appendContent(cw.create_separator(label='Bind Poses'))

        poses_list_wid:PosesListWidget = self.widgets_dict['poses_list_wid']
        pose_widget.appendContent(poses_list_wid)

        pose_widget.appendContent(cw.create_separator(label='Human IK'))

        hik_panel:QWidget = self.widgets_dict['hik_panel']
        pose_widget.appendContent(hik_panel)

    def connect_widgets(self):
        y_radio:QRadioButton = self.widgets_dict['Y']
        y_radio.toggled.connect(self.toggle_axis_up)
        z_radio:QRadioButton = self.widgets_dict['Z']
        z_radio.toggled.connect(self.toggle_axis_up)

        create_root_btn:QPushButton = self.widgets_dict['create_root']
        create_root_btn.clicked.connect(self.setup_root_joint)

        orient_btn:QPushButton = self.widgets_dict['orient_btn']
        orient_btn.clicked.connect(lambda: su.reorient_selected_guides(
                                                                    (self.widgets_dict['primary_x_radio'],
                                                                    self.widgets_dict['primary_y_radio'],
                                                                    self.widgets_dict['primary_z_radio']),
                                                                    (self.widgets_dict['secondary_x_radio'],
                                                                    self.widgets_dict['secondary_y_radio'],
                                                                    self.widgets_dict['secondary_z_radio']),
                                                                    (self.widgets_dict['world_x_radio'],
                                                                    self.widgets_dict['world_y_radio'],
                                                                    self.widgets_dict['world_z_radio']),
                                                                    1.0 if self.widgets_dict['world_direction'].currentText() == "+" else -1.0,
                                                                ))
        mirror_btn:QPushButton = self.widgets_dict['mirror_btn']
        mirror_btn.clicked.connect(lambda: su.mirror_selected_guides(self.get_mirror_direction()))

        snap_selected_btn:QPushButton = self.widgets_dict['snap_selected']
        snap_selected_btn.clicked.connect(su.snap_appendages_guides_to_limbs)

        attach_selected_btn:QPushButton = self.widgets_dict['attach_selected']
        attach_selected_btn.clicked.connect(su.attach_appendages_guides_to_limbs)

        save_templ_btn:QPushButton = self.widgets_dict['save_templ_btn']
        save_templ_btn.clicked.connect(self.save_guides_template)

        load_templ_btn:QPushButton = self.widgets_dict['load_templ_btn']
        load_templ_btn.clicked.connect(self.load_guides_template)

        load_preset_btn:QPushButton = self.widgets_dict['guides_load_preset_btn']
        load_preset_btn.clicked.connect(self.load_guides_preset)

        save_preset_btn:QPushButton = self.widgets_dict['guides_save_preset_btn']
        save_preset_btn.clicked.connect(self.save_preset)

        config_combo:QComboBox = self.widgets_dict['config_combo']
        config_combo.currentIndexChanged.connect(lambda: self.read_joints_names(specifier_key=config_combo.currentText()))

        build_skeleton_btn: QPushButton = self.widgets_dict['build_skeleton_btn']
        build_skeleton_btn.clicked.connect(self.build_skeleton)

        number_spinbox:QSpinBox = self.widgets_dict['number_spinbox']
        number_spinbox.valueChanged.connect(self.add_twist_joints)

        fraction_spinbox:QDoubleSpinBox = self.widgets_dict['fraction_spinbox']
        fraction_spinbox.valueChanged.connect(self.add_twist_joints)

        update_guides_btn:QPushButton = self.widgets_dict['update_guides_btn']
        update_guides_btn.clicked.connect(self.update_guides_from_joints)

        update_joints_btn:QPushButton = self.widgets_dict['update_joints_btn']
        update_joints_btn.clicked.connect(lambda: self.update_guides_from_joints(True))

        confirm_btn:QPushButton = self.widgets_dict['confirm_btn']
        confirm_btn.clicked.connect(self.finish_guides_update)

        bind_btn:QPushButton = self.widgets_dict['bind_btn']
        bind_btn.clicked.connect(self.bind_skin)

        hik_btn:QPushButton = self.widgets_dict['hik_btn']
        hik_btn.clicked.connect(self.characterize_skeleton)

    def characterize_skeleton(self)->None:
        hik_id_map:dict = self.hik_joints_ids
        sides_map:dict = self.hik_sides_map
        skel_hik_map:dict = self.hik_to_joints_map
        template:dict = self.joints_names_config
        su.characterize_skeleton(hik_id_map, sides_map, skel_hik_map, template)


    def bind_skin(self)->None:
        influences_number_slider:QSlider = self.widgets_dict['influences_number_slider']
        bind_to_combo:QComboBox = self.widgets_dict['bind_to_combo']
        bind_method_combo:QComboBox = self.widgets_dict['bind_method_combo']
        skin_method_combo:QComboBox = self.widgets_dict['skin_method_combo']

        infl_num:int = influences_number_slider.value()
        bind_to:str = bind_to_combo.currentText()
        bind_method:int = bind_method_combo.currentIndex()
        skin_method:int = skin_method_combo.currentIndex()
        su.bind_skin(bind_to, infl_num, bind_method, skin_method)

    def update_guides_from_joints(self, invert:bool=False)->None:
        template:dict = self.joints_names_config
        guides_data:dict|None = su.get_all_guides_hierarchies()
        if not guides_data:
            return
        su.update_guides_to_joints_start(guides_data, template, invert)

    def finish_guides_update(self)->None:
        template: dict = self.joints_names_config
        su.update_guides_to_joints_end(template)

    def add_twist_joints(self)->None:
        number:int = self.widgets_dict['number_spinbox'].value()
        fraction:float = self.widgets_dict['fraction_spinbox'].value()
        su.add_twist_joints(number, fraction, self.joints_names_config)

    def build_skeleton(self)->None:
        guides_data:dict|None = su.get_all_guides_hierarchies()
        template:dict|None = self.joints_names_config
        su.build_skeleton_from_guides(guides_data, template)


    def save_guides_template(self)->None:
        data:dict|None = su.get_all_guides_hierarchies()
        if not data:
            return
        res:tuple|None = uiu.get_save_file_name(self,
                               'Save Guides Template File',
                               uiu.get_workspace_path(),
                               {'Guides Template File': ['guides']}
                               )
        if not res:
            return
        file_path:str = os.path.join(*res)
        if not file_path.endswith('.guides'):
            file_path += '.guides'

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_guides_preset(self)->None:
        preset_combo:QComboBox = self.widgets_dict['guides_preset_combo']
        data:dict = self.guides_presets.get(preset_combo.currentText())
        su.rebuild_guides_hierarchy(data)

    def load_guides_template(self):
        res:tuple|None = uiu.get_open_file_name(self,
                                                'Load Guides Template File',
                                                uiu.get_workspace_path(),
                                                {'Guides Template File': ['guides']}
                                                )
        if not res:
            return
        file_path:str = os.path.join(*res)
        data:dict = dict()
        with open(file_path, 'r') as f:
            data = json.load(f)
        su.rebuild_guides_hierarchy(data)

    def get_mirror_direction(self)->list:
        mirror_direction: list = [1, 1, 1]
        axis: int = self.widgets_dict['mirror_direction'].currentIndex()
        mirror_direction[axis] = -1.0
        return mirror_direction

    def setup_root_joint(self)->None:
        world_up:str = self.up_axis
        up:str = self.widgets_dict['root_orient'].currentText().split()[0].lower()
        root_name:str = self.joints_names_config.get('guides_to_joint_map', dict()).get('Root', '')
        root_jnt:str|None = su.get_root_joint(root_name)
        if root_jnt:
            # do all the reorienting taking into account possible skin clusters
            su.orient_root(root_jnt, up, world_up)
            return
        root_jnt = su.create_joint(root_name)
        su.orient_root(root_jnt, up, world_up)

    def toggle_axis_up(self)->None:
        up:str = 'y' if self.widgets_dict['Y'].isChecked() else 'z'
        if up == self.up_axis:
            return
        uiu.set_up_axis(up)

    def set_axis_text(self)->None:
        lbl = self.widgets_dict['axis_up_label']
        text:str = f'World Up Axis:'
        lbl.setText(text)

    def add_tool_tips(self)->None:
        tooltips:dict = dict()
        with open(tooltips_path, 'r') as f:
            tooltips = json.load(f)
        tool_tips_errors:list = list()
        for k, v in tooltips.items():
            if not v:
                continue
            try:
                wid:QWidget = self.widgets_dict[k]
                wid.setToolTip(v)
            except Exception as e:
                error:list = [f'Error at key: "{k}"', e.__repr__()]
                tool_tips_errors.append(error)
        if tool_tips_errors:
            import sys
            uiu.buildMsg(['INFO:', 'Some errors occurred while applying tool tips', 'See script editor for details.'],
                         ['yellow', 'blue'],
                         ['Arial', 14])
            for error in tool_tips_errors:
                line:str = '#### {}\n\n'.format("\n# ".join(error))
                sys.stdout.write(line)
            sys.stdout.flush()

    def dump_widgets_to_file_for_tool_tips(self)->None:
        uiu.dump_widgets_to_file_for_tool_tips(self.widgets_dict, tooltips_path)


    @classmethod
    def load_window(cls)->QMainWindow:
        global skel_win
        try:
            skel_win.close()
            skel_win.deleteLater()
        except AttributeError as e:
            skel_win = None
        skel_win = cls()
        skel_win.show()
        return skel_win