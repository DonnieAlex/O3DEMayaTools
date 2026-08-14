import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import os

from contextlib import contextmanager

@contextmanager
def undo_queue(perform_undo:bool=True):
    mc.undoInfo(openChunk=True)
    yield
    mc.undoInfo(closeChunk=True)
    if perform_undo:
        mc.undo()

def export_selection(
                    selection:list,
                    folder_path:str,
                    file_name:str,
                    fbx_type:str,
                    up_axis:str,
                    triangulate:bool,
                    include_anim:bool,
                    start_frame:int,
                    end_frame:int,
                    as_takes:bool,
                    clips_data:list|None,
                    embed_media:bool,

                    convert_world_axis_animation:bool,
                    anim_only:bool,
                    strip_namespaces:bool,
                    add_obj_name:str|None)->None:

    set_fbx_params(include_anim=include_anim, start_frame=start_frame, end_frame=end_frame,
                   triangulate=triangulate,fbx_type=fbx_type,
                   up_axis=up_axis, embed_media=embed_media, convert_world_axis_animation=convert_world_axis_animation)
    if add_obj_name:
        file_path:str = build_fbx_file_path(folder_path, file_name, add_obj_name)
    else:
        file_path:str = build_fbx_file_path(folder_path, file_name, None)

    mc.select(selection, replace=True)

    if as_takes:
        fbx_export_as_takes(file_path, clips_data)
    else:
        fbx_export(file_path)


def get_exportable_selection()->list:
    selection:list = mc.ls(selection=True)
    selection = [
        i for i in selection
        if mc.listRelatives(i, shapes=True, fullPath=True) is not None
        if mc.nodeType(mc.listRelatives(i, shapes=True, fullPath=True)[0]) == 'mesh'
    ]
    return selection

def get_skin_cluster(obj:str)->list|None:
    skin:list|None = mc.ls(mc.listHistory(obj), type='skinCluster') or None
    return skin

def get_blendshapes(obj:str)->list|None:
    bs:list|None = mc.ls(mc.listHistory(obj), type='blendShape') or None
    return bs

def get_joints_from_skin(skin:str)->list | None:
    if not skin:
        return None
    res:list = mc.skinCluster(skin, query=True, influence=True)
    if res:
        res = mc.ls(res, long=True)
        # return them in hierarchical order
        res.sort(key=lambda x: len(x.split('|')))
    return res

def get_skel_root(joints:list|None)->str|None:
    if not joints:
        return None
    ancestor:str = joints[0]
    parent:list | None = mc.listRelatives(ancestor, parent=True, fullPath=True)
    root:str = ancestor
    cycles=0
    while parent:
        if mc.nodeType(parent[0]) == 'joint':
            root=parent[0]
            parent = mc.listRelatives(parent[0], parent=True, fullPath=True)
        else: break
        cycles+=1

        if cycles > 300:
            break
    return root

def get_hierarchy_from_root(root:str)->list:
    hierarchy:list = mc.ls(
        mc.listRelatives(root, allDescendents=True, fullPath=True),
        type='joint',
        long=True
    )
    hierarchy.append(root)
    return hierarchy

def enable_plugins()->None:
    loaded: list = mc.pluginInfo(q=True, ls=True, l=True)
    needed: list = [
        'timeSliderBookmark',
        'fbxmaya'
    ]
    for item in needed:
        if not item in loaded:
            mc.loadPlugin(item, quiet=True)

def go_to_bind_pose():
    mc.GoToBindPose()

def remove_constraints(hierarchy_root:str)->None:
    """to be used in conjunction with undo_queue() context manager"""
    hierarchy:list = mc.listRelatives(hierarchy_root, allDescendents=True, fullPath=True) or list()
    if not hierarchy:
        return
    constraints:list = list()
    for child in hierarchy:
        if 'constrain' in mc.nodeType(child).lower():
            constraints.append(child)
    if constraints:
        mc.delete(constraints)
    
