import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
from contextlib import contextmanager
import math

import UI_Utilities.UI_Utils as uiu

@contextmanager
def dyn_selection(selection:list|None):
    if not selection:
        selection = mc.ls(selection=True)
    yield
    mc.select(selection, replace=True)

def get_root_joint(root_name:str)->str|None:
    joints:list = [i
                   for i in mc.ls(type='joint', long=True)
                   if root_name in i.split('|')[-1]
                   ]
    return joints[0] if joints else None

def create_joint(name:str, parented:bool=False)->str:
    if not parented:
        mc.select(clear=True)
    return mc.joint(name=name)


def orient_root(root:str|None, up:str, world_up:str)->None:
    if not root:
        return
    
    orients:dict = {
        'yz': [90, 0, 0],
        'zy': [-90, 0, 0]
    }
    rots:list|None = orients.get(up+world_up)
    if not rots:
        rots = [0.0,0.0,0.0]

    children:list = mc.listRelatives(root, children=True)
    if children:
        mc.parent(children, world=True)
    mc.setAttr(f'{root}.jointOrient', *rots, type='double3')
    if children:
        mc.parent(children, root)
    mc.makeIdentity(root, apply=True, rotate=True, translate=True, scale=True)

def add_vectors(vector_list_1:list, vector_list_2:list, multiplier:float|int|None)->list:
    vector_1:om.MVector = om.MVector(*vector_list_1)
    vector_2:om.MVector = om.MVector(*vector_list_2)
    if multiplier is not None:
        vector_2 *= multiplier
    result_vector:om.Mvector = vector_1 + vector_2
    return [result_vector[i] for i in range(3)]

def create_hand_guides_section(section:str, members:dict, up_vector:list, prefix:str, circle_shape:str, distance_multiplier:float)->None:
    members_list:list = list(members.keys())

    wrist:str = f'{prefix}{members_list[0]}'
    wrist = mc.spaceLocator(name=wrist)[0]
    mc.parent(circle_shape, wrist, shape=True, relative=True)
    mc.setAttr(f'{wrist}.displayLocalAxis', True)

    members_list.remove(members_list[0])
    fingers_list:list = [
         [f'{prefix}{k}_{i}' for i in range(members.get(k))]
        for k in members_list
    ]

    init_pos:list = [i*10 for i in up_vector]
    reversed_fingers: list = list()
    for finger in fingers_list:
        reversed_finger:list = list()
        for phalanx in finger:
            reversed_finger.insert(0,phalanx)
            loc = mc.spaceLocator(name=phalanx)[0]
            mc.setAttr(f'{loc}.displayLocalAxis', True)
            mc.setAttr(f'{loc}.translate', *init_pos, type='double3')
            init_pos = add_vectors(init_pos, up_vector, distance_multiplier)

        init_pos = [i*10 for i in up_vector]
        reversed_fingers.insert(0, reversed_finger)

    # orient the guides to the next one in the hierarchy now that the hierarchy doesn't exist yet
    for finger in reversed_fingers:
        for idx, phalanx in enumerate(finger):
            if idx < len(finger) - 1:
                mc.delete(quick_aim_constraint(finger[idx + 1], phalanx))

    # orient the wrist too since we're at it and the fingers are laying directly on top of it
    mc.delete(quick_aim_constraint(wrist, reversed_fingers[0][0]))

    for finger in reversed_fingers:
        for idx, phalanx in enumerate(finger):
            try:
                mc.parent(phalanx, finger[idx+1])
            except IndexError:
                pass
            if idx == len(finger) - 1:
                mc.parent(phalanx, wrist)
                mc.setAttr(f'{finger[0]}.rotate', 0,0,0, type='double3')

    mc.addAttr(wrist, longName='guidesSection', dataType='string')
    mc.setAttr(f'{wrist}.guidesSection', section, type='string')
    mc.setAttr(f'{wrist}.guidesSection', lock=True)

def create_root_circle_shape(name:str, up_axis:str)->str:
    axis: dict = {
        'y': [0, 1, 0],
        'z': [0, 0, 1]
    }
    up_vector: list = axis.get(up_axis)
    circle: list[str] = mc.circle(name=name, normal=up_vector)
    mc.delete(circle, constructionHistory=True)
    circle = [i for i in circle if mc.objExists(i)]
    circle:str = circle[0]
    circle_shape: str = mc.listRelatives(circle, shapes=True, fullPath=True)[0]
    return circle, circle_shape

