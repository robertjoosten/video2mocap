from maya import cmds


def get_first_valid_frame(frames):
    """
    :param list frames:
    :return: Frame data
    :rtype: dict/None
    """
    for frame in frames:
        if not frame:
            continue

        return frame


def extract_people_sequence(mocap_data):
    """
    Extract all of the matrices for each frame per person. Extracting this
    information will make it possible to simple loop the frames and create
    the mocap data for one person.

    :param dict mocap_data:
    :return: People data
    :rtype: dict
    """
    people = []
    for frame in mocap_data.get("frames"):
        for i, p in enumerate(frame.get("people")):
            if len(people) < i + 1:
                people.append({"frames": []})

            people[i].get("frames").append(p)

    return people


def create_groups(mocap_data):
    """
    Create groups from the matrices coming from the json data. Two additional
    groups are added to make sure a valid skeleton can be created using the
    HIK functionality in maya.

    :param dict mocap_data:
    :return: Group data
    :rtype: dict
    """
    # variable
    groups = {}

    # matrix groups
    for name, matrix in mocap_data.get("matrices_3d").iteritems():
        group = cmds.group(name=name, world=True, empty=True)
        groups[name] = group

    # extra groups
    for name in ["hip", "spine"]:
        group = cmds.group(name=name, world=True, empty=True)
        groups[name] = group

    return groups
