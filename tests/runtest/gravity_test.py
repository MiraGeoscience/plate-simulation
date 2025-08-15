# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                        '
#                                                                                      '
#  This file is part of plate-simulation package.                                      '
#                                                                                      '
#  plate-simulation is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                         '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py import Workspace
from geoh5py.groups import SimPEGGroup
from simpeg_drivers.options import ActiveCellsOptions
from simpeg_drivers.potential_fields.gravity.options import GravityForwardOptions

from plate_simulation.driver import PlateSimulationDriver
from plate_simulation.mesh.options import MeshOptions
from plate_simulation.models.options import (
    ModelOptions,
    OverburdenOptions,
    PlateOptions,
)
from plate_simulation.options import PlateSimulationOptions

from . import get_survey, get_topography


def test_gravity_plate_simulation(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        topography = get_topography(ws)
        survey = get_survey(ws, 10, 10)

        mesh_params = MeshOptions(
            u_cell_size=10.0,
            v_cell_size=10.0,
            w_cell_size=10.0,
            padding_distance=1500.0,
            depth_core=600.0,
            max_distance=200.0,
        )

        overburden_params = OverburdenOptions(thickness=50.0, overburden=0.2)

        plate_params = PlateOptions(
            name="plate",
            plate=0.5,
            elevation=-250.0,
            width=100.0,
            strike_length=100.0,
            dip_length=100.0,
            dip=0.0,
            dip_direction=0.0,
            reference="center",
        )

        model_params = ModelOptions(
            name="density",
            background=0.0,
            overburden_model=overburden_params,
            plate_model=plate_params,
        )

        active_cells = ActiveCellsOptions(topography_object=topography)
        inputs = {"geoh5": ws, "active_cells": active_cells, "data_object": survey}
        options = GravityForwardOptions.model_construct(
            **inputs,
        )

        gravity_forward = SimPEGGroup.create(ws)
        gravity_forward.options = options.serialize()

        params = PlateSimulationOptions(
            title="test",
            run_command="run",
            geoh5=ws,
            mesh=mesh_params,
            model=model_params,
            simulation=gravity_forward,
        )
        driver = PlateSimulationDriver(params)
        driver.run()

        assert np.nanmax(driver.model.values) == 0.5
