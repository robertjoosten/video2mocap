from maya import cmds
from utils.path import *


def create_skeleton():
    """
    Create a skeleton hierarchy using the variables provided in the path
    module.

    :return: Skeleton data
    :rtype: dict
    """
    # variable
    joints = {}

    # clear selection
    cmds.select(clear=True)

    # create body
    for body in BODY_HIERARCHY:
        joint = cmds.joint(name="{}_jnt".format(body))
        joints[body] = joint

    # create limbs
    for side in ["l", "r"]:
        cmds.select(joints["hip"])
        for leg in LEG_HIERARCHY:
            joint = cmds.joint(name="{}_{}_jnt".format(side, leg))
            joints["{}_{}".format(side, leg)] = joint

        cmds.select(joints["spine"])
        for arm in ARM_HIERARCHY:
            joint = cmds.joint(name="{}_{}_jnt".format(side, arm))
            joints["{}_{}".format(side, arm)] = joint

    # reference
    reference_name = "reference"
    reference = cmds.spaceLocator(name=reference_name)[0]
    joints["reference"] = reference

    # parent hip to reference
    cmds.parent(joints["hip"], reference)

    return joints


def position_skeleton(skeleton_data, gen):
    """
    Position the skeleton using the data that is stored in the Skeleton
    Generator node. The joint ids are sorted and looped to make sure the
    positions get set in the correct order. Unfortunately this is not correct
    and the head is processed before the neck. This means this function will
    have to be ran twice to ensure the currect stance position of the
    skeleton.

    :param dict skeleton_data:
    :param str gen:
    """
    for _id in sorted(HIK_ID_MAPPER.keys()):
        attribute = HIK_ID_MAPPER.get(_id)
        joint = skeleton_data.get(HIK_MAPPER.get(attribute))

        # position joint
        translate = cmds.getAttr("{}.{}T".format(gen, attribute))[0]
        rotate = cmds.getAttr("{}.{}R".format(gen, attribute))[0]
        scale = cmds.getAttr("{}.{}S".format(gen, attribute))[0]

        cmds.xform(
            joint,
            worldSpace=True,
            translation=translate,
            rotation=rotate,
            scale=scale
        )
