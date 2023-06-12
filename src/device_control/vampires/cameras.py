from Pyro4.errors import CommunicationError

from swmain.network.pyroclient import connect


def connect_cameras():
    vcam1 = vcam2 = None
    try:
        vcam1 = connect("VCAM1")
    except CommunicationError:
        pass
    try:
        vcam2 = connect("VCAM2")
    except CommunicationError:
        pass
    return vcam1, vcam2
