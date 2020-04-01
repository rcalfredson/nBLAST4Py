# nBLAST4Py
A high-performance Python implementation of NBLAST neuron search algorithm adapted from the R package nat.nblast (https://github.com/natverse/nat.nblast)

## Setup
### Install Boost.Python
See the project's [GitHub repository](https://github.com/boostorg/python#build) for generic instructions. However, an alternative strategy was needed for installation on a Windows machine using MinGW ([details here](boostPythonWinMinGW.md))
### Install Libnabo
Again, the [GitHub repository](https://github.com/ethz-asl/libnabo#compilation) contains generic instructions; Windows-specific details are [here](libnaboWin.md). Once you have built Pynabo, the library's C extension for Python, then copy it to the DLLs directory of your Python installation, along with any DLLs on which it may depend, chiefly Boost.Python.