def create_section_guides(section:str, members:dict, up_axis:str, left_side:bool|None, distance_multiplier:float|int)->None:

    axis:dict = {
        'y': [0,1,0],
        'z': [0,0,1]
    }
    up_vector:list = axis.get(up_axis)

    circle, circle_shape = create_root_circle_shape(section, up_axis)

    init_pos:list = [0,0,0]
    prefix_map:dict = {
        None: '',
        True: 'L_',
        False: 'R_'
    }
    prefix:str = prefix_map.get(left_side)

    if section == 'hand':
        create_hand_guides_section(section, members, up_vector, prefix, circle_shape, distance_multiplier)
        mc.delete(circle)
        return

    reversed_members:list = list()
    for name, number in members.items():
        if number > 1:
            for idx in range(number):
                loc = mc.spaceLocator(name=f'{prefix}{name}_{idx}')[0]
                mc.setAttr(f'{loc}.displayLocalAxis', True)
                mc.setAttr(f'{loc}.translate', *init_pos, type='double3')
                reversed_members.insert(0, loc)
                init_pos = add_vectors(init_pos, up_vector, distance_multiplier)
        else:
            loc = mc.spaceLocator(name=f'{prefix}{name}')[0]
            mc.setAttr(f'{loc}.translate', *init_pos, type='double3')
            mc.setAttr(f'{loc}.displayLocalAxis', True)
            reversed_members.insert(0, loc)
            init_pos = add_vectors(init_pos, up_vector, distance_multiplier)

    reversed_members_dags:list = uiu.get_dag_paths(reversed_members)

    for idx, member in enumerate(reversed_members):
        if idx < len(reversed_members)-1:
            mc.delete(quick_aim_constraint(reversed_members[idx + 1], member))

    for idx, member in enumerate(reversed_members):
        try:
            mc.parent(member, reversed_members[idx+1])
        except Exception as e:
            print(str(e))
    reversed_members = [i.fullPathName() for i in reversed_members_dags]

    mc.setAttr(f'{reversed_members[0]}.rotate', 0,0,0, type='double3')

    mc.parent(circle_shape, reversed_members[-1], relative=True, shape=True)
    add_guide_section_attr(reversed_members[-1], section)
    mc.delete(circle)

def add_guide_section_attr(item:str, section:str)->None:
    mc.addAttr(item, longName='guidesSection', dataType='string')
    mc.setAttr(f'{item}.guidesSection', section, type='string')
    mc.setAttr(f'{item}.guidesSection', lock=True)

def quick_aim_constraint(constrained:str, constrainer:str,
                         aimVector:list=[1, 0, 0], upVector:list=[0, 0, 1],
                         world_up:list=[1, 0, 0])->list[str]:
    #aimConstraint -offset 0 0 0 -weight 1 -aimVector 1 0 0 -upVector 0 0 1 -worldUpType "vector" -worldUpVector 1 0 0;
    return mc.aimConstraint(constrainer, constrained,
                     aimVector=aimVector, upVector=upVector,
                     worldUpType="vector", worldUpVector=world_up)

def reorient_selected_guides(primary_radios:tuple, secondary_radios:tuple, world_axis_radios:tuple, world_dir:float|int)->None:
    selection: list = mc.ls(selection=True, long=True)
    if not selection:
        return
    with dyn_selection(selection):
        primary_axis:list = [int(i.isChecked()) for i in primary_radios]
        secondary_axis:list = [int(i.isChecked()) for i in secondary_radios]
        world_axis:list = [int(i.isChecked()) for i in world_axis_radios]

        guides:list = list()
        if len(selection)==1:
            if mc.attributeQuery('guidesSection', node=selection[0], exists=True):
                guides = get_guides_hierarchy(selection[0])
            else:
                parent:list|None = mc.listRelatives(selection[0], parent=True, fullPath=True)
                root:str|None = None
                iters:int = 0
                while parent:
                    if mc.attributeQuery('guidesSection', node=parent[0], exists=True):
                        root = parent[0]
                        break
                    else:
                        parent = mc.listRelatives(parent[0], parent=True, fullPath=True)

                    iters+=1
                    if iters==50:
                        break
                if not root:
                    return
                guides = get_guides_hierarchy(root)
        elif len(selection)>1:
            guides = sorted(selection, key=lambda x: int(len(x.split('|'))), reverse=True)

        guides_dags:list[om.MDagPath] = uiu.get_dag_paths(guides)
        guides_parents_dags:list = list()
        for dag in guides_dags:
            mfn_dag_node:om.MFnDagNode = om.MFnDagNode(dag)
            parent:om.MObject = mfn_dag_node.parent(0)
            parent_mfn_dag_node:om.MFnDagNode = om.MFnDagNode(parent)
            parent_dag:om.MDagPath = om.MDagPath()
            parent_mfn_dag_node.getPath(parent_dag)
            if parent_dag.fullPathName():
                guides_parents_dags.append(parent_dag)

        parents_associations:list = list(zip(guides_dags, guides_parents_dags))
        mc.parent(guides, world=True)

        for idx, gd in enumerate(guides_dags):
            try:
                # this still needs the world orientation of secondary axis as an input!!
                mc.delete(quick_aim_constraint(guides_dags[idx+1].fullPathName(), gd.fullPathName(),
                                               aimVector=primary_axis, upVector=secondary_axis,
                                               world_up=[i*world_dir for i in world_axis]))
            except Exception as e:
                print(str(e))

        for child_dag, parent_dag in parents_associations:
            mc.parent(child_dag.fullPathName(), parent_dag.fullPathName())
        mc.setAttr(f'{guides_dags[0].fullPathName()}.rotate', 0,0,0, type='double3')

