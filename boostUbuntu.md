# Installing Boost.Python on Ubuntu (adapted from [this SO post](https://askubuntu.com/a/1094678))
1. Make sure there is a directory in `/usr/local/include` that corresponds with your targeted version of Python; if not, see the [README](README.md) for a link to instructions for building Python from source, which will ensure Python header files are placed correctly.
2. `cd /usr/src`
3. `sudo wget ${URL_TO_BOOST_TAR_GZ}` (find download URLs [here](https://www.boost.org/users/download/))
4. `sudo tar xzf ${BOOST_TAR_GZ}`
5. `cd ${BOOST_DIR}` (namely, the untarred file from prior step)
6. `sudo ./bootstrap.sh --with-python=$(which $PREFERRED_PYTHON_COMMAND)`
7. `sudo ./b2 install`
8. Then delete the tar file and the source directory if you prefer.
