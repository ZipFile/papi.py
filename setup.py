#!/usr/bin/env python

from distutils.core import setup

setup(
    name="papi.py",
    version="1.1.0",
    description="Unofficial Pixiv's Public API client",
    packages=["papi"],
    package_data={"": ["LICENSE"]},
    package_dir={"papi": "papi"},
    include_package_data=True,
    install_requires=["requests"],
    license="BSD 2-Clause",
)
