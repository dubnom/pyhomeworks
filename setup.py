import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhomeworks",
    version="0.0.6",
    author="Michael Dubno",
    author_email="michael@dubno.com",
    description="Lutron Homeworks Series 4 and 8 interface over Ethernet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/dubnom/pyhomeworks",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