def mirror_selected_guides(mirror_direction:list|tuple=(-1,0,0))->None:
    # we'll accept the selection only if it's a root guide
    selected_guides: list = mc.ls(selection=True, long=True)
    if not selected_guides:
        return
    valid_guides:list = [
        i
        for i in selected_guides
        if mc.attributeQuery('guidesSection', node=i, exists=True)
    ]
    if not valid_guides:
        uiu.buildMsg(['Error:', 'No valid root guide found in selection', 'Select the root guide of a section to mirror it.'],
                     ['red', 'orange', 'yellow'],
                     ['Arial', 14])
        return
    mirror_map:dict = {
        'L':'R_',
        'R':'L_',
    }
    # get the dagPaths first
    guides_dags:list[om.MDagPath] = uiu.get_dag_paths(valid_guides)
    # get all the dagPaths parents
    guides_parents_dags:list[om.MDagPath] = list()
    for dag in guides_dags:
        mfn_dag_node:om.MFnDagNode = om.MFnDagNode(dag)
        parent:om.MObject = mfn_dag_node.parent(0)
        parent_mfn_dag_node:om.MFnDagNode = om.MFnDagNode(parent)
        parent_dag:om.MDagPath = om.MDagPath()
        parent_mfn_dag_node.getPath(parent_dag)
        guides_parents_dags.append(parent_dag)

    # now we can start doing our magic.
    for dag in guides_dags:
        section:str = mc.getAttr(f'{dag.fullPathName()}.guidesSection')
        mc.parent(dag.fullPathName(), world=True)
        grp:str = mc.group(name='mirroring_grp_delete_me_please', empty=True, world=True)
        mc.parent(dag.fullPathName(), grp)
        dup_grp:str = mc.duplicate(grp)[0]
        mc.setAttr(f'{dup_grp}.scale', *mirror_direction, type='double3')
        children:list = mc.listRelatives(dup_grp, allDescendents=True, fullPath=True)
        locators:list = [
            mc.listRelatives(i, parent=True, fullPath=True)[0]
            for i in children
            if mc.nodeType(i)=='locator'
        ]
        #locators.sort(key=lambda x: int(len(x.split('|'))), reverse=True)
        new_guides:list[str] = list()
        for loc in locators:
            name:str = loc.split('|')[-1]
            split:list = name.split('_')
            side:str = mirror_map.get(split[0])
            if not side: continue
            new_name:str = f'{side}{"_".join(split[1:])}'
            new_name = mc.ls(mc.spaceLocator(name=new_name)[0], long=True)[0]
            mc.setAttr(f'{new_name}.displayLocalAxis', True)
            mc.delete(mc.parentConstraint(loc, new_name, maintainOffset=False))
            new_guides.append(new_name)

        new_guides:list[om.MDagPath] = uiu.get_dag_paths(new_guides)

        for idx, ng in enumerate(new_guides):
            sibling:str = locators[idx]
            sib_parent:str = mc.listRelatives(sibling, parent=True, fullPath=True)[0]
            sib_par_name:str = sib_parent.split('|')[-1]
            sib_par_split:list = sib_par_name.split('_')
            side:str = mirror_map.get(sib_par_split[0])
            if not side: continue
            #new_guide_parent:str = f'{side}{sib_par_split[1]}'
            new_guide_parent = [i for i in new_guides if f'{side}{"_".join(sib_par_split[1:])}' in i.fullPathName().split('|')[-1]][0] or om.MDagPath()
            if mc.objExists(new_guide_parent.fullPathName()):
                mc.parent(ng.fullPathName(), new_guide_parent.fullPathName())

        top_guide:str|None = [i.fullPathName()
                             for i in new_guides
                             if not mc.listRelatives(i.fullPathName(), parent=True, fullPath=True)
                             ][0] or None
        if top_guide:
            add_guide_section_attr(top_guide, section)
            circle, circle_shape = create_root_circle_shape(section, uiu.get_up_axis())
            mc.parent(circle_shape, top_guide, relative=True, shape=True)
            mc.delete(circle)



        mc.delete(dup_grp)
        guide_parent = guides_parents_dags[guides_dags.index(dag)].fullPathName()
        if mc.objExists(guide_parent):
            mc.parent(dag.fullPathName(), guide_parent)
            mc.parent(top_guide, guide_parent)

        mc.delete(grp)

