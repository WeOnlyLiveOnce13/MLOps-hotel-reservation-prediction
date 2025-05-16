from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="hotel-reservation-mlops",
    version="0.1",
    author="Dan-Tshisungu",
    packages=find_packages(),
    install_requires = requirements,
)