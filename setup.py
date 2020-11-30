import pathlib

import setuptools

# The directory containing this file
TOPLEVEL_DIR = pathlib.Path(__file__).parent.absolute()
ABOUT_FILE = TOPLEVEL_DIR / "pokejdr" / "_version.py"
README = TOPLEVEL_DIR / "README.md"

# Information on the omc3 package
ABOUT_POKEJDR: dict = {}
with ABOUT_FILE.open("r") as f:
    exec(f.read(), ABOUT_POKEJDR)

with README.open("r") as docs:
    long_description = docs.read()

# Dependencies for the package itself
DEPENDENCIES = [
    "numpy>=1.19.0",
    "pandas>=1.0",
    "loguru>=0.5.3",
    "pydantic>=1.7",
]

# Extra dependencies
EXTRA_DEPENDENCIES = {
    "test": [
        "pytest>=5.2",
        "pytest-cov>=2.7",
    ],
}
EXTRA_DEPENDENCIES.update(
    {"all": [elem for list_ in EXTRA_DEPENDENCIES.values() for elem in list_]}
)

setuptools.setup(
    name=ABOUT_POKEJDR["__title__"],
    version=ABOUT_POKEJDR["__version__"],
    description=ABOUT_POKEJDR["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=ABOUT_POKEJDR["__author__"],
    author_email=ABOUT_POKEJDR["__author_email__"],
    url=ABOUT_POKEJDR["__url__"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "pokejdr": ["data/*"],
    },  # Include all files found in the "data" subdirectory
    python_requires=">=3.6",
    license=ABOUT_POKEJDR["__license__"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=DEPENDENCIES,
    tests_require=EXTRA_DEPENDENCIES["test"],
    extras_require=EXTRA_DEPENDENCIES,
)
