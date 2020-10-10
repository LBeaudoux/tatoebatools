import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tatoebatools",
    version="0.0.7",
    author="L.Beaudoux",
    description="A library for downloading and reading data from Tatoeba",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/l-bdx/tatoebatools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "pandas>=1.1.1",
        "requests>=2.23.0",
        "tqdm>=4.46.0",
    ],
)
