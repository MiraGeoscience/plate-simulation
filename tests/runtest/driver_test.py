# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                        '
#                                                                                      '
#  This file is part of plate-simulation package.                                      '
#                                                                                      '
#  plate-simulation is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                         '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from copy import deepcopy
from pathlib import Path
from uuid import UUID

import numpy as np
from geoh5py import Workspace
from geoh5py.groups import SimPEGGroup
from geoh5py.objects import AirborneTEMReceivers, ObjectBase, Octree, Surface
from geoh5py.ui_json import InputFile
from simpeg_drivers.electromagnetics.time_domain.constants import (
    default_ui_json as tdem_default_ui_json,
)
from simpeg_drivers.potential_fields.gravity.constants import (
    default_ui_json as gravity_default_ui_json,
)

from plate_simulation import assets_path
from plate_simulation.driver import PlateSimulationDriver, PlateSimulationParams
from plate_simulation.mesh.params import MeshParams
from plate_simulation.models.params import ModelParams

from . import get_survey, get_topography


# pylint: disable=duplicate-code


def get_simulation_group(workspace: Workspace, survey: ObjectBase, topography: Surface):
    tem_inversion = SimPEGGroup.create(workspace)
    options = deepcopy(InputFile.stringify(tdem_default_ui_json))
    options["inversion_type"] = "tdem"
    options["forward_only"] = True
    options["geoh5"] = str(workspace.h5file)
    options["topography_object"]["value"] = str(topography.uid)
    options["data_object"]["value"] = str(survey.uid)
    options["x_channel_bool"] = True
    options["y_channel_bool"] = True
    options["z_channel_bool"] = True
    tem_inversion.options = options

    return tem_inversion


def get_input_file(filepath: Path) -> InputFile:
    with Workspace(filepath / "test.geoh5") as ws:
        with Workspace(assets_path() / "demo.geoh5", mode="r") as demo_workspace:
            survey = demo_workspace.get_entity("Simulation rx")[0].copy(
                parent=ws, copy_children=False
            )
            topography = demo_workspace.get_entity("Topography")[0].copy(parent=ws)
            mask = np.zeros(survey.n_vertices, dtype=bool)
            mask[::10] = True
            new_survey = survey.copy(mask=mask, cell_mask=mask[:-1])

        simulation = get_simulation_group(ws, new_survey, topography)
        ifile = InputFile.read_ui_json(
            assets_path() / "uijson" / "plate_simulation.ui.json", validate=False
        )
        ifile.set_data_value("name", "test_tem_plate_simulation")
        ifile.set_data_value("geoh5", ws)
        ifile.set_data_value("simulation", simulation)
        ifile.set_data_value("u_cell_size", 50.0)
        ifile.set_data_value("v_cell_size", 50.0)
        ifile.set_data_value("w_cell_size", 50.0)
        ifile.set_data_value("depth_core", 600.0)
        ifile.set_data_value("max_distance", 200.0)
        ifile.set_data_value("padding_distance", 1000.0)
        ifile.set_data_value("background", 2000.0)
        ifile.set_data_value("overburden", 7500.0)
        ifile.set_data_value("thickness", 50.0)
        ifile.set_data_value("plate", 20.0)
        ifile.set_data_value("width", 100.0)
        ifile.set_data_value("strike_length", 1000.0)
        ifile.set_data_value("dip_length", 300.0)
        ifile.set_data_value("dip", 65.0)
        ifile.set_data_value("dip_direction", 65.0)
        ifile.set_data_value("number", 2)
        ifile.set_data_value("spacing", 600.0)
        ifile.set_data_value("relative_locations", True)
        ifile.set_data_value("easting", 100.0)
        ifile.set_data_value("northing", 100.0)
        ifile.set_data_value("elevation", -100.0)
        ifile.set_data_value("reference_surface", "overburden")
        ifile.set_data_value("reference_type", "min")

    return ifile


