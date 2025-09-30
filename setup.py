from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chain-of-thought",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A debugger for human reasoning processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chain-of-thought",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8',
    install_requires=[
        'spacy>=3.4.0',
        'nltk>=3.6.0',
        'rich>=12.5.1',
        'textblob>=0.17.1',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'chain-of-thought=main:main',
        ],
    },
)
