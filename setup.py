#!/usr/bin/env python3
"""
Encrypted Keylogger - Setup Script
A secure, cross-platform keylogger with encryption and stealth capabilities.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="encrypted-keylogger",
    version="4.2.0",
    author="Security Research Team",
    author_email="security@example.com",
    description="A secure, encrypted keylogger with comprehensive logging and analysis tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/encrypted-keylogger",
    packages=find_packages(),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "build": [
            "pyinstaller>=4.0",
            "cx-Freeze>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "keylogger=keylogger:main",
            "keylogger-cli=keylogger_cli:main",
            "klog=keylogger_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="keylogger security monitoring encryption stealth",
    project_urls={
        "Bug Reports": "https://github.com/example/encrypted-keylogger/issues",
        "Source": "https://github.com/example/encrypted-keylogger",
        "Documentation": "https://github.com/example/encrypted-keylogger/docs",
    },
)
