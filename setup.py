from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pcg_benchmark',
      version='0.1.0',
      install_requires=['gym', 'numpy>=1.22', 'pillow'],
      author="Ahmed Khalifa",
      author_email="ahmed@akhalifa.com",
      description="A package for \"Procedural Content Generation Benchmark\" to test and compare your pcg algorithm against each other.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/amidos2006/pcg-benchmark",
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      packages=['pcg_benchmark'],
)