def snap_appendages_guides_to_limbs()->None:
    selection:list = mc.ls(selection=True, long=True)
    if not selection:
        return
    for sel in selection:
        base_name:str = sel.split('|')[-1]
        existing:list = mc.ls(base_name, long=True)
        if len(existing) != 2:
            continue
        existing.remove(sel)
        mc.delete(mc.parentConstraint(existing[0], sel, maintainOffset=False))

def attach_appendages_guides_to_limbs()->None:
    selection: list = mc.ls(selection=True, long=True)
    if not selection:
        return
    for sel in selection:
        base_name:str = sel.split('|')[-1]
        existing:list = mc.ls(base_name, long=True)
        if len(existing) != 2:
            continue
        existing.remove(sel)
        target_parent:str = existing[0]
        children:list = mc.listRelatives(sel, children=True, type='transform', fullPath=True)
        mc.parent(children, target_parent)

def get_guides_hierarchy(root_guide:str)->list:
    all_children:list = [i
                         for i in mc.listRelatives(root_guide, allDescendents=True, fullPath=True)
                         if mc.nodeType(i) == 'transform'
                         ]
    guide_roots:list = [i
                        for i in all_children
                        if mc.attributeQuery('guidesSection', node=i, exists=True)
                        ]
    if guide_roots:
        to_remove:list = list()
        for root in guide_roots:
            to_remove.extend(
                [i
                 for i in mc.listRelatives(root, allDescendents=True, fullPath=True)
                 if mc.nodeType(i) == 'transform'
                 ]
            )
            to_remove.append(root)
        if to_remove:
            for rem in to_remove:
                if rem in all_children:
                    all_children.remove(rem)
    all_children.append(root_guide)
    return all_children

def get_all_guides_hierarchies()->dict|None:
    selection:list = mc.ls(selection=True, long=True)
    if len(selection) != 1: return None# we want one single root to start from
    if not [i for i in selection if mc.attributeQuery('guidesSection', node=i, exists=True)]:
        return None# we want a section root to be selected
    child_roots:list = [i
                        for i in mc.listRelatives(selection[0], allDescendents=True, fullPath=True)
                        if mc.attributeQuery('guidesSection', node=i, exists=True)
                     ]
    child_roots.extend(selection)
    out_data:dict = dict()
    for root in child_roots:
        section:str = mc.getAttr(f'{root}.guidesSection')
        if section not in out_data:
            out_data[section] = list()
        hierarchy:list = get_guides_hierarchy(root)
        local_dict:dict = dict()
        for loc in hierarchy:
            mtx:list = mc.xform(loc, query=True, matrix=True, worldSpace=True)
            parent:str = mc.listRelatives(loc, parent=True, fullPath=True)
            if parent:
                parent = parent[0] if mc.listRelatives(parent[0], shapes=True) else None
            local_dict[loc] = {
                'parent':parent,
                'world_matrix':mtx,
                'isRoot': loc in child_roots,
            }
        out_data[section].append(local_dict)
    return out_data

def rebuild_guides_hierarchy(data:dict)->None:

    locators_data:list = list()
    for section, members in data.items():
        for section_data in members:
            for loc, loc_data in section_data.items():
                loc_name:str = loc.split('|')[-1]
                mtx:list = loc_data.get('world_matrix')
                is_root:bool = loc_data.get('isRoot')
                loc_dag:om.MDagPath = uiu.get_dag_paths([mc.spaceLocator(name=loc_name)[0]])[0]
                mc.setAttr(f'{loc_dag.fullPathName()}.displayLocalAxis', True)
                if mtx:
                    mc.xform(loc_dag.fullPathName(), matrix=mtx, worldSpace=True)
                if is_root:
                    add_guide_section_attr(loc_dag.fullPathName(), section)
                    circle, circle_shape = create_root_circle_shape(section, uiu.get_up_axis())
                    mc.parent(circle_shape, loc_dag.fullPathName(), relative=True, shape=True)
                    mc.delete(circle)
                locators_data.append(loc_dag)
    # parenting
    for section, members in data.items():
        for section_data in members:
            for loc, loc_data in section_data.items():
                loc_name:str = loc.split('|')[-1]
                parent:str|None = loc_data.get('parent')
                loc_dag:om.MDagPath = [i
                                       for i in locators_data
                                       if loc_name in i.partialPathName().split('|')[-1]
                                       ][0]
                if parent:
                    parent_name:str = parent.split('|')[-1]
                    parent_dag:om.MDagPath = [i
                                              for i in locators_data
                                              # there could be another locator with the same name not yet parented where it should, so this
                                              # one may have been automatically renamed to avoid name clashing by appending a number at the end
                                              if parent_name in i.partialPathName().split('|')[-1]
                                              ][0]
                    if mc.objExists(parent_name):
                        mc.parent(loc_dag.fullPathName(), parent_dag.fullPathName())

    mc.viewFit(allObjects=True)

