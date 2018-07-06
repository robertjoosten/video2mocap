from __future__ import absolute_import

import os
import sys
from absl import flags


# ----------------------------------------------------------------------------


flags.DEFINE_string("json_path", None, "Path containing json data exported by HMR")
flags.DEFINE_string("output_dir", None, "Output dir for characters")


# ----------------------------------------------------------------------------


def bind(group_data, skeleton_data):
    """
    Bind the group data to the skeleton data using constraints. Doing this
    will not only take translation into account but also a proper rotation
    which is needed for a decent result.

    :param dict group_data:
    :param dict skeleton_data:
    """
    # point constraint hip joint between left and right
    cmds.pointConstraint(
        [group_data["l_hip"], group_data["r_hip"]],
        group_data["hip"],
        maintainOffset=False
    )

    # parent constraint spine joint between hip and neck
    constraint = cmds.parentConstraint(
        [group_data["hip"], group_data["neck"]],
        group_data["spine"],
        maintainOffset=False,
        skipRotate="none"
    )[0]

    # set aliases to position spine closer to the hip
    aliases = cmds.parentConstraint(
        constraint,
        query=True,
        weightAliasList=True
    )
    cmds.setAttr("{}.{}".format(constraint, aliases[0]), 0.8)
    cmds.setAttr("{}.{}".format(constraint, aliases[1]), 0.2)

    # create point constraints
    for key, group in group_data.iteritems():
        joint = skeleton_data.get(key)
        if not joint:
            continue

        cmds.pointConstraint(group, joint, maintainOffset=False)

    # aim constraints
    # body
    cmds.aimConstraint(
        group_data.get("neck"),
        skeleton_data.get("hip"),
        aimVector=[0, 1, 0],
        upVector=[1, 0, 0],
        worldUpVector=[0, 0, 1],
        worldUpType="object",
        worldUpObject=group_data.get("l_hip")
    )
    cmds.aimConstraint(
        group_data.get("head"),
        skeleton_data.get("neck"),
        aimVector=[0, 1, 0],
        upVector=[0, 0, 1],
        worldUpVector=[0, 0, -1],
        worldUpType="objectrotation",
        worldUpObject=group_data.get("neck")
    )

    # limbs
    for side, aimDirection in zip(["l", "r"], [1, -1]):
        # leg
        for leg1, leg2 in zip(LEG_HIERARCHY[:-1], LEG_HIERARCHY[1:]):
            joint = skeleton_data.get("{}_{}".format(side, leg1))
            target = group_data.get("{}_{}".format(side, leg2))

            up_name = LEG_HIERARCHY[:]
            up_name.remove(leg1)
            up_name.remove(leg2)
            up = group_data.get("{}_{}".format(side, up_name[0]))

            cmds.aimConstraint(
                target,
                joint,
                aimVector=[0, -1, 0],
                upVector=[0, 0, -1],
                worldUpVector=[0, 0, 1],
                worldUpType="object",
                worldUpObject=up
            )

        # arm
        for arm1, arm2 in zip(ARM_HIERARCHY[:-1], ARM_HIERARCHY[1:]):
            joint = skeleton_data.get("{}_{}".format(side, arm1))
            target = group_data.get("{}_{}".format(side, arm2))

            up_name = ARM_HIERARCHY[:]
            up_name.remove(arm1)
            up_name.remove(arm2)
            up = group_data.get("{}_{}".format(side, up_name[0]))

            cmds.aimConstraint(
                target,
                joint,
                aimVector=[aimDirection, 0, 0],
                upVector=[0, 0, 1],
                worldUpVector=[0, 0, 1],
                worldUpType="object",
                worldUpObject=up
            )

    # need to do more testing to confidently bind the wrist, ankles and head.
    # At the moment the results seem inaccurate.


# ----------------------------------------------------------------------------


def get_center_matrix(matrices):
    """
    Get a matrix that can be used to transform other matrices to make sure on
    the start frame the center point between the ankles is at 0, 0, 0 in world
    space.

    :param dict matrices:
    :return: Center matrix
    :rtype: OpenMaya.MMatrix
    """
    # get ankle matrices
    l_ankle = OpenMaya.MVector(matrices.get("l_ankle")[12:15])
    r_ankle = OpenMaya.MVector(matrices.get("r_ankle")[12:15])
    center = (l_ankle + r_ankle) * -0.5

    # compile matrix
    return OpenMaya.MMatrix(
        [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            center.x, center.y, center.z, 1.0
        ]
    )


