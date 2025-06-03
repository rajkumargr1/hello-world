from setuptools import setup, find_packages

setup(
    name="edi_eda",
    version="0.1.0",
    description="A Python package for Electronic Data Interchange (EDI) Exploratory Data Analysis (EDA)",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here, e.g.,
        # "pandas>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