def create_joint_name(locator_name:str, guides_to_joint_map:dict, template_data:dict)->str:
    name_split: list = locator_name.split('_')
    sides_data:dict = template_data.get('sides')

    sides: list = list()
    name: str = str()
    num: str | None = None
    for chunk in name_split:
        if chunk.isdigit():
            num = chunk
        if chunk in sides_data:
            sides.append(sides_data.get(chunk))
        if chunk in guides_to_joint_map:
            name = guides_to_joint_map.get(chunk)
    side:str = '_'.join(sides)
    return f'{side+"_" if side else ""}{name}{"_"+num if num else ""}'

def build_skeleton_from_guides(guides_data:dict, template_data:dict)->None:

    if not guides_data or not template_data:
        return

    guides_to_joint_map:dict = template_data.get('guides_to_joint_map')

    root_name:str|None = guides_to_joint_map.get('Root')
    root_name = get_root_joint(root_name)

    joints_to_guides_list:list = list()
    for section, members in guides_data.items():
        for section_data in members:
            for loc, loc_data in section_data.items():
                loc_name:str = loc.split('|')[-1]
                joint:str = create_joint_name(loc_name, guides_to_joint_map, template_data)
                joint = create_joint(joint, parented=False)
                joint_dag:om.MDagPath = uiu.get_dag_paths([joint])[0]
                mc.xform(joint, matrix=loc_data.get('world_matrix'), worldSpace=True)
                loc_parent:str|None = loc_data.get('parent')
                joints_to_guides_list.append(
                    {
                        'joint' : joint_dag,
                        'locator': loc,
                        'parent_locator': loc_parent,
                    }
                )
    root:str|None = None
    for joint_data in joints_to_guides_list:
        joint:om.MDagPath = joint_data.get('joint')
        parent_loc:str = joint_data.get('parent_locator')
        if not parent_loc:
            root = joint.fullPathName()
        for jnt_dt in joints_to_guides_list:
            loc:str = jnt_dt.get('locator')
            if parent_loc == loc:
                parent_joint:om.MDagPath = jnt_dt.get('joint')
                mc.parent(joint.fullPathName(), parent_joint.fullPathName())

    if root:
        mc.makeIdentity(root, apply=True, rotate=True, jointOrient=False)
    if root_name:
        mc.parent(root, root_name)
        mc.makeIdentity(root_name, apply=True, rotate=True, jointOrient=False)

def get_average_position_vector()->list:
    selection:list = mc.ls(selection=True, long=True, flatten=True)
    if not selection:
        return []
    mc.ConvertSelectionToVertices()
    selection:list = mc.ls(selection=True, long=True, flatten=True)
    vtx_num = len(selection)
    vector_sum:om.MVector = om.MVector()
    for vtx in selection:
        pos:list = mc.pointPosition(vtx, world=True)
        vector:om.MVector = om.MVector(*pos)
        vector_sum += vector

    avg_vector:om.MVector = vector_sum / float(vtx_num)
    return [avg_vector[i] for i in range(3)]

def get_manipulator_position_vector(component_list:list):
    mc.select(component_list, replace=True)
    mc.ConvertSelectionToVertices()
    mc.select(mc.ls(selection=True, long=True, flatten=True), replace=True)
    mc.setToolTo('moveSuperContext')
    mc.manipMoveContext('Move', edit=True, mode=0)
    return mc.manipMoveContext('Move', query=True, position=True)

def get_manipulator_rotation_vector(components_list:list):
    mc.select(components_list, replace=True)
    mc.select(mc.ls(selection=True, long=True, flatten=True), replace=True)
    mc.setToolTo('moveSuperContext')
    mode:int = mc.manipMoveContext('Move', query=True, mode=True)
    mc.manipMoveContext('Move', edit=True, mode=10)
    rot:list = [math.degrees(i) for i in mc.manipMoveContext('Move', query=True, orientAxes=True)]
    mc.manipMoveContext('Move', edit=True, mode=mode)
    return rot

def rotate_guides_to_component(components_list:list, guides_list:list)->None:
    for cmp, gd in zip(components_list, guides_list):
        rot:list = get_manipulator_rotation_vector(cmp)
        snap_guides_to_components_center([cmp], [gd])
        mc.xform(gd, absolute=True, rotation=rot, worldSpace=True)


def snap_guides_to_components_center(components_list:list, guides_list:list)->None:
    center:list = get_manipulator_position_vector(components_list)
    for guide in guides_list:
        mc.move(*center, guide, absolute=True, worldSpace=True, preserveChildPosition=True)

    mc.select(clear=True)

