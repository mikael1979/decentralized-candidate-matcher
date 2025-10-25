from .core import DataManagerCore
from .content import ContentMixin
from .ipfs import IPFSMixin
from .elo import EloMixin
from .meta import MetaMixin
from .time_lock import TimeLockMixin

class DataManager(
    DataManagerCore,
    ContentMixin,
    IPFSMixin,
    EloMixin,
    MetaMixin,
    TimeLockMixin
):
    """Yhdistetty DataManager-luokka kaikilla toiminnallisuuksilla"""
    pass
