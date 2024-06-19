# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                             '
#                                                                                      '
#  This file is part of plate-simulation package.                                      '
#                                                                                      '
#  plate-simulation is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                         '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py.objects import Surface
from geoh5py.ui_json import InputFile
from octree_creation_app.driver import OctreeDriver
from octree_creation_app.params import OctreeParams, default_ui_json


def get_topo_mesh(workspace):
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [10.0, 10.0, 0.0],
            [0.0, 10.0, 0.0],
        ]
    )
    cells = np.array([[0, 1, 2], [0, 2, 3]])

    topography = Surface.create(workspace, name="topo", vertices=vertices, cells=cells)

    kwargs = {
        "geoh5": workspace,
        "objects": topography,
        "u_cell_size": 0.5,
        "v_cell_size": 0.5,
        "w_cell_size": 0.5,
        "horizontal_padding": 10.0,
        "vertical_padding": 10.0,
        "depth_core": 5.0,
        "minimum_level": 4,
        "diagonal_balance": False,
        "Refinement A object": topography.uid,
        "Refinement A levels": "4, 2, 1",
        "Refinement A horizon": True,
    }
    params = OctreeParams(**kwargs)
    params.write_input_file(name="octree.ui.json", path=workspace.h5file.parent)
    driver = OctreeDriver(params)
    octree = driver.run()
    return topography, octree
