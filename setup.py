from setuptools import setup, find_packages

setup(
    name="srunit",
    version="0.1",
    packages=find_packages(),
    package_data={"srunit": ["defaults/*"]},
    entry_points={
        "console_scripts": [
            "srunit = srunit:main",
        ],
    },
)