def add_twist_joints(joints_number:float, fraction:float, template:dict)->None:
    selection:list = mc.ls(selection=True, long=True)
    if not selection:
        return

    twist_suffix:str = template.get('twist')
    with dyn_selection(selection):
        for jnt in selection:
            jnt_name:str = jnt.split('|')[-1]
            children:list|None = mc.listRelatives(jnt, children=True, fullPath=True)
            if not children: #it's a leaf joint, skip it
                continue
            children = [i
                             for i in children
                             if mc.listRelatives(i, children=True)
                             ]

            existing_twists:list = [i
                                    for i in mc.listRelatives(jnt, children=True, fullPath=True)
                                    if i not in children
                                    if twist_suffix in i.split('|')[-1]
                                    ]
            if existing_twists:
                mc.delete(existing_twists)
            children: list | None = mc.listRelatives(jnt, children=True, fullPath=True)

            length:float = mc.getAttr(f'{children[0]}.translateX') * fraction
            increment:float = length / float(joints_number+1)
            next_dist:float = 0.0
            for idx in range(joints_number):
                mc.select(jnt, replace=True)
                twist_name:str = f'{jnt_name}_{twist_suffix}_{idx}'
                if not mc.objExists(twist_name):
                    mc.joint(name=twist_name)
                next_dist += increment
                mc.setAttr(f'{twist_name}.translateX', next_dist)

def get_all_joints()->list:
    all_joints:list = mc.ls(type='joint', long=True)
    return sorted(all_joints, key=lambda x: int(len(x.split('|'))))

def get_all_joints_under_root(root_name:str)->list:
    roots:list = mc.ls(root_name, long=True)
    root:str|None = roots[0] if roots else None
    if not root:
        return list()
    hierarchy:list = mc.ls(mc.listRelatives(root, allDescendents=True, fullPath=True), type='joint')
    hierarchy.append(root)
    return hierarchy



def get_hik_name(idx:int)->str:
    return mc.GetHIKNodeName(idx)

def hik_plugin_check()->None:
    plugins = mc.pluginInfo(query=True, listPlugins=True)
    if 'mayaHIK' not in plugins:
        mc.loadPlugin('mayaHIK')

def get_hik_joints_ids() -> dict:
    """ reusable as static query method """
    hik_jnts = dict()
    hik_count = mc.hikGetNodeCount()

    for i in range(hik_count):
        hik_name = mc.GetHIKNodeName(i)
        hik_jnts[hik_name] = i
    return hik_jnts

def assign_joint_to_hik_id(joint:str, hik_id:int, char_name)->None:
    mel.eval(f'setCharacterObject("{joint}","{char_name}",{hik_id},0);')

def create_hik_character()->str:
    prmpt_dialog = mc.promptDialog(title='Choose character name',
                                   message='Choose a name for your new character definition',
                                   button=['OK', 'Default', 'Cancel'],
                                   defaultButton='OK',
                                   dismissString='Cancel',
                                   cancelButton='Cancel'
                                   )

    if prmpt_dialog == 'Cancel':
        return str()
    elif prmpt_dialog == 'Default':
        char_name = 'Character'
    else:
        char_name = mc.promptDialog(query=True, text=True)
        if not char_name:
            char_name = 'Character'

    mel.eval('HIKCharacterControlsTool;')
    mel.eval(f'hikCreateCharacter( "{char_name}" )')
    mel.eval(f'hikSetCurrentCharacter( "{char_name}" )')
    return char_name

def toggle_lock_hik_definition()->None:
    mel.eval('hikToggleLockDefinition();')
    mel.eval('refreshAE;')

def get_hik_joint_name(joint_name:str, sides_map:dict, skel_hik_map:dict, template:dict)->str:
    split_name: list = joint_name.split('_')
    hik_side: str | None = None
    hik_name: str | None = None
    num: int | None = None
    out_name: str = str()
    for chunk in split_name:
        if chunk.isdigit():
            num = int(chunk)
        elif sides_map.get(chunk):
            hik_side = sides_map.get(chunk)
        elif skel_hik_map.get(chunk):
            hik_name = skel_hik_map.get(chunk)
    if hik_name:
        out_name = f'{hik_side if hik_side else ""}{hik_name}{num if num else ""}'
    return out_name


