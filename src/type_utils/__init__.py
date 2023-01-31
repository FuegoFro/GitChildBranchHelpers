import sys

MYPY = False

if sys.version_info[0] >= 3:
    from type_utils.abc_py3 import _ABC as ABC
else:
    from type_utils.abc_py2 import _ABC as ABC

__all__ = ["ABC", "MYPY"]
