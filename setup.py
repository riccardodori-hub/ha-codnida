from setuptools import setup, find_namespace_packages

setup(
    name="ha-codnida",
    version="0.1.0",
    packages=find_namespace_packages(include=['custom_components.*']),
    package_data={
        "custom_components.codnida": ["manifest.json"]
    },
)