def characterize_skeleton(hik_id_map:dict, sides_map:dict, skel_hik_map:dict, template:dict)->None:
    char_name:str = create_hik_character()
    if not char_name:
        return
    all_joints = get_all_joints()
    hik_command_map:dict = dict()
    for joint in all_joints:
        name:str = joint.split('|')[-1]
        hik_joint_name:str = get_hik_joint_name(name, sides_map, skel_hik_map, template)

        if template.get('twist') in name or (not hik_joint_name):
            continue

        if not hik_command_map.get(hik_joint_name):
            hik_command_map[hik_joint_name] = [joint, hik_id_map.get(hik_joint_name)]
        else:
            num = 1
            hik_joint_entry:str|None = hik_command_map.get(hik_joint_name)
            while hik_joint_entry:
                numbered:str = f'{hik_joint_name}{num}'
                if not hik_command_map.get(numbered):
                    hik_joint_name = numbered
                num += 1
                hik_joint_entry = hik_command_map.get(hik_joint_name)
            hik_command_map[hik_joint_name] = [joint, hik_id_map.get(hik_joint_name)]

    for hik, data in hik_command_map.items():
        joint, hik_id = data
        assign_joint_to_hik_id(joint, hik_id, char_name)
    try:
        toggle_lock_hik_definition()
    except Exception as ex:
        print(str(ex))



def update_guides_to_joints_start(guides_data:dict, template:dict, invert:bool)->None:
    guides_to_joint_map:dict = template.get('guides_to_joint_map')
    skipped:list = list()
    for section, members in guides_data.items():
        for section_data in members:
            for loc, loc_data in section_data.items():
                loc_name:str = loc.split('|')[-1]
                joint: str = create_joint_name(loc_name, guides_to_joint_map, template)
                if not mc.objExists(joint):
                    skipped.append([loc_name, joint])
                    continue
                joint = mc.ls(joint, type='joint')[0]
                if invert:
                    mc.parentConstraint(loc, joint, maintainOffset=False)
                else:
                    mc.parentConstraint(joint, loc, maintainOffset=False)

    if skipped:
        msg:str = '\n'.join([f'{i[0]}->{i[1]}' for i in skipped])
        msg = f'Guides update preparation skipped the following connections:\n{msg}'
        print(msg)

def update_guides_to_joints_end(template:dict)->None:
    root:str|None = get_root_joint(template.get('guides_to_joint_map').get('Root'))
    if not root:
        roots:list = [i
                        for i in mc.ls(type='joint')
                        if not mc.listRelatives(i, parent=True, fullPath=True)
                      ]
        if len(roots) != 1:
            return
        root = roots[0]
    children:list = mc.listRelatives(root, allDescendents=True, fullPath=True, type='joint')
    children.append(root)
    constraints_names:list = ['parentConstraint', 'orientConstraint', 'pointConstraint']
    for child in children:
        conns:list = [i
                      for i in mc.listConnections(child, destination=True)
                      if mc.nodeType(i) in constraints_names
                      ]
        if conns:
            mc.delete(conns)

def bind_skin(bind_to:str, max_influences:int, bind_method:int, skinning_method:int)->None:
    """cmds.skinCluster( 'joint1', 'pPlane1', dr=4.5)"""
    selection:list = mc.ls(selection=True, long=True)
    if not selection:
        return
    joints:list = mc.ls(selection, type='joint')
    meshes:list = [i for i in selection if i not in joints]
    if (not joints) or (not meshes):
        return

    if bind_to == 'Joints Hierarchy':
        root:str = str()
        parent:list|None = mc.listRelatives(joints[0], parent=True, fullPath=True)
        if not parent:
            root = joints[0]
        else:
            while parent:
                par:list|None = mc.listRelatives(parent[0], parent=True, fullPath=True)
                if not par or mc.nodeType(par[0]) != 'joint':
                    root = parent[0]
                    break
                parent = par
        joints.clear()
        joints = mc.listRelatives(root, allDescendents=True, fullPath=True)
        joints.append(root)


    selection.clear()
    selection.extend(joints)
    selection.extend(meshes)
    mc.skinCluster(selection, skinMethod=skinning_method, toSelectedBones=True,
                   obeyMaxInfluences=True, normalizeWeights=1, maximumInfluences=max_influences,
                   bindMethod=bind_method, weightDistribution=1, dropoffRate=10.0)

def create_tpose_utility_locator(joint:str)->str:
    def round_normalize(vec:list) -> None:
        for idx, ax in enumerate(vec):
            ax = round(ax, 0)
            vec[idx] = ax

    mtx:list = mc.xform(joint, query=True, matrix=True, worldSpace=True)
    x_axis:list = mtx[0:3]
    y_axis:list = mtx[4:7]
    z_axis:list = mtx[8:11]

    round_normalize(x_axis)
    round_normalize(y_axis)
    round_normalize(z_axis)

    new_mtx:list = list()
    x_axis.append(0.0)
    y_axis.append(0.0)
    z_axis.append(0.0)

    new_mtx.extend(x_axis)
    new_mtx.extend(y_axis)
    new_mtx.extend(z_axis)
    new_mtx.extend(mtx[12:])

    loc:str = mc.spaceLocator(name=f'{joint}_aim_constraint_locator')[0]
    mc.xform(loc, matrix=new_mtx, worldSpace=True)
    return loc

