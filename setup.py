import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setuptools.setup(
    name="wirinj",
    version=version,
    author="David Cimadevilla",
    author_email="dev.davidcim@gmail.com",
    description="Dependency injection library compatible with IDE inspections and minimal boiler plate code."
                "dessign.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidcim/wirinj",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
