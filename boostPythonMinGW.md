# Installing Boost.Python on Windows using MinGW
1. Install MinGW by running the installer available [here](http://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win32/Personal%20Builds/mingw-builds/installer/mingw-w64-install.exe/download).
    - If using 64-bit, select x86_64 for "Architecture;" otherwise, use default installation options.
    - Optionally, use the installation path of `C:\MinGW`. Even though it is not the default, it was recommended by the original MinGW developers because they claimed the presence of spaces in the project's paths could cause problems in certain cases (though I do not know more details)
2. Install Boost from one of the installers available [here](https://sourceforge.net/projects/boost/files/boost-binaries/1.72.0/).
    - These binaries were built using the Microsoft Visual C++ Compiler, MSVC, but I found they did not cause a conflict with libraries built on your own system using MinGW, and since the compilation is already completed, there is no need to install MSVC on your system if you do not have it already.
3. Build Boost.Python.
    - Please note that results may vary, because I found these steps temperamental and requiring a fair amount of trial and error.
    - Copy the file `user-config.jam` from directory `boost_VERSION_NUMBER/tools/build/example` to `boost_VERSION_NUMBER/tools/build/src`.
    - In the "Python configuration" section at the very bottom of `user-config.jam`, add a line specifying your Python version and the paths to the interpreter, header files, and library files, respectively, e.g., `using python : 3.6 : "C:/Program\ Files/Python36/python.exe" : "C:/Program\ Files/Python36/include" : "C:/Program\ Files/Python36/libs" ;`.
    - Open an administrator command prompt and change to the base directory of the Boost installation.
    - From there, read [these instructions](https://gist.github.com/zserg/920dad2a3d64549d26d0#file-readme-md) and complete the first two bullets: "Install Boost.Build" and "Build Boost.Python". Ideally, they should work as is, though you may have to experiment with parameters. For example, I did not have to use the `--prefix` arg or modify the environment variable `PATH`. Furthermore, whenever calling the `b2` executable, I needed these arguments: `link=shared toolset=gcc architecture=x86 address-model=64`.
    - If the build succeeded, then inside the directory `boost_VERSION_NUMBER/stage/lib` there should be two DLLs named similarly to `libboost_pythonXx_COMPILER_NAME`, which you will need for the next step: [Installing Libnabo](libnaboWin.md).
