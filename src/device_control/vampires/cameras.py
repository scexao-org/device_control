from swmain.network.pyroclient import connect


def connect_cameras():
    try:
        vcam1 = connect("VCAM1")
        vcam1.get_tint()
    except Exception:
        vcam1 = None
    try:
        vcam2 = connect("VCAM2")
        vcam2.get_tint()
    except Exception:
        vcam2 = None
    return vcam1, vcam2
