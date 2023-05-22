PYRO_KEYS = {
    "beamsplitter": "VAMPIRES_BEAMSPLITTER",
    "camfocus": "VAMPIRES_CAMFOCUS",
    "diffwheel": "VAMPIRES_DIFFWHEEL",
    "filter": "VAMPIRES_FILTER",
    "flc": "VAMPIRES_FLC",
    "focus": "VAMPIRES_FOCUS",
    "mask": "VAMPIRES_MASK",
    "mbi": "VAMPIRES_MBI",
    "qwp1": "VAMPIRES_QWP1",
    "qwp2": "VAMPIRES_QWP2",
    "tc": "VAMPIRES_TC",
    "trigger": "VAMPIRES_TRIGGER",
}

from .vampires_beamsplitter import VAMPIRESBeamsplitter
from .vampires_camfocus import VAMPIRESCamFocus
from .vampires_diffwheel import VAMPIRESDiffWheel
from .vampires_filter import VAMPIRESFilter
from .vampires_flc import VAMPIRESFLCStage
from .vampires_focus import VAMPIRESFocus
from .vampires_mask import VAMPIRESMaskWheel
from .vampires_mbi import VAMPIRESMBIWheel
from .vampires_qwp import VAMPIRESQWP
from .vampires_tc import VAMPIRESTC
from .vampires_trigger import VAMPIRESTrigger

__all__ = [
    "PYRO_KEYS",
    "VAMPIRESBeamsplitter",
    "VAMPIRESCamFocus",
    "VAMPIRESDiffWheel",
    "VAMPIRESFilter",
    "VAMPIRESFLCStage",
    "VAMPIRESFocus",
    "VAMPIRESMaskWheel",
    "VAMPIRESMBIWheel",
    "VAMPIRESQWP",
    "VAMPIRESTC",
    "VAMPIRESTrigger",
]
