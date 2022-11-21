Prerequisites
-------------

The installation of Python (and its developing packages) differs from operating system to operating system. Optional Git is needed if a package is installed directly from GitHub.

### Linux

On Linux, Python3 is probably already installed, but the development packages are usually not. Optionally, Git can be installed as well. You should be able to install all prerequisites using:

```
# Ubuntu/Debian
sudo apt-get install python3 python3-dev python3-venv
sudo apt-get install git

# CentOS/RHEL
sudo yum install python3 python3-devel
sudo yum install git

# openSUSE/SLES
sudo zypper install python3 python3-devel
sudo zypper install git
```

### macOS

While we reccoment using [Homebrew](https://brew.sh) to install Python3 on a Mac, other means of obtaining Python like [Anaconda](https://www.anaconda.com/products/individual), [MacPorts](https://www.macports.org/), or [Fink](https://www.finkproject.org/) should work just as fine:

```
brew install python
brew install git
```

### Windows

#### Regular installation

The software prerequisites need to be downloaded and installed from their particular web sites.

For python:
* download from <https://www.python.org/downloads/windows/>
* use the 64bit version if your system is not very old
* **don't forget to check 'Add Python to PATH' during setup**

For git:
* download from <https://git-for-windows.github.io/>
* use the 64bit version if your system is not very old

All further steps need to be performed using the windows shell `cmd.exe`. You can open it from the Start-Menu.

#### Using the Windows Subsystem for Linux (WSL)

As an alternative for advanced users, you can use the Windows Subsystem for Linux (WSL) to install a Linux distribution whithin Windows 10. The installation is explained in the [Microsoft documentation](https://docs.microsoft.com/en-us/windows/wsl/install-win10). When using WSL, please install Python3 as explained in the Linux section.
