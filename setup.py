# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="erbst-dach",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dach-erbst=erbst_dach.cli:main",
        ],
    },
)