def get_scale_matrix():
    """
    The scale matrix is used to scale the character to be 170 cm tall. The
    uniform scale can be adjusted in maya to make it work for different sized
    characters.

    :return: Scale matrix
    :rtype: OpenMaya.MMatrix
    """
    scale = 170 / 1.5
    return OpenMaya.MMatrix(
        [
            1.0 * scale, 0.0, 0.0, 0.0,
            0.0, -1.0 * scale, 0.0, 0.0,
            0.0, 0.0, -1.0 * scale, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
    )


# ----------------------------------------------------------------------------


def animate(group_data, skeleton_data, mocap_data):
    """
    Loop over the mocap data and key frame all of the groups. After all of the
    keys are set the skeleton itself will be baked and the groups and formerly
    created constraints will removed so only the desired skeleton and hik are
    left in the scene

    :param dict group_data:
    :param dict skeleton_data:
    :param list mocap_data:
    """
    # get center matrix
    data = mocap.get_first_valid_frame(mocap_data)
    center_matrix = get_center_matrix(data.get("matrices_3d"))

    # scale an rotate matrix
    scale_matrix = get_scale_matrix()

    # bake groups
    for i, frame in enumerate(mocap_data):
        if not frame:
            logger.debug("No Frame Data:         {}".format(i + 1))
            continue

        for name, group in group_data.iteritems():
            # get matrix
            matrix = frame.get("matrices_3d").get(name)
            if not matrix:
                continue

            matrix = OpenMaya.MMatrix(frame.get("matrices_3d").get(name))

            # set matrix
            cmds.currentTime(i + 1)
            cmds.xform(
                group,
                worldSpace=True,
                matrix=matrix * center_matrix * scale_matrix
            )
            cmds.setKeyframe(group)

    # get attributes
    attributes = [
        "{}.{}{}".format(joint, attribute, channel)
        for joint in skeleton_data.values()
        for attribute in ["translate", "rotate", "scale"]
        for channel in ["X", "Y", "Z"]
    ]

    # get constraints
    constraints = []
    for joint in skeleton_data.values():
        constraint = cmds.listConnections(joint, type="constraint") or []
        constraints.extend(constraint)

    # bake joints
    cmds.bakeResults(
        attributes,
        t=(1, len(mocap_data)),
    )

    # cleanup
    cmds.delete(group_data.values() + constraints)


# ----------------------------------------------------------------------------


def process(path, output_dir):
    """
    Convert the stored mocap json file to animated maya human ik skeletons.
    Each character will be exported as a separate maya file.

    :param str path:
    :param str output_dir:
    """
    # load mocap data
    mocap_data = io.read_json(path)

    # extract character data
    characters = mocap.extract_people_sequence(mocap_data)

    # loop people
    for i, character in enumerate(characters):
        # open a new scene
        cmds.file(newFile=True, force=True)

        # extract frames
        frames = character.get("frames")

        # create groups
        valid_frame = mocap.get_first_valid_frame(frames)
        character_groups = mocap.create_groups(valid_frame)

        # create skeleton
        character_skeleton = skeleton.create_skeleton()

        # create hik
        hik.create_hik(character_skeleton)

        # bind
        bind(character_groups, character_skeleton)

        # query character height
        animate(character_groups, character_skeleton, frames)

        # save file
        output_path = os.path.join(
            output_dir,
            "character_{0:02d}.ma".format(i+1)
        )

        cmds.file(rename=output_path)
        cmds.file(save=True, type="mayaAscii")

        # log save
        logger.info("Saved Character:       {}".format(output_path))


# ----------------------------------------------------------------------------


if __name__ == '__main__':
    # initialize maya standalone
    import maya.standalone
    maya.standalone.initialize()

    from maya import cmds, mel
    from maya.api import OpenMaya
    from utils import io, hik, mocap, logging, skeleton
    from utils.path import *

    # convert data
    config = flags.FLAGS
    config(sys.argv)

    # create logger
    logger = logging.get_maya_logger(config.output_dir)

    # process data
    process(config.json_path, config.output_dir)