def get_joint_orient_vectors(joint:str)->tuple[list, list, list]:
    mtx: list = mc.xform(joint, query=True, matrix=True, worldSpace=True)
    x_axis: list = mtx[0:3]
    y_axis: list = mtx[4:7]
    z_axis: list = mtx[8:11]
    return x_axis, y_axis, z_axis

def make_t_pose(actuator:dict)->None:
    choice_: str = mc.confirmDialog(
        title='Children orientation',
        message='Do you want to orient the next 2 children in the hierarchy?',
        button=['Yes', 'No'],
        cancelButton='No',
        dismissString='No'
    )
    dist:float = 10000.0
    constraints:list = list()
    locators:list = list()
    for joint, vector in actuator.items():
        loc:str = create_tpose_utility_locator(joint)
        locators.append(loc)
        x_axis, y_axis, z_axis = get_joint_orient_vectors(joint)
        pos: list = mc.getAttr(f'{loc}.translate')[0]
        new_pos: list = [(i[0] + i[1]) for i in zip([i*dist for i in vector], pos)]
        mc.setAttr(f'{loc}.translate', *new_pos, type='double3')
        old_loc_pos:om.MVector = om.MVector(*pos)
        new_loc_pos:om.MVector = om.MVector(*new_pos)
        move_vector:om.MVector = new_loc_pos - old_loc_pos
        move_vector.normalize()
        x_axis_vector:om.MVector = om.MVector(*x_axis)
        dot:float = x_axis_vector * move_vector

        multiplier:float = dot and (1.0,-1.0)[dot < 0.0]

        aim_vector:list = [i * multiplier for i in [1, 0, 0]]
        constraints.extend(
            mc.aimConstraint(loc, joint, weight=1, offset=[0,0,0],
                             aimVector=aim_vector, upVector=[0,0,1],
                             worldUpType='objectrotation', worldUpVector=[0,0,1],
                             worldUpObject=loc)
        )
        if choice_ == 'No':
            continue
        # let's do this on the remaining joints of the chain, finding only the joints that
        # have one child of their own, skipping if otherwise (no children or multiple children)
        children:list = mc.listRelatives(joint, children=True, fullPath=True)
        if not children:
            continue
        children = [
            i for i in children
            if mc.listRelatives(i, children=True, fullPath=True)
        ]
        if len(children) > 1:
            continue # like the hands, for example
        grand_children:list = mc.listRelatives(children[0], children=True, fullPath=True)
        if not grand_children:
            continue
        children.extend([
            i for i in grand_children
            if mc.listRelatives(i, children=True, fullPath=True)
        ])
        children.sort(key=lambda x: int(len(x.split('|'))))
        for child in children:
            constraints.extend(
                mc.aimConstraint(loc, child, weight=1, offset=[0, 0, 0],
                                 aimVector=aim_vector, upVector=[0, 0, 1],
                                 worldUpType='objectrotation', worldUpVector=[0, 0, 1],
                                 worldUpObject=loc)
            )
    mc.delete(constraints)
    mc.delete(locators)


def get_selected_joints()->list:
    selection:list = mc.ls(selection=True, long=True, type='joint')
    if not selection:
        return list()
    return selection

def save_bind_pose(selection:list, pose_name:str)->None:
    if not selection:
        return
    pose_name = mc.dagPose(selection, bindPose=True, save=True, name=pose_name)
    mc.addAttr(pose_name, longName='poseType', dataType='string')
    mc.setAttr(f'{pose_name}.poseType', pose_name, type='string')
    mc.setAttr(f'{pose_name}.poseType', lock=True)

def get_all_bind_poses(selection:list)->list:
    poses:list = list()
    for sel in selection:
        hist:list = mc.listHistory(sel)
        fut:list = mc.listHistory(sel, future=True, allFuture=True)
        poses.extend(hist)
        poses.extend(fut)
    poses = mc.ls(poses, type='dagPose')
    return poses

def create_update_bind_pose(root_name:str, pose_name:str)->None:
    # get the root
    root:str = get_root_joint(root_name)
    if not root:
        return
    hierarchy:list = mc.ls(mc.listRelatives(root, allDescendents=True, fullPath=True), type='joint')
    hierarchy.append(root)
    all_poses:list = get_all_bind_poses(hierarchy)
    this_pose_type:list = [i
                           for i in all_poses
                           if mc.attributeQuery('poseType', node=i, exists=True)
                           if mc.getAttr(f'{i}.poseType') == pose_name
                           ]
    if this_pose_type:
        mc.delete(this_pose_type)
    save_bind_pose(hierarchy, pose_name)

def go_to_bind_pose(root_name:str)->None:
    root:str|None = get_root_joint(root_name)
    if not root:
        return
    with dyn_selection(None):
        mc.select(root, replace=True)
        mc.GoToBindPose()


