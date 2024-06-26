from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="compression_tester_controls",  # Required
    version="2.1.7",  # Required
    description="poorly made hardware control library",  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/dn757657/compression_tester_controls",  # Optional
    packages=find_packages(where='src'),  # Required
    package_data={
        'compression_tester_controls.components': ['configs/*.json'],
    },
    package_dir={"": "src"},
    python_requires=">=3.8, <4",
)
