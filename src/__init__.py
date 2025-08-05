"""
Encrypted Keylogger Package
A secure, cross-platform keylogger with encryption and comprehensive analysis tools.
"""

__version__ = "4.2.0"
__author__ = "Security Research Team"
__email__ = "security@example.com"
__description__ = "A secure, encrypted keylogger with comprehensive logging and analysis tools"

# Package metadata
PACKAGE_NAME = "encrypted-keylogger"
PROJECT_URL = "https://github.com/example/encrypted-keylogger"
DOCUMENTATION_URL = "https://github.com/example/encrypted-keylogger/docs"

# Supported platforms
SUPPORTED_PLATFORMS = ["Windows", "macOS", "Linux"]

# Required Python version
MIN_PYTHON_VERSION = (3, 6)

# Core modules
from . import keylogger
from . import keylogger_cli
from . import log_utils

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "keylogger",
    "keylogger_cli", 
    "log_utils",
]
