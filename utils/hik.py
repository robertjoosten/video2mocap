from __future__ import absolute_import

from maya import cmds, mel
from utils import skeleton
from utils.path import *


def create_hik(skeleton_data):
    """
    Create a HIK character and attach the skeleton data to this character.
    The stance pose is forced to be the default char pose provided in Maya.

    :param dict skeleton_data:
    :return: HIK character
    :rtype: str
    """
    # create node
    character = "character"
    mel.eval('hikCreateCharacter("{}")'.format(character))

    # create skeleton generator for default pose
    gen = cmds.createNode("HIKSkeletonGeneratorNode")
    mel.eval(
        'hikReadDefaultCharPoseFileOntoSkeletonGeneratorNode("{}")'.format(
            gen
        )
    )

    # define skeleton, need to apply translation twice as the ID order doesn't
    # really guarantee the right order. Doh!
    skeleton.position_skeleton(skeleton_data, gen)
    skeleton.position_skeleton(skeleton_data, gen)

    # add joints to definition
    for _id in sorted(HIK_ID_MAPPER.keys()):
        attribute = HIK_ID_MAPPER.get(_id)
        joint = skeleton_data.get(HIK_MAPPER.get(attribute))

        # set character object
        mel.eval(
            'hikSetCharacterObject("{}", "{}", {}, 0)'.format(
                joint,
                character,
                _id
            )
        )

    # delete gen as data has been written and applied
    # no need for this node anymore
    cmds.delete(gen)

    # lock definition
    mel.eval('hikToggleLockDefinition')

    return character
