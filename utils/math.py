from __future__ import absolute_import

from math import *
from maya import cmds
from maya.api import OpenMaya


def distance_between(node1, node2):
    """
    Get the distance between two transform nodes in world space.

    :param str node1:
    :param str node2:
    :return: Distance between
    :rtype: float
    """
    point1 = OpenMaya.MVector(cmds.xform(node1, q=True, ws=True, t=True))
    point2 = OpenMaya.MVector(cmds.xform(node2, q=True, ws=True, t=True))

    return (point1 - point2).length()
