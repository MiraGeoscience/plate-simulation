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
from geoh5py.objects import Surface

from plate_simulation.models.events import Anomaly, Deposition, Erosion, Overburden
from plate_simulation.models.params import PlateParams
from plate_simulation.models.plates import Plate

from . import get_topo_mesh


def test_deposition(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        topography, octree = get_topo_mesh(ws)
        locs = topography.vertices.copy()
        locs[:, 2] -= 5.0
        surface = Surface.create(ws, vertices=locs, cells=topography.cells)

        deposition = Deposition(surface=surface, value=2.0, name="deposition")
        background = np.ones(octree.n_cells)
        event_map = {1: ("Background", 1.0)}
        deposition_model, event_map = deposition.realize(
            mesh=octree, model=background, event_map=event_map
        )
        for event_id, props in event_map.items():
            deposition_model[deposition_model == event_id] = props[1]
        model = octree.add_data({"model": {"values": deposition_model}})

        ind = octree.centroids[:, 2] < -5.0
        assert all(model.values[ind] == 2)
        assert all(model.values[~ind] == 1)


def test_erosion(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        topography, octree = get_topo_mesh(ws)
        erosion = Erosion(surface=topography)
        background = np.ones(octree.n_cells)
        event_map = {1: ("Background", 1.0)}
        erosion_model, event_map = erosion.realize(
            mesh=octree, model=background, event_map=event_map
        )
        for event_id, props in event_map.items():
            erosion_model[erosion_model == event_id] = props[1]
        model = octree.add_data({"model": {"values": erosion_model}})

        ind = octree.centroids[:, 2] < 0.0
        assert all(np.isfinite(model.values[ind]))
        assert all(np.isnan(model.values[~ind]))


def test_overburden(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        topography, octree = get_topo_mesh(ws)
        overburden = Overburden(topography=topography, thickness=5.0, value=2.0)
        background = np.ones(octree.n_cells)
        event_map = {1: ("Background", 1.0)}
        overburden_model, event_map = overburden.realize(
            mesh=octree, model=background, event_map=event_map
        )
        for event_id, props in event_map.items():
            overburden_model[overburden_model == event_id] = props[1]
        model = octree.add_data({"model": {"values": overburden_model}})

        ind = octree.centroids[:, 2] < -5.0
        assert all(model.values[ind] == 1)
        assert all(model.values[~ind] == 2)


def test_anomaly(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as workspace:
        _, octree = get_topo_mesh(workspace)
        params = PlateParams(
            name="my plate",
            plate=10.0,
            elevation=-1.5,
            width=10.0,
            strike_length=10.0,
            dip_length=1.0,
        )
        plate = Plate(params, center_x=5.0, center_y=5.0, center_z=-1.5)
        surface = plate.create_surface(workspace)
        anomaly = Anomaly(surface=surface, value=10.0)
        event_map = {1: ("Background", 1.0)}
        model, event_map = anomaly.realize(
            mesh=octree, model=np.ones(octree.n_cells), event_map=event_map
        )
        for event_id, props in event_map.items():
            model[model == event_id] = props[1]
        data = octree.add_data({"model": {"values": model}})
        ind = (
            (octree.centroids[:, 0] > 0.0)
            & (octree.centroids[:, 0] < 10.0)
            & (octree.centroids[:, 1] > 0.0)
            & (octree.centroids[:, 1] < 10.0)
            & (octree.centroids[:, 2] > -2.0)
            & (octree.centroids[:, 2] < -1.0)
        )
        assert all(data.values[ind] == 10.0)
