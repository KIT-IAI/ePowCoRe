# Setup.py

from setuptools import setup

setup(
    name="epowcore",
    version="0.1.0",
    description="A converter between different power system model formats and a generic data format.",
    url="",
    author="KIT-IAI-ESA",
    author_email="",
    license="",
    packages=[
        "epowcore",
    ],
    install_requires=[
        "dataclasses",
        "geojson",
        "networkx",
        "matlabengine==9.13.9",
        "matplotlib",
        "scipy",
        "pyyaml",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "mypy",
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
    zip_safe=False,
)