def test_plate_simulation(tmp_path):
    ifile = get_input_file(tmp_path)
    ifile.write_ui_json("test_plate_simulation.ui.json", path=tmp_path)
    result = PlateSimulationDriver.start(
        Path(tmp_path / "test_plate_simulation.ui.json")
    )
    with Workspace(result.out_group.options["geoh5"]) as ws:
        out_group = ws.get_entity(UUID(result.out_group.options["out_group"]["value"]))[
            0
        ]
        data = next(
            obj for obj in out_group.children if isinstance(obj, AirborneTEMReceivers)
        )
        mesh = next(obj for obj in out_group.children if isinstance(obj, Octree))
        model = next(k for k in mesh.children if k.name == "starting_model")
        assert data.property_groups is not None
        assert len(data.property_groups) == 3
        assert all(
            k.name in [f"Iteration_0_{i}" for i in "xyz"] for k in data.property_groups
        )
        assert all(
            k.properties is not None and len(k.properties) == 20
            for k in data.property_groups
        )
        assert mesh.n_cells == 14555
        assert len(np.unique(model.values)) == 4
        assert all(k in np.unique(model.values) for k in [7500, 2000, 20])
        assert any(np.isnan(np.unique(model.values)))


# pylint: disable=too-many-statements
def test_plate_simulation_params_from_input_file(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        topography = get_topography(ws)
        survey = get_survey(ws, 10, 10)

        ifile = InputFile.read_ui_json(
            assets_path() / "uijson" / "plate_simulation.ui.json", validate=False
        )
        ifile.data["name"] = "test_gravity_plate_simulation"
        ifile.data["geoh5"] = ws

        # Add simulation parameter
        gravity_inversion = SimPEGGroup.create(ws)
        options = deepcopy(gravity_default_ui_json)
        options["inversion_type"] = "gravity"
        options["forward_only"] = True
        options["geoh5"] = str(ws.h5file)
        options["topography_object"]["value"] = str(topography.uid)
        options["data_object"]["value"] = str(survey.uid)
        gravity_inversion.options = options
        ifile.data["simulation"] = gravity_inversion

        # Add mesh parameters
        ifile.data["u_cell_size"] = 10.0
        ifile.data["v_cell_size"] = 10.0
        ifile.data["w_cell_size"] = 10.0
        ifile.data["depth_core"] = 400.0
        ifile.data["minimum_level"] = 8
        ifile.data["max_distance"] = 200.0
        ifile.data["diagonal_balance"] = False
        ifile.data["padding_distance"] = 1500.0

        # Add model parameters
        ifile.data["background"] = 1000.0
        ifile.data["overburden"] = 5.0
        ifile.data["thickness"] = 50.0
        ifile.data["plate"] = 2.0
        ifile.data["width"] = 100.0
        ifile.data["strike_length"] = 100.0
        ifile.data["dip_length"] = 100.0
        ifile.data["dip"] = 0.0
        ifile.data["dip_direction"] = 0.0
        ifile.data["number"] = 9
        ifile.data["spacing"] = 10.0
        ifile.data["relative_locations"] = True
        ifile.data["easting"] = 10.0
        ifile.data["northing"] = 10.0
        ifile.data["elevation"] = -250
        ifile.data["reference_surface"] = "topography"
        ifile.data["reference_type"] = "mean"

        params = PlateSimulationParams.build(ifile)
        assert isinstance(params.simulation, SimPEGGroup)

        simulation_parameters = params.simulation_parameters()

        assert simulation_parameters.inversion_type == "gravity"
        assert simulation_parameters.forward_only
        assert simulation_parameters.geoh5.h5file == ws.h5file
        assert simulation_parameters.topography_object.uid == topography.uid
        assert simulation_parameters.data_object.uid == survey.uid

        assert isinstance(params.mesh, MeshParams)
        assert params.mesh.u_cell_size == 10.0
        assert params.mesh.v_cell_size == 10.0
        assert params.mesh.w_cell_size == 10.0
        assert params.mesh.depth_core == 400.0
        assert params.mesh.max_distance == 200.0
        assert params.mesh.padding_distance == 1500.0
        assert params.mesh.minimum_level == 8
        assert not params.mesh.diagonal_balance

        assert isinstance(params.model, ModelParams)
        assert params.model.name == "test_gravity_plate_simulation"
        assert params.model.background == 1000.0
        assert params.model.overburden.thickness == 50.0
        assert params.model.overburden.overburden == 5.0
        assert params.model.plate.plate == 2.0
        assert params.model.plate.width == 100.0
        assert params.model.plate.strike_length == 100.0
        assert params.model.plate.dip_length == 100.0
        assert params.model.plate.dip == 0.0
        assert params.model.plate.dip_direction == 0.0

        assert params.model.plate.number == 9
        assert params.model.plate.spacing == 10.0
        assert params.model.plate.relative_locations
        assert params.model.plate.easting == 10.0
        assert params.model.plate.northing == 10.0
        assert params.model.plate.elevation == -250.0
