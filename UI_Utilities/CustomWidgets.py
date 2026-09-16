from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import UI_Utilities.UI_Utils as wf
import UI_Utilities.SkeletonUtils as su

class CollapsibleWidgetContainer(QWidget):
    layouts = {
        'vertical' :[QVBoxLayout, QBoxLayout.TopToBottom],
        'horizontal' :[QHBoxLayout, QBoxLayout.LeftToRight],
        'grid' :[QGridLayout, QBoxLayout.LeftToRight]
    }
    collapseStatusChanged = Signal(bool)


    def __init__(self, label_text,
                 orientation='vertical',
                 header_bkg_color = [0.55 ,0.55 ,0.55],
                 header_text_color = [0.0 ,0.0 ,0.0],
                 font = ['Arial', 10],
                 scroll:bool=True,
                 *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.scrollable = scroll
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setContentsMargins(0 ,0 ,0 ,0)
        self.label = QLabel(label_text)
        self.label.setFont(QFont(font[0], font[1]))
        self.label.setFixedHeight(20)

        self.collapsed = False

        open_ = getattr(QStyle, 'SP_TitleBarUnshadeButton')
        self.open_icon = self.style().standardIcon(open_)

        close_ = getattr(QStyle, 'SP_MediaPlay')
        self.close_icon = self.style().standardIcon(close_)

        self.collapse_btn = QPushButton()
        self.collapse_btn.setIcon(self.open_icon)
        self.collapse_btn.setFixedSize(20 ,20)
        self.collapse_btn.clicked.connect(self.toggleCollapse)
        self.collapse_btn.setObjectName('NORESIZE')

        top_lyt = QHBoxLayout()
        top_lyt.addWidget(self.collapse_btn)
        top_lyt.addWidget(self.label)

        self.layout().addLayout(top_lyt)
        self.ui_container = QWidget()
        self.visibility_widget = self.ui_container
        if scroll:
            scroll_area = QScrollArea()
            scroll_area.setWidget(self.ui_container)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.layout().addWidget(scroll_area)
            self.visibility_widget = scroll_area

        self.layout().addWidget(self.visibility_widget)
        self.ui_container.setLayout(self.layouts.get(orientation)[0]())
        self.ui_container.layout().setAlignment(Qt.AlignTop)

        wf.setWidgetPalette(self.collapse_btn,
                            header_bkg_color
                            )
        wf.setWidgetPalette(self.label,
                            header_bkg_color,
                            text_color=header_text_color
                            )
        self.icons_map = {
            True: self.close_icon,
            False: self.open_icon
        }

    def uiOrientation(self, orientation='vertical'):
        self.ui_container.layout().setDirection(self.layouts.get(orientation)[1])

    def toggleCollapse(self):
        vis = self.visibility_widget.isVisible()
        self.collapseWidget(vis)

    def collapseWidget(self, visible):
        self.visibility_widget.setHidden(visible)
        self.collapsed = visible
        self.collapse_btn.setIcon(self.icons_map.get(visible))
        self.collapseStatusChanged.emit(True)

    def appendContent(self, content):
        if isinstance(content, QLayout):
            self.ui_container.layout().addLayout(content)

        if isinstance(content, QWidget):
            self.ui_container.layout().addWidget(content)

    def insertContentAtIndex(self, content, index):
        if isinstance(content, QLayout):
            self.ui_container.layout().insertLayout(index, content)

        if isinstance(content, QWidget):
            self.ui_container.layout().insertWidget(index, content)

    def addStretch(self)->None:
        self.ui_container.layout().addStretch()


class GuidesLists(QWidget):

    unsided_sections:list = ['center', 'chain']
    _tooltips_path:str = str()

    def __init__(self, parent=None)->None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.splitter:QSplitter = QSplitter()
        self.layout().addWidget(self.splitter)

        self.widgets_dict: dict = dict()
        self.components_list:list = list()
        self.guides_list:list = list()

        self.category_list_wid:QListWidget = QListWidget()
        self.category_list_wid.setMaximumWidth(80)
        self.category_members_wid:QWidget = QWidget()
        self.category_members_wid.setLayout(QVBoxLayout())
        self.category_numbers_wid:QListWidget = QListWidget()
        self.category_numbers_wid.clicked.connect(self.category_numbers_item_clicked)
        self.category_numbers_wid.setMaximumWidth(80)

        self.widgets_dict['guides_list_category_list_wid'] = self.category_list_wid
        self.widgets_dict['guides_list_category_members_wid'] = self.category_members_wid
        self.widgets_dict['guides_list_category_numbers_wid'] = self.category_numbers_wid

        self.splitter.addWidget(self.category_list_wid)
        self.splitter.addWidget(self.category_members_wid)
        self.splitter.addWidget(self.category_numbers_wid)

        self.list_to_members:dict = dict()

        self.multi_joints_data:dict = dict()
        self.multi_joints_names:list = list()

        self.sides_wid:QWidget = QWidget()
        self.sides_wid.setLayout(QHBoxLayout())
        self.sides_wid.setEnabled(False)
        left_radio:QRadioButton = QRadioButton('Left')
        right_radio:QRadioButton = QRadioButton('Right')

        self.widgets_dict['guides_list_sides_wid'] = self.sides_wid
        self.widgets_dict['guides_list_left_radio'] = left_radio
        self.widgets_dict['guides_list_right_radio'] = right_radio

        left_radio.setChecked(True)

        self.guides_spacing_spin:QDoubleSpinBox = QDoubleSpinBox()
        self.guides_spacing_spin.setMinimum(0.01)
        self.guides_spacing_spin.setSingleStep(1.0)
        self.guides_spacing_spin.setValue(15.0)
        self.guides_spacing_spin.setSuffix(' cm')

        self.widgets_dict['guides_list_guides_spacing_spin'] = self.guides_spacing_spin

        self.sides_wid.layout().addWidget(left_radio)
        self.sides_wid.layout().addWidget(right_radio)
        self.sides_wid.layout().addStretch()
        self.sides_wid.layout().addWidget(self.guides_spacing_spin)
        sides_spacing_lyt:QHBoxLayout = QHBoxLayout()
        sides_spacing_lyt.addWidget(self.sides_wid)
        sides_spacing_lyt.addWidget(QLabel('Spacing:'))
        sides_spacing_lyt.addWidget(self.guides_spacing_spin)
        self.layout().addLayout(sides_spacing_lyt)


        create_btn:QPushButton = QPushButton('Create Guides')
        create_btn.clicked.connect(self.create_section_guides)
        self.layout().addWidget(create_btn)

        self.widgets_dict['guides_list_create_btn'] = create_btn

        snapping_section_lyt:QHBoxLayout = QHBoxLayout()

        components_btn:QPushButton = QPushButton('Store Components')
        components_btn.clicked.connect(self.store_components_list)
        guide_btn:QPushButton = QPushButton('Store Guide')
        guide_btn.clicked.connect(self.store_guides_list)
        do_it_btn:QPushButton = QPushButton('Snap Guide Position')
        do_it_btn.clicked.connect(self.perform_snap_to_selection)
        do_it_rot_btn:QPushButton = QPushButton('Snap Guide Rotation')
        do_it_rot_btn.clicked.connect(self.perform_copy_rotation_to_selection)
        reset_btn:QPushButton = QPushButton('Reset')
        reset_btn.clicked.connect(self.reset_guide_snap_tool)

        self.widgets_dict['guides_list_components_btn'] = components_btn
        self.widgets_dict['guides_list_guide_btn'] = guide_btn
        self.widgets_dict['guides_list_do_it_btn'] = do_it_btn
        self.widgets_dict['guides_list_do_it_rot_btn'] = do_it_rot_btn
        self.widgets_dict['guides_list_reset_btn'] = reset_btn

        snapping_section_lyt.addWidget(components_btn)
        snapping_section_lyt.addWidget(guide_btn)
        snapping_section_lyt.addStretch()
        snapping_section_lyt.addWidget(do_it_btn)
        snapping_section_lyt.addWidget(do_it_rot_btn)
        snapping_section_lyt.addWidget(reset_btn)

        self.layout().addLayout(snapping_section_lyt)

    @property
    def tooltips_path(self):
        return self._tooltips_path

    @tooltips_path.setter
    def tooltips_path(self,value):
        self._tooltips_path = value

    def store_components_list(self)->None:
        self.components_list = wf.list_selected_items(vtx_convert=True)
        wf.buildMsg(['Selection Components Stored'],
                    ['blue'],
                    ['Arial', 12])

    def store_guides_list(self)->None:
        self.guides_list = wf.list_selected_items(vtx_convert=False)
        wf.buildMsg(['Guides Stored'],
                    ['blue'],
                    ['Arial', 12])

    def reset_guide_snap_tool(self)->None:
        self.components_list.clear()
        self.guides_list.clear()
        wf.buildMsg(['Guide Snapping tool reset.'],
                    ['blue'],
                    ['Arial', 12])

    def perform_snap_to_selection(self)->None:
        if (not self.components_list) or (not self.guides_list):
            return
        su.snap_guides_to_components_center(self.components_list, self.guides_list)

    def perform_copy_rotation_to_selection(self)->None:
        if (not self.components_list) or (not self.guides_list):
            return
        su.rotate_guides_to_component(self.components_list, self.guides_list)

    def create_section_guides(self):
        items: list = self.category_list_wid.selectedItems()
        if not items:
            return
        item_name = items[0].text()
        section_dict:dict = dict()
        container_wid:QWidget|None = self.list_to_members.get(item_name)
        if not container_wid:
            return
        children:list = [i
                         for i in container_wid.children()
                         if not isinstance(i, QLayout)
                         ]
        for child in children:
            grand_children:list = child.children()
            ckbx:QCheckBox|None = None
            spin:QSpinBox|None = None
            for gc in grand_children:
                if isinstance(gc, QCheckBox):
                    ckbx = gc
                if isinstance(gc, QSpinBox):
                    spin = gc

            name:str = ckbx.text()
            enabled:bool = ckbx.isChecked()
            number:int = 1
            if spin:
                number = spin.value()
            number = number if enabled else 0
            if enabled:
                section_dict[name] = number

        left_side:bool|None = None
        if self.sides_wid.isEnabled():
            sides_wid_children:list = self.sides_wid.children()
            for ch in sides_wid_children:
                if isinstance(ch, QRadioButton):
                    if 'left' in ch.text().lower():
                        left_side = ch.isChecked()
                        break

        su.create_section_guides(item_name, section_dict, wf.get_up_axis(), left_side, self.guides_spacing_spin.value())
        self.category_numbers_add_data(wf.get_existing_section_guides(item_name))

    def category_list_add_data(self, data:list)->None:
        self.category_list_wid.clear()
        self.category_list_wid.addItems(data)

    def category_members_add_data(self, data:dict)->None:

        for idx in range(self.category_list_wid.count()):
            item:QListWidgetItem = self.category_list_wid.item(idx)
            container_wid:QWidget = QWidget()
            container_wid.setLayout(QVBoxLayout())
            name:str = item.text()
            container_wid.setObjectName(f'{name}_container')
            self.list_to_members[name] = container_wid
            container_wid.setVisible(False)
            members:list = data.get(name)
            for m in members:
                member_wid:QWidget = wf.create_guides_list_widget(m, self.multi_joints_data)
                container_wid.layout().addWidget(member_wid)

        for container in self.list_to_members.values():
            self.category_members_wid.layout().addWidget(container)

        self.category_list_wid.itemClicked.connect(self.category_list_item_clicked)
        self.category_list_wid.itemClicked.connect(self.toggle_sidedness_radios)

    def category_list_item_clicked(self)->None:
        items:list = self.category_list_wid.selectedItems()
        if not items:
            return
        for idx in range(self.category_list_wid.count()):
            item: QListWidgetItem = self.category_list_wid.item(idx)
            cont:QWidget|None = self.list_to_members.get(item.text())
            if cont:
                cont.setVisible(False)
        item_name = items[0].text()
        container_wid:QWidget|None = self.list_to_members.get(item_name)
        if not container_wid:
            return
        container_wid.setVisible(True)
        self.category_numbers_add_data(wf.get_existing_section_guides(item_name))

    def get_all_category_numbers_list(self):
        out:dict = dict()
        for idx in range(self.category_list_wid.count()):
            section: str = self.category_list_wid.item(idx).text()
            existing_sections: list = wf.get_existing_section_guides(section)
            out[section] = existing_sections
        return out

    def category_numbers_item_clicked(self)->None:
        items:list = self.category_numbers_wid.selectedItems()
        if not items:
            return
        item:QListWidgetItem = items[0]
        data:str = item.data(3).fullPathName()
        if data.split('|')[-1] != item.text():
            item.setText(data.split('|')[-1])
            children:list = su.get_guides_hierarchy(data)
            children.remove(data)
            children_dags:list = wf.get_dag_paths(list(reversed(children)))
            start_num:int = 1
            if data[-1].isdigit():
                start_num = int(data[-1]) + 1
            for idx, dag in enumerate(children_dags):
                name:str = dag.partialPathName()
                split:str = name.split('_')[0]
                new_name:str = f'{split}_{start_num + idx}'
                wf.rename(dag.fullPathName(), new_name)

        wf.select_items([data])
        hierarchy:list = su.get_guides_hierarchy(data)
        container_wid: QWidget | None = self.list_to_members.get(self.category_list_wid.selectedItems()[0].text())
        if not container_wid:
            return
        wid_children:list = [i
                             for i in container_wid.children()
                             if not isinstance(i, QLayout)
                             ]
        for wid in wid_children:
            guide_name:str = wid.objectName().split('_')[0]
            in_hierarchy:list = [i for i in hierarchy
                                 if guide_name in i.split('|')[-1]
                                ]
            child_cont:list = [i
                               for i in wid.children()
                               if not isinstance(i, QLayout)
                               ]
            for child in child_cont:
                if isinstance(child, QCheckBox):
                    child.setChecked(bool(len(in_hierarchy)))
                if isinstance(child, QSpinBox):
                    child.setValue(len(in_hierarchy))

    def category_numbers_add_data(self, data:list):
        self.category_numbers_wid.clear()
        if not data:
            return
        self.category_numbers_wid.addItems([i.split('|')[-1] for i in data])
        dag_paths:list[om.MDagPath] = wf.get_dag_paths(data)
        for idx in range(self.category_numbers_wid.count()):
            item:QListWidgetItem = self.category_numbers_wid.item(idx)
            item.setData(3, dag_paths[idx])

    def toggle_sidedness_radios(self):
        enabled:bool = False
        selected:list = self.category_list_wid.selectedItems()
        if not selected:
            return
        item:QListWidgetItem = selected[0]
        section_name:str = item.text()
        if section_name not in self.unsided_sections:
            enabled = True
        self.sides_wid.setEnabled(enabled)

class PosingSetup(QWidget):
    def __init__(self, template:dict, parent=None):
        super().__init__(parent)
        self.widgets_dict:dict = dict()
        self.joints_names_config:dict = template
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.build_ui()
        self.populate_ui()
        self.connect_widgets()

    def build_ui(self)->None:
        refresh_btn:QPushButton = QPushButton()
        refresh_btn.setMaximumSize(20,20)
        pixmapi = getattr(QStyle, 'SP_BrowserReload')
        icon:QIcon = self.style().standardIcon(pixmapi)
        refresh_btn.setIcon(icon)

        joints_table:QTableWidget = QTableWidget()
        joints_table.setFixedWidth(300)
        joints_table.setColumnCount(2)
        joints_table.setHorizontalHeaderLabels(['Joint Name', 'Direction'])
        joints_table.setShowGrid(True)
        joints_table.setColumnWidth(0, joints_table.width()-100)
        joints_table.setColumnWidth(1, 100)

        make_t_pose_btn:QPushButton = QPushButton('Make T-Pose')
        save_t_pose_btn:QPushButton = QPushButton('Save T-Pose')
        save_bind_pose_btn:QPushButton = QPushButton('Save Bind Pose')

        self.widgets_dict['posing_tool_refresh_btn'] = refresh_btn
        self.widgets_dict['posing_tool_joints_table'] = joints_table
        self.widgets_dict['posing_tool_make_t_pose_btn'] = make_t_pose_btn
        self.widgets_dict['posing_tool_save_t_pose_btn'] = save_t_pose_btn
        self.widgets_dict['posing_tool_save_bind_pose_btn'] = save_bind_pose_btn

    def populate_ui(self)->None:
        refresh_btn:QPushButton = self.widgets_dict['posing_tool_refresh_btn']
        self.layout().addWidget(refresh_btn)

        joints_table:QTableWidget = self.widgets_dict['posing_tool_joints_table']
        self.layout().addWidget(joints_table)

        make_t_pose_btn:QPushButton = self.widgets_dict['posing_tool_make_t_pose_btn']
        self.layout().addWidget(make_t_pose_btn)

        save_btns_lyt:QHBoxLayout = QHBoxLayout()
        self.layout().addLayout(save_btns_lyt)

        save_t_pose_btn:QPushButton = self.widgets_dict['posing_tool_save_t_pose_btn']
        save_btns_lyt.addWidget(save_t_pose_btn)

        save_bind_pose_btn:QPushButton = self.widgets_dict['posing_tool_save_bind_pose_btn']
        save_btns_lyt.addWidget(save_bind_pose_btn)

    def connect_widgets(self)->None:
        refresh_btn:QPushButton = self.widgets_dict['posing_tool_refresh_btn']
        refresh_btn.clicked.connect(self.populate_table)

        make_t_pose_btn: QPushButton = self.widgets_dict['posing_tool_make_t_pose_btn']
        make_t_pose_btn.clicked.connect(self.make_t_pose)

        save_t_pose_btn:QPushButton = self.widgets_dict['posing_tool_save_t_pose_btn']
        save_t_pose_btn.clicked.connect(lambda: su.create_update_bind_pose(self.joints_names_config.get('guides_to_joint_map').get('Root'), 'T_Pose'))
        save_bind_pose_btn:QPushButton = self.widgets_dict['posing_tool_save_bind_pose_btn']
        save_bind_pose_btn.clicked.connect(lambda: su.create_update_bind_pose(self.joints_names_config.get('guides_to_joint_map').get('Root'), 'Bind_Pose'))

    def populate_table(self)->None:
        table:QTableWidget = self.widgets_dict['posing_tool_joints_table']
        table.clearContents()
        joints:list = su.get_selected_joints()
        joints_names:list = [i.split('|')[-1] for i in joints]
        table.setRowCount(len(joints))

        directions:list = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
        vectors:list = [
            [1,0,0], [0,1,0], [0,0,1],
            [-1,0,0], [0,-1,0], [0,0,-1]
                        ]
        for joint, joint_name in zip(joints, joints_names):
            item:QTableWidgetItem = QTableWidgetItem()
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(0, joint_name)
            item.setData(1, joint)
            dir_combo:QComboBox = QComboBox()
            for d, v in zip(directions, vectors):
                dir_combo.addItem(d)
                dir_combo.setItemData(vectors.index(v), v, 1)
            row:int = joints.index(joint)
            table.setRowHeight(row, 20)
            table.setItem(row, 0, item)
            table.setCellWidget(row, 1, dir_combo)

    def make_t_pose(self)->None:
        # parse the data from the table:
        table:QTableWidget = self.widgets_dict['posing_tool_joints_table']
        actuator_list:list = list()
        for row in range(table.rowCount()):
            item:QTableWidgetItem = table.item(row, 0)
            combo:QComboBox = table.cellWidget(row, 1)
            joint:str = item.data(1)
            vector:str = combo.itemData(combo.currentIndex(), 1)
            actuator_list.append([joint, vector])

        actuator_dict:dict = dict(actuator_list)
        su.make_t_pose(actuator_dict)

class PosesListWidget(QWidget):
    _default_poses:QColor = QColor(255,0,0)
    _our_poses:QColor = QColor(0,255,0)

    def __init__(self, template:dict, parent=None):
        super().__init__(parent)
        self.widgets_dict:dict = dict()

        self.table_items_dict:dict = dict()

        self.joints_names_config:dict = template

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.build_ui()
        self.populate_widget()
        self.connect_button()



    def build_ui(self)->None:
        refresh_btn: QPushButton = QPushButton()
        refresh_btn.setMaximumSize(20, 20)
        pixmapi = getattr(QStyle, 'SP_BrowserReload')
        icon: QIcon = self.style().standardIcon(pixmapi)
        refresh_btn.setIcon(icon)

        poses_table:QTableWidget = QTableWidget()
        poses_table.setFixedWidth(300)
        poses_table.setColumnCount(2)
        poses_table.setColumnWidth(0, int(poses_table.width()*0.75))
        poses_table.setColumnWidth(1, int(poses_table.width()*0.2))
        poses_table.setHorizontalHeaderLabels(['Pose Name', 'Active'])
        poses_table.setShowGrid(True)

        go_to_bindpose_btn:QPushButton = QPushButton('Go To Bind Pose')

        self.widgets_dict['pose_list_refresh_btn'] = refresh_btn
        self.widgets_dict['pose_list_table'] = poses_table
        self.widgets_dict['pose_list_go_to_bindpose_btn'] = go_to_bindpose_btn

    def populate_widget(self)->None:
        refresh_btn:QPushButton = self.widgets_dict['pose_list_refresh_btn']
        poses_table:QTableWidget = self.widgets_dict['pose_list_table']
        go_to_bindpose_btn:QPushButton = self.widgets_dict['pose_list_go_to_bindpose_btn']

        self.layout().addWidget(refresh_btn)
        self.layout().addWidget(poses_table)
        self.layout().addWidget(go_to_bindpose_btn)

    def populate_table(self, joints:list)->None:
        table:QTableWidget = self.widgets_dict['pose_list_table']
        table.clearContents()
        self.table_items_dict.clear()
        bind_poses:list = su.get_all_bind_poses(joints)
        if not bind_poses:
            return
        poses_with_status:list = [(i, {
                                        'attribute_data': [wf.get_attribute(i, 'bindPose'), wf.attribute_exists(i, 'poseType')]
                                        }
                                   )
                                  for i in bind_poses
                                  ]
        self.table_items_dict = dict(poses_with_status)
        table.setRowCount(len(bind_poses))
        count:int = 0
        for node, data in self.table_items_dict.items():
            active, our_bind = data.get('attribute_data')
            main_item:QTableWidgetItem = QTableWidgetItem()
            main_item.setText(node)
            main_item.setForeground(QBrush(self._our_poses if our_bind else self._default_poses))
            main_item.setFlags(Qt.ItemIsEnabled)
            main_item.setToolTip('Posing tool generated pose.' if our_bind else 'Generic bind pose from Maya.')
            table.setItem(count, 0, main_item)

            active_checkbox:QCheckBox = QCheckBox()
            active_checkbox.setChecked(active)
            self.connect_checkbox_toggle(active_checkbox)
            data['checkbox'] = active_checkbox
            table.setCellWidget(count, 1, active_checkbox)
            count += 1

    def refresh_table(self)->None:
        all_joints:list = su.get_all_joints_under_root(self.joints_names_config.get('guides_to_joint_map').get('Root'))
        self.populate_table(all_joints)

    def connect_button(self)->None:
        refresh_btn:QPushButton = self.widgets_dict['pose_list_refresh_btn']
        refresh_btn.clicked.connect(self.refresh_table)

        go_to_bindpose_btn: QPushButton = self.widgets_dict['pose_list_go_to_bindpose_btn']
        go_to_bindpose_btn.clicked.connect(lambda: su.go_to_bind_pose(self.joints_names_config.get('guides_to_joint_map').get('Root')))

    def connect_checkbox_toggle(self, checkbox:QCheckBox)->None:
        checkbox.clicked.connect(lambda: self.ensure_only_one_active_bind_pose(checkbox))


    def ensure_only_one_active_bind_pose(self, checkbox:QCheckBox)->None:
        for item, data in self.table_items_dict.items():
            stored:QCheckBox = data.get('checkbox')
            if stored == checkbox:
                checkbox.setChecked(True)
                # get the bindPose node to reflect the checkbox state here
                wf.set_attribute(item, 'bindPose', checkbox.isChecked())
                pass
            else:
                stored.setChecked(False)
                wf.set_attribute(item, 'bindPose', stored.isChecked())
                # get the corresponding bindPose node to reflect the state
