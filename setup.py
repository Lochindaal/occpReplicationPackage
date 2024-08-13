from setuptools import setup, find_packages

setup(
    name="occp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mona",
    ],
    py_modules=["occp"],
    python_requires=">=3.7",
)
