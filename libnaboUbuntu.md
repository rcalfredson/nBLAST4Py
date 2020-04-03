# Building Libnabo on Ubuntu
1. Ensure Numpy is installed for the version of Python you plan to use with `nBLAST4Py`.
2. Download `eigen` C++ header library:

        cd /usr/local/include
        sudo git clone https://gitlab.com/libeigen/eigen.git
3. Clone the [Libnabo repository from GitHub](https://github.com/ethz-asl/libnabo#download) to your local machine.
4. In the file `python/CMakeLists.txt` in the Libnabo source, on [the line beginning `find_package(Boost`](https://github.com/ethz-asl/libnabo/blob/d4f45e2b2f9b811344cd5002346b9fb52ac2520e/python/CMakeLists.txt#L46), change `${BOOST_PYTHON_COMPONENT}` to the Python version tag associated with your build of Boost.Python, e.g., `python38`. Ideally, this step would not be needed, but when I ran CMake, `BOOST_PYTHON_COMPONENT` got set to `python3`, which was not associated with a library.
5. Run the sequence of commands from the [official instructions](https://github.com/ethz-asl/libnabo#quick-compilation-and-installation-under-unix) (here slightly modified)

        SRC_DIR=`pwd`
        BUILD_DIR=${SRC_DIR}/build
        mkdir -p ${BUILD_DIR} && cd ${BUILD_DIR}
        cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DPYTHON_VERSION_MAJOR=$REPLACE -DPYTHON_VERSION_MINOR=$REPLACE ${SRC_DIR}
        make
        sudo make install
