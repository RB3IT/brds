import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BRDSolution-RB3IT",
    version="0.0.1",
    author="RB3IT",
    author_email="",
    description="BRDSolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdamantLife/alcustoms",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "openpyxl",
        "xlrd",
        "git+https://github.com/AdamantLife/alcustoms"
        ]
)
