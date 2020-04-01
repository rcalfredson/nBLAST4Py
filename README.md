# nBLAST4Py
A high-performance Python implementation of NBLAST neuron search algorithm adapted from the R package nat.nblast (https://github.com/natverse/nat.nblast)

## Setup
### Install Boost.Python
See the project's [GitHub repository](https://github.com/boostorg/python#build) for generic instructions. However, an alternative strategy was needed for installation on a Windows machine using MinGW ([details here](boostPythonWinMinGW.md))
### Install Libnabo
Again, the [GitHub repository](https://github.com/ethz-asl/libnabo#compilation) contains generic instructions; Windows-specific details are [here](libnaboWin.md). Once you have built Pynabo, the library's C extension for Python, then copy it to the DLLs directory of your Python installation, along with any DLLs on which it may depend, chiefly Boost.Python.
### Install Python packages
Either create a virtualenv using the given Pipfile and [`pipenv`](https://github.com/pypa/pipenv), or simply install `numpy`, `feather-format`, and `pandas` system-wide using `pip`.
### Populate `skeletons` directory with SWC files
The neuron database used by this developer was Hemibrain; see the project overview [here](https://www.janelia.org/project-team/flyem/hemibrain) and download the database of 21,663 neurons [here](https://storage.cloud.google.com/hemibrain-release/skeletons.tar.gz).

## Usage
### Prerequisites
- Z-stack image of neurons to query; it must already have undergone registration, using a tool such as [CMTK](https://www.nitrc.org/projects/cmtk/).
- Coordinates in µm of the point in the brain shown here [#so-called anatomical origin of the brain](anatomicalOrigin.png)
