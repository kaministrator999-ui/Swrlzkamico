from setuptools import Extension, setup
import numpy

COMMON_ARGS = ["-O3", "-ffast-math", "-fno-math-errno", "-funroll-loops"]

setup(
    name="swrlzkamico-native",
    version="0.2.0",
    packages=["swyrlz"],
    ext_modules=[
        Extension(
            "swyrlz._r39_native",
            sources=["native/r39_native.c"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=COMMON_ARGS,
        ),
        Extension(
            "swyrlz._r39_batch",
            sources=["native/r39_batch.c"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=COMMON_ARGS,
        ),
    ],
)
