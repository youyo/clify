#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="clify",
    use_scm_version=True,
    description="OpenAPI仕様からCLIを自動生成するツール",
    author="youyo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
        "requests>=2.25.0",
    ],
    python_requires=">=3.10.0",
    entry_points={
        "console_scripts": [
            "clify=clify.cli:main",
        ],
    },
    setup_requires=["setuptools_scm>=6.2"],
)