def build_fbx_file_path(file_path:str, file_name:str, add_obj_name:str|None)->str:
    if add_obj_name:
        file_name = file_name.replace('.fbx', '')
        file_name += f'_{add_obj_name}.fbx'

    return os.path.join(file_path, file_name)

def fbx_export(file_save_path:str)->None:
    mel.eval('FBXExport -f "{}" -s;'.format(file_save_path))

def set_fbx_params(include_anim:bool, start_frame:int, end_frame:int,
                   triangulate:bool, fbx_type:str, up_axis:str, embed_media:bool,
                   convert_world_axis_animation:bool)->None:

    mel.eval('FBXExportBakeComplexAnimation -v {};'.format(str(include_anim).lower()))
    if include_anim:
        mel.eval('FBXExportBakeComplexStart -v {};'.format(start_frame))
        mel.eval('FBXExportBakeComplexEnd -v {};'.format(end_frame))

    mel.eval('FBXExportTriangulate -v {};'.format(str(triangulate).lower()))

    # hard-coded settings that are always desirable to force
    mel.eval('FBXExportSkins -v true;')
    mel.eval('FBXExportShapes -v true;')
    mel.eval('FBXExportSkeletonDefinitions -v true;')
    mel.eval('FBXExportSmoothMesh -v true;')
    mel.eval('FBXExportHardEdges -v false;')
    mel.eval('FBXExportInputConnections -v false;')
    mel.eval('FBXExportSmoothingGroups -v true;')
    mel.eval('FBXExportConstraints -v false;')
    mel.eval('FBXExportIncludeChildren -v true')
    mel.eval('FBXExportInstances -v true')
    mel.eval('FBXExportScaleFactor 1.0;')

    mel.eval('FBXExportReferencedAssetsContent -v true;')
    mel.eval('FBXExportLights -v false;')
    mel.eval('FBXExportCameras -v false;')

    mel.eval('FBXExportTangents -v false;')
    mel.eval('FBXExportEmbeddedTextures -v {};'.format(str(embed_media).lower()))
    # hard-coded settings end ^^^^^^^^^
    # file format setting, binary or Ascii?
    mel.eval('FBXExportInAscii -v {};'.format(str(True if fbx_type == 'Ascii' else False).lower()))
    # exported scene world up axis
    mel.eval('FBXExportUpAxis {};'.format(up_axis.lower()))
    # we're converting all animation curves on the spot to conform to the new world axis coordinates
    # this setting is not exposed in the regular FBX export UI and therefore not normally accessible
    # default behavior is usually addFBXRoot which adds a root group node that gets rotated to eat up
    # the transformation change. engines do not really like that.
    if convert_world_axis_animation:
        mel.eval('FBXExportAxisConversionMethod "convertAnimation";')
    #FBXPushSettings ?

def fbx_export(file_path:str)->None:
    mel.eval(f'FBXExport -f "{file_path}" -s;')


def fbx_export_as_takes(file_path:str, clips:list)->None:
    for clip in clips:
        mel.eval(
            'FBXExportSplitAnimationIntoTakes -v {} {} {}'.format(clip.get('clip_name'), clip.get('clip_start_frame'), clip.get('clip_end_frame')))
    #perform export
    fbx_export(file_path)
    #mel.eval(f'FBXExport -f "{file_path}" -s;')
    # the accumulator doesn't clear itself automatically across different invocations of the FBXExport method,
    # so we manually clear it now, ready for the next round.
    mel.eval('FBXExportSplitAnimationIntoTakes -c')

def selection_includes_skins(input_selection:list)->bool:
    skins:list = mc.ls(input_selection, type='skinCluster')
    return bool(len(skins))

def selection_includes_blendshapes(input_selection:list)->bool:
    bs:list = mc.ls(input_selection, type='blendShape')
    return bool(len(bs))

