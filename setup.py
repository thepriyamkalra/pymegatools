from pathlib import Path
from setuptools import find_packages, setup

with open(Path(__file__).parent / "README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="pymegatools",
    version="1.0.1",
    author="justaprudev",
    description="Simple Python wrapper for the megatools cmdline utility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justaprudev/pymegatools",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
)