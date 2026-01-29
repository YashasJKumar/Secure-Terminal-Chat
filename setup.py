"""
Setup configuration for Secure Terminal Chat Application.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="secure-terminal-chat",
    version="1.0.0",
    author="Secure Chat Team",
    description="A secure terminal-based chat application with end-to-end encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YashasJKumar/Secure-Terminal-Chat",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Security :: Cryptography",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "secure-chat=main:main",
        ],
    },
    keywords="chat encryption security terminal peer-to-peer e2e",
    project_urls={
        "Bug Reports": "https://github.com/YashasJKumar/Secure-Terminal-Chat/issues",
        "Source": "https://github.com/YashasJKumar/Secure-Terminal-Chat",
    },
)
