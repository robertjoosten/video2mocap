from maya import cmds, mel

# load hik
mel.eval("HIKCharacterControlsTool")

# ----------------------------------------------------------------------------


LEG_HIERARCHY = ["hip", "knee", "ankle"]
ARM_HIERARCHY = ["shoulder", "elbow", "wrist"]
BODY_HIERARCHY = ["hip", "spine", "neck", "head"]


# ----------------------------------------------------------------------------


HIK_MAPPER = {
    "Reference": "reference",
    "Hips": "hip",
    "Spine": "spine",
    "Neck": "neck",
    "Head": "head",
    "LeftUpLeg": "l_hip",
    "LeftLeg": "l_knee",
    "LeftFoot": "l_ankle",
    "RightUpLeg": "r_hip",
    "RightLeg": "r_knee",
    "RightFoot": "r_ankle",
    "LeftArm": "l_shoulder",
    "LeftForeArm": "l_elbow",
    "LeftHand": "l_wrist",
    "RightArm": "r_shoulder",
    "RightForeArm": "r_elbow",
    "RightHand": "r_wrist"
}

HIK_ID_MAPPER = {
    cmds.hikGetNodeIdFromName(node): node
    for node in HIK_MAPPER.keys()
}
