.. _getting_started:

Getting Started
===============

In this section, we will guide you through the installation of **plate-simulation** and it's dependencies inside a
conda environment.

.. contents::

.. toctree::
   :maxdepth: 2

Installation
------------

Install Conda
~~~~~~~~~~~~~

Install Conda for Python 3.10 or higher. Follow this link to download its Windows installer (~140 MB of disk space):

`Miniforge <https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe>`_

.. figure:: /images/getting_started/Miniforge3_Setup-1.png
    :align: center
    :width: 200

.. figure:: /images/getting_started/Miniforge3_Setup-3.png
    :align: center
    :width: 200

Registering the Conda distribution as the default Python 3.10 interpreter is optional.
Preferably uncheck that box if you already have Python 3 installed on your system.

.. note:: We recommend installing **Miniforge**: beyond being smaller,
    it also installs packages from the conda-forge repository by default,
    which has no restriction for commercial use, while both Miniconda and Anaconda distributions use
    the Anaconda repository by default: see `Anaconda Terms of Service <https://www.anaconda.com/terms-of-service>`_ for details.
    In any case, the installation of **plate-simulation** forces the usage of the conda-forge repository,
    and is thus not affected by the Anaconda Terms of Service.

Install **plate-simulation** from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The latest release of **plate-simulation** can be installed from the Python package index (`PyPI <https://pypi.org/project/plate-simulation/>`_)
with ``pip install plate-simulation``.  However, because plate-simulation contains dependencies that will not be
satisfied by the pip installation, we recommend using a conda environment and installing the package
and its few dependencies together.

This is as simple opening a miniforge terminal and running the following commands

.. code-block:: bash

    conda create -n "plate-simulation" python=3.10
    conda activate plate-simulation
    pip install plate-simulation octree-creation-app geoh5py geoapps-utils mira-simpeg param-sweeps simpeg-drivers

This way you will have a *plate-simulation* environment that is already encoded into the ui.json files stored
with the package in the assets folder, and can begin running the programs contained within right away.

To learn more about running from ui.json file, proceed to the :ref:`usage` section.
