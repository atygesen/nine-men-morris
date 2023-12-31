from glob import glob
from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11

ext_modules = [
    Pybind11Extension(
        "nnm_board",
        glob("cxx/src/*.cpp"),  # Sort source files for reproducibility
        include_dirs=[pybind11.get_include(), "cxx/include/"],
    ),
]

setup(
    name="nine_men_morris",
    version="0.0.1",
    author="Alexander Tygesen",
    description="A test project using pybind11",
    long_description="",
    ext_modules=ext_modules,
    packages=find_packages(),
    install_requires=[
        "pygame",
        "numpy",
    ],
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.10",
)