import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tatoebatools",
    version="0.2.2",
    author="L.Beaudoux",
    description="A library for downloading and reading data from Tatoeba",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LBeaudoux/tatoebatools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8.0",
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "pandas>=1.5.0",
        "requests>=2.23.0",
        "SQLAlchemy==1.4.23",
        "tqdm>=4.46.0",
    ],
)
