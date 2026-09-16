import os
import maya.cmds as mc
import maya.mel as mel
import maya.utils

debug:bool = False
reload_str:str = 'from importlib import reload;' if debug else ''
module_reload:str = 'reload({mod_name});' if debug else ''
def create_menu():
    main_win = mel.eval('$mainWindow = $gMainWindow')

    menu_obj = 'O3DETools'
    menu_lbl = 'O3DE Tools'

    if mc.menu(menu_obj, label=menu_lbl, exists=True, parent=main_win):
        mc.deleteUI(mc.menu(menu_obj, e=True, deleteAllItems=True))

    o3de_tools = mc.menu(menu_obj, label=menu_lbl, parent=main_win, tearOff=False)
    mc.menuItem(label='FBX Export', subMenu=False, parent=o3de_tools, tearOff=False,
                command="{}import FBX_Exporter.ExporterUI as ui;{}ui.FbxExportUI.load_window()".format(reload_str, module_reload.format(mod_name='ui')))

    mc.menuItem(label='Skeleton Builder', subMenu=False, parent=o3de_tools, tearOff=False,
                command="{}import SkeletonBuilder.BuilderUI as bld;{}bld.SkeletonBuilderUI.load_window()".format(reload_str, module_reload.format(mod_name='bld')))


maya.utils.executeDeferred(create_menu)