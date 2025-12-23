#!/usr/bin/env python3
"""
Setup script for Jarvis Assistant
License: MIT
Author: its4yus4
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="jarvis-assistant",
    version="2.1.0",
    author="its4yus4",
    author_email="",  # Add your email
    description="Voice-activated personal assistant for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/its4yus4/jarvis-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jarvis=jarvis:main",
        ],
    },
    include_package_data=True,
    keywords="voice assistant jarvis macos automation",
    project_urls={
        "Bug Reports": "https://github.com/its4yus4/jarvis-assistant/issues",
        "Source": "https://github.com/its4yus4/jarvis-assistant",
        "License": "https://github.com/its4yus4/jarvis-assistant/blob/main/LICENSE",
    },
    license="MIT",
)
