from setuptools import Extension, setup
import numpy

setup(
    name="swrlzkamico-native",
    version="0.1.0",
    packages=["swyrlz"],
    ext_modules=[
        Extension(
            "swyrlz._r39_native",
            sources=["native/r39_native.c"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=["-O3", "-ffast-math", "-fno-math-errno"],
        )
    ],
)
