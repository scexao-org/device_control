PYRO_KEYS = {
    "beamsplitter": "VAMPIRES_BEAMSPLITTER",
    "focus": "VAMPIRES_FOCUS",
    "camfocus": "VAMPIRES_CAMFOCUS",
    "diffwheel": "VAMPIRES_DIFFWHEEL",
    "mask": "VAMPIRES_MASK",
    "qwp1": "VAMPIRES_QWP1",
    "qwp2": "VAMPIRES_QWP2",
    "filter": "VAMPIRES_FILTER",
    "tc": "VAMPIRES_TC",
}

from .vampires_beamsplitter import VAMPIRESBeamsplitter
from .vampires_camfocus import VAMPIRESCamFocus
from .vampires_diffwheel import VAMPIRESDiffWheel
from .vampires_filter import VAMPIRESFilter
from .vampires_focus import VAMPIRESFocus
from .vampires_mask import VAMPIRESMaskWheel
from .vampires_tc import VAMPIRESTC
from .vampires_qwp import VAMPIRESQWP
from .vampires_trigger import VAMPIRESTrigger

__all__ = [
    "PYRO_KEYS",
    "VAMPIRESBeamsplitter",
    "VAMPIRESCamFocus",
    "VAMPIRESDiffWheel",
    "VAMPIRESFilter",
    "VAMPIRESFocus",
    "VAMPIRESMaskWheel",
    "VAMPIRESTC",
    "VAMPIRESQWP",
    "VAMPIRESTrigger",
]
