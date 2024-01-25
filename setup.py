from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="compression_tester_controls",  # Required
    version="2.0.0",  # Required
    description="poorly made hardware control library",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/dn757657/compression_tester_controls",  # Optional
    packages=find_packages(),  # Required
    py_modules=['trail_protocols'],
    python_requires=">=3.8, <4",
)