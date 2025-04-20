"""
clify - OpenAPI仕様からCLIを自動生成するツール
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("clify")
except PackageNotFoundError:
    # パッケージがインストールされていない場合
    try:
        from ._version import version as __version__
    except ImportError:
        __version__ = "unknown"

__all__ = ["__version__"]
