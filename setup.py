from setuptools import Extension, setup
import os
import numpy

COMMON_ARGS = ["-O3", "-ffast-math", "-fno-math-errno", "-funroll-loops"]
# Vercel's production builder is Linux/GCC-compatible. Keep the native
# parallelism build-selectable so local/non-OpenMP builders can still compile
# the serial correctness path with SWYRLZ_OPENMP=0.
USE_OPENMP = os.environ.get("SWYRLZ_OPENMP", "1") not in {"0", "false", "False"}
OPENMP_COMPILE = ["-fopenmp"] if USE_OPENMP else []
OPENMP_LINK = ["-fopenmp"] if USE_OPENMP else []

setup(
    name="swrlzkamico-native",
    version="0.2.1",
    packages=["swyrlz"],
    ext_modules=[
        Extension(
            "swyrlz._r39_native",
            sources=["native/r39_native.c"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=COMMON_ARGS + OPENMP_COMPILE,
            extra_link_args=OPENMP_LINK,
        ),
        Extension(
            "swyrlz._r39_batch",
            sources=["native/r39_batch.c"],
            include_dirs=[numpy.get_include()],
            extra_compile_args=COMMON_ARGS + OPENMP_COMPILE,
            extra_link_args=OPENMP_LINK,
        ),
    ],
)
