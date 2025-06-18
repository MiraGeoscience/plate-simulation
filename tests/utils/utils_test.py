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

from plate_simulation.models.parametric import Plate, PlateOptions
from plate_simulation.utils import azimuth_to_unit_vector, replicate


def test_azimuth_to_unit_vector():
    assert np.allclose(azimuth_to_unit_vector(0.0), np.array([0.0, 1.0, 0.0]))
    assert np.allclose(azimuth_to_unit_vector(90.0), np.array([1.0, 0.0, 0.0]))
    assert np.allclose(azimuth_to_unit_vector(180.0), np.array([0.0, -1.0, 0.0]))
    assert np.allclose(azimuth_to_unit_vector(270.0), np.array([-1.0, 0.0, 0.0]))
    assert np.allclose(azimuth_to_unit_vector(360.0), np.array([0.0, 1.0, 0.0]))


def test_replicate_even(tmp_path):
    workspace = Workspace.create(tmp_path / f"{__name__}.geoh5")
    options = PlateOptions(
        name="test",
        plate=1.0,
        width=1.0,
        strike_length=1.0,
        dip_length=1.0,
        elevation=1.0,
    )
    plate = Plate(options, (0, 0, 0), workspace=workspace)
    plates = replicate(plate, 2, 10.0, 90.0)
    assert plates[0].surface.vertices is not None
    assert plates[1].surface.vertices is not None
    assert plates[0].params.name == "test offset 1"
    assert np.allclose(
        plates[0].surface.vertices.mean(axis=0), np.array([-5.0, 0.0, 0.0])
    )
    assert plates[1].params.name == "test offset 2"
    assert np.allclose(
        plates[1].surface.vertices.mean(axis=0), np.array([5.0, 0.0, 0.0])
    )


def test_replicate_odd(tmp_path):
    workspace = Workspace.create(tmp_path / f"{__name__}.geoh5")
    options = PlateOptions(
        name="test",
        plate=1.0,
        width=1.0,
        strike_length=1.0,
        dip_length=1.0,
        elevation=1.0,
    )
    plate = Plate(options, (0, 0, 0), workspace=workspace)
    plates = replicate(plate, 3, 5.0, 0.0)
    assert plates[0].surface.vertices is not None
    assert plates[1].surface.vertices is not None
    assert plates[2].surface.vertices is not None
    assert np.allclose(
        plates[0].surface.vertices.mean(axis=0), np.array([0.0, -5.0, 0.0])
    )
    assert np.allclose(
        plates[1].surface.vertices.mean(axis=0), np.array([0.0, 0.0, 0.0])
    )
    assert np.allclose(
        plates[2].surface.vertices.mean(axis=0), np.array([0.0, 5.0, 0.0])
    )
