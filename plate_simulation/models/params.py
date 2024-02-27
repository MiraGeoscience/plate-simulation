#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of plate-simulation package.
#
#  All rights reserved.
#

from typing import ClassVar
from pydantic import BaseModel, ConfigDict, field_validator

from plate_simulation.quantities import Quantity


class PlateParams(BaseModel):
    """
    Parameters describing an anomalous plate.

    :param name: Name to be given to the geoh5py Surface object
        representing the plate.
    :param anomaly: Plate value in accepted units.
    :param center_x: X-coordinate of the center of the plate.
    :param center_y: Y-coordinate of the center of the plate.
    :param center_z: Z-coordinate of the center of the plate.
    :param width: V-size of the plate.
    :param strike_length: U-size of the plate.
    :param dip_length: W-size of the plate.
    :param dip: Orientation of the u-axis in degree from horizontal.
    :param dip_direction: Orientation of the u axis in degree from north.
    :param reference: Point of rotation to be 'center' or 'top'.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    anomaly: Quantity
    center_x: float
    center_y: float
    center_z: float
    width: float
    strike_length: float
    dip_length: float
    dip: float = 0.0
    dip_direction: float = 0.0
    reference: str = "center"


class OverburdenParams(BaseModel):
    """
    Parameters for the overburden layer.

    :param thickness: Thickness of the overburden layer.
    :param anomaly: Overburden value in accepted units.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    thickness: float
    anomaly: Quantity

    @field_validator("anomaly")
    def flatten(cls, val):
        return val.value



class ModelParams(BaseModel):
    """
    Parameters for the blackground + overburden and plate model.

    :param name: Name to be given to the model
    :param background: Background value in accepted units.
    :param overburden: Overburden layer parameters.
    :param plate: Plate parameters.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    background: Quantity
    overburden: OverburdenParams
    plate: PlateParams
