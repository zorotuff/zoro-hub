"""
Backward-compatible shim. This module used to have its own JSON-file
profile storage (a duplicate of profiles.py with an incompatible
save_profile signature). It now just delegates to the real,
database-backed implementation in profiles.py, keeping this module's
original one-argument save_profile(profile) contract intact for any
existing caller.
"""

from profiles import get_profile, save_profile as _save_profile


def save_profile(profile):
    return _save_profile(profile["username"], profile)


__all__ = ["get_profile", "save_profile"]
