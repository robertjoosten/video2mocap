from maya import cmds


def applyEulerFilter(transforms):
    """
    Apply an euler filter to fix euler issues on curves connected to the
    transforms rotation attributes.

    :param list transforms: Path to transforms
    """
    # get anim curves connected to the rotate attributes
    rotationCurves = []

    # loop transforms
    for transform in transforms:
        # loop channels
        for channel in ["X", "Y", "Z"]:
            # variables
            node = "{0}.rotate{1}".format(transform, channel)

            # get connected animation curve
            rotationCurves.extend(
                cmds.listConnections(
                    node,
                    type="animCurve",
                    destination=False
                ) or []
            )

    # apply euler filter
    if rotationCurves:
        cmds.filterCurve(*rotationCurves, filter="euler")