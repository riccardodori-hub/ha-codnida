from setuptools import setup, find_packages

setup(
    name="ha-codnida",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "homeassistant",
        "aiohttp",
    ],
)