def get_dag_paths(objs:list)->list[om.MDagPath]:
    dag_paths:list[om.MDagPath] = list()
    selList = om.MSelectionList()
    for obj in objs:
        selList.add(obj)
    it:om.MItSelectionList = om.MItSelectionList(selList)
    while not it.isDone():
        dag:om.MDagPath = om.MDagPath()
        it.getDagPath(dag)
        dag_paths.append(dag)
        it.next()
    return dag_paths

def get_paths_from_dags(dag_paths:list[om.MDagPath])->list[str]:
    return [i.fullPathName() for i in dag_paths]

def parent_to_world(objs:list[str])->None:
    for obj in objs:
        if mc.objExists(obj):
            mc.parent(obj, world=True)

def to_center(objs:list[str])->None:
    for obj in objs:
        if mc.objExists(obj):
            mc.xform(obj, translation=(0,0,0), worldSpace=True)

def zero_rotation(objs:list[str])->None:
    for obj in objs:
        if mc.objExists(obj):
            mc.setAttr(f'{obj}.rotate', 0.0,0.0,0.0, type='double3')

def filter_selection_by_type(selection:list, typ:str)->list:
    in_list:list = mc.ls(selection, type=typ)
    out_list:list = list()
    if typ in ['mesh']: # leave an extendable checklist for possible future cases
        for obj in selection:
            shapes:list = mc.listRelatives(obj, shapes=True, fullPath=True)
            if shapes and mc.nodeType(shapes[0]) == 'mesh':
                out_list.append(obj)

    return out_list if len(out_list) else in_list

def select_list(selection:list)->None:
    mc.select(selection, replace=True)

def is_referenced(obj:str)->bool:
    return mc.referenceQuery(obj, isNodeReferenced=True)

def duplicate_special(input_meshes:list|None, input_joints:list|None)->tuple[list, list]:
    root:str = get_skel_root(input_joints)
    to_dup:list = list()
    if root:
        to_dup.append(root)
    if input_meshes:
        to_dup.extend(input_meshes)
    dups:list = mc.duplicate(to_dup, instanceLeaf=False, returnRootsOnly=True, upstreamNodes=True)

    out_meshes:list = list()
    out_joints:list = list()
    for d in dups:
        if mc.nodeType(d)=='joint':
            out_joints = mc.ls(mc.listRelatives(d, allDescendents=True, fullPath=True), type='joint')
            out_joints.append(get_skel_root(out_joints))
        else:
            out_meshes.append(d)
    if out_meshes:
        mc.parent(out_meshes, world=True)
    if out_joints:
        mc.parent(get_skel_root(out_joints), world=True)
    return out_meshes, out_joints

def delete_selection(selection:list)->None:
    mc.delete(selection)

def remove_namespaces()->None:
    mc.namespace(setNamespace=':')
    # name = mc.namespaceInfo(currentNamespace=True)
    namespaces:list = mc.namespaceInfo(listOnlyNamespaces=True,
                                  recurse=True,
                                  absoluteName=True)
    # remove the default namespaces that Maya uses internally
    if namespaces.count(':UI'): namespaces.remove(':UI')
    if namespaces.count(':shared'): namespaces.remove(':shared')
    if namespaces:
        namespaces.sort(key=lambda x: len(x.split(':')),
                        reverse=True)  # sort'em by most nested namespace to the closest to root
        for ns in namespaces:
            depNodes:list|None = mc.namespaceInfo(ns, listOnlyDependencyNodes=True, absoluteName=True)
            if depNodes is None:
                # namespace is empty
                try:
                    mc.namespace(removeNamespace=ns)
                except Exception:
                    pass
            else:
                mc.namespace(moveNamespace=(ns, ':'), force=True)
                mc.namespace(removeNamespace=ns, force=True)

def remove_namespaces_from_selection_list(selection:list)->list:
    out_list:list = list()
    for item in selection:
        item_split:list = item.split('|')
        new_name_list:list = list()
        for split in item_split:
            new_item:str = split.split(':')[-1]
            new_name_list.append(new_item)
        out_list.append('|'.join(new_name_list))
    return out_list
