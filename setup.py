#!/usr/bin/env python3
"""
Setup script for SecurityExceptionAuditor.

Install:
    pip install -e .

Then use:
    securityaudit --help
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="securityaudit",
    version="1.0.0",
    description="Security Exception Manager for Development Environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FORGE (Team Brain)",
    author_email="logan@metaphy.io",
    url="https://github.com/DonkRonk17/SecurityExceptionAuditor",
    license="MIT",
    
    py_modules=["securityaudit"],
    python_requires=">=3.8",
    
    # No external dependencies!
    install_requires=[],
    
    entry_points={
        "console_scripts": [
            "securityaudit=securityaudit:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    
    keywords=[
        "security",
        "antivirus",
        "firewall",
        "exceptions",
        "whitelist",
        "windows-defender",
        "bitdefender",
        "development",
        "devtools",
    ],
    
    project_urls={
        "Bug Reports": "https://github.com/DonkRonk17/SecurityExceptionAuditor/issues",
        "Source": "https://github.com/DonkRonk17/SecurityExceptionAuditor",
        "Documentation": "https://github.com/DonkRonk17/SecurityExceptionAuditor#readme",
    },
)
