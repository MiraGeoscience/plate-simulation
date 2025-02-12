# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                        '
#                                                                                      '
#  This file is part of plate-simulation package.                                      '
#                                                                                      '
#  plate-simulation is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                         '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoapps_utils.utils.transformations import rotate_xyz
from geoh5py import Workspace

from plate_simulation.models.params import PlateParams
from plate_simulation.models.plates import Plate


def are_collocated(pts1, pts2):
    truth = []
    for loc in pts1:
        truth.append(any(np.allclose(loc, k) for k in pts2))

    return np.all(truth)


def vertical_east_striking_plate(workspace):
    params = PlateParams(
        name="my plate",
        plate=1.0,
        elevation=0.0,
        width=10.0,
        strike_length=1000.0,
        dip_length=500.0,
        dip=90.0,
        dip_direction=0.0,
    )
    plate = Plate(params)

    return plate.create_surface(workspace)


def test_vertical_east_striking_plate(tmp_path):
    workspace = Workspace(tmp_path / "test.geoh5")
    vertical_east_striking = vertical_east_striking_plate(workspace)
    assert vertical_east_striking.vertices is not None
    assert vertical_east_striking.extent is not None
    assert np.isclose(
        vertical_east_striking.extent[1, 0] - vertical_east_striking.extent[0, 0],
        1000.0,
    )
    assert np.isclose(
        vertical_east_striking.extent[1, 1] - vertical_east_striking.extent[0, 1],
        10.0,
    )
    assert np.isclose(
        vertical_east_striking.extent[1, 2] - vertical_east_striking.extent[0, 2],
        500.0,
    )
    assert (
        vertical_east_striking.vertices[:, 0].mean() == 0.0  # pylint: disable=no-member
    )
    assert (
        vertical_east_striking.vertices[:, 1].mean() == 0.0  # pylint: disable=no-member
    )
    assert (
        vertical_east_striking.vertices[:, 2].mean() == 0.0  # pylint: disable=no-member
    )


def test_dipping_plates_all_quadrants(tmp_path):
    workspace = Workspace(tmp_path / "test.geoh5")
    reference = vertical_east_striking_plate(workspace)

    for dip_direction in np.arange(0.0, 361.0, 45.0):
        for dip in [20.0, 70.0]:
            params = PlateParams(
                name=f"plate dipping {dip} at {dip_direction}",
                plate=1.0,
                elevation=0.0,
                width=10.0,
                strike_length=1000.0,
                dip_length=500.0,
                dip=dip,
                dip_direction=dip_direction,
                reference="center",
            )

            plate = Plate(params)
            surface = plate.create_surface(workspace)
            locs = rotate_xyz(surface.vertices, [0.0, 0.0, 0.0], dip_direction, 0.0)
            locs = rotate_xyz(locs, [0.0, 0.0, 0.0], 0.0, dip - 90.0)
            assert np.allclose(locs, reference.vertices)
