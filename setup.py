from distutils.core import setup
from distutils.extension import Extension
import platform
import os
import sys
import subprocess

# Set to true to enable line profiling
line_debug = False

#The following try-catch statements ensure numpy and cython are installed prior to running setup.py
#in some virtual environments, pip dependencies have issues with cython packages.
#NUMPY CHECK
try:
    from numpy import get_include
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    from numpy import get_include
#CYTHON CHECK
try:
    from Cython.Build import cythonize
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cython"])
    from Cython.Build import cythonize


#Load the readme as a long description
with open('README.md') as fp:
    long_description = fp.read()

# Compile Cython
try:
    numpyInclude = [get_include(), '.']

    #Install Bioscrape Core Package
    package_data = {'bioscrape': ['*.pxd']}
    bioscrape_src_dir = 'bioscrape'

    ext_options = {}
    ext_options['language'] = 'c++'
    ext_options['include_dirs'] = numpyInclude
    if platform.system() == "Darwin":
        ext_options['extra_compile_args'] = ['-std=c++11', "-mmacosx-version-min=10.9"]
        ext_options['extra_link_args'] = ["-stdlib=libc++", "-mmacosx-version-min=10.9"]
        print('Using macOS clang args')
    if line_debug:
        ext_options['define_macros'] = [('CYTHON_TRACE_NOGIL', '1')]

    #used to generate HTML annotations of the cython code for
    #optimization purposes.
    cythonize_options = {
    "include_path":[bioscrape_src_dir],
    "language_level":"2" #Language level 3 does not work yet
    }
    if "annotate" in sys.argv:
        cythonize_options['annotate'] = True
        sys.argv.remove("annotate")
    if line_debug:
        cythonize_options["compiler_directives"] = {
            'profile': True,
            'linetrace': True,
            'binding': True
        }

    # # Turn on to enable gdb debugging
    # cythonize_options["gdb_debug"] = True

    #Determine if we install bioscrape, lineage, or both
    install_bioscrape = False
    install_lineage = False
    if "bioscrape" not in sys.argv and "lineage" not in sys.argv:
        install_bioscrape = True
        install_lineage = True
    if "bioscrape" in sys.argv:
        install_bioscrape = True
        sys.argv.remove("bioscrape")
    if "lineage" in sys.argv:
        install_lineage = True
        sys.argv.remove("lineage")

    elif "bioscrape" not in sys.argv:
        install_lineage = True

    cython_extensions = []
    if install_bioscrape:
        print("Installing Bioscrape...")
        bioscrape_source_files = ['random.pyx', 'types.pyx', 'simulator.pyx', 'inference.pyx']
        bioscrape_extensions = [
                Extension(
                    name = 'bioscrape.'+s.split('.')[0],
                    sources = [bioscrape_src_dir+'/'+s],
                    **ext_options) for s in bioscrape_source_files
            ]
        cython_extensions += cythonize(bioscrape_extensions, **cythonize_options)
        print("Bioscrape Cythonized.")

    if install_lineage:
        package_data['lineage'] = ['*.pxd']
        print("Installing Lineage...")
        lineage_src_dir = 'lineage'
        lineage_source_files = ['lineage.pyx']
        lineage_extensions = [
            Extension(name = 'bioscrape.'+s.split('.')[0],
                sources = [lineage_src_dir+'/'+s],
                **ext_options) for s in lineage_source_files
        ]
        cython_extensions += cythonize(lineage_extensions, **cythonize_options)
        print("Lineage Cythonized.")

except Exception as e:
    print("Error occured during Cython Compilation. Check C++ Compiler and Cython Installation.")
    raise

setup(
    name = 'bioscrape',
    version = '1.2.1',
    author='Anandh Swaminathan, William Poole, Ayush Pandey',
    url='https://github.com/biocircuits/bioscrape/',
    description='Biological Stochastic Simulation of Single Cell Reactions and Parameter Estimation.',
    long_description=long_description,
    packages = ['bioscrape'],
    package_dir = {'bioscrape' : bioscrape_src_dir},
    package_data = package_data,
    ext_modules = cython_extensions,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
    ],
    setup_requires = [
        "numpy",
        "cython",
        ],
    install_requires=[
        "numpy",
        "matplotlib",
        "pytest",
        "scipy",
        "cython",
        "python-libsbml",
        "beautifulsoup4",
        "sympy",
        "emcee",
        "pandas"
    ],
    python_requires='>=3.6',
    keywords="SBML synthetic biology modeling Chemical Reaction Network CRN simulator stochastic parameter inference",
    tests_require=["pytest"],
    project_urls={
    'Documentation': 'https://github.com/biocircuits/bioscrape/wiki',
    'Funding': 'http://www.cds.caltech.edu/~murray/wiki/DARPA_BioCon',
    'Source': 'https://github.com/biocircuits/bioscrape/',
    'Tracker': 'https://github.com/biocircuits/bioscrape/issues',
    }
)
