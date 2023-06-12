from Pyro4.errors import CommunicationError
from swmain.network.pyroclient import connect

from .vampires_beamsplitter import VAMPIRESBeamsplitter
from .vampires_camfocus import VAMPIRESCamFocus
from .vampires_diffwheel import VAMPIRESDiffWheel
from .vampires_fieldstop import VAMPIRESFieldstop
from .vampires_filter import VAMPIRESFilter
from .vampires_flc import VAMPIRESFLCStage
from .vampires_focus import VAMPIRESFocus
from .vampires_mask import VAMPIRESMaskWheel
from .vampires_mbi import VAMPIRESMBIWheel
from .vampires_pupil import VAMPIRESPupilLens
from .vampires_qwp import VAMPIRESQWP
from .vampires_tc import VAMPIRESTC
from .vampires_trigger import VAMPIRESTrigger


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


__all__ = [
    "VAMPIRESBeamsplitter",
    "VAMPIRESCamFocus",
    "VAMPIRESDiffWheel",
    "VAMPIRESFieldstop",
    "VAMPIRESFilter",
    "VAMPIRESFLCStage",
    "VAMPIRESFocus",
    "VAMPIRESMaskWheel",
    "VAMPIRESMBIWheel",
    "VAMPIRESPupilLens",
    "VAMPIRESQWP",
    "VAMPIRESTC",
    "VAMPIRESTrigger",
]
