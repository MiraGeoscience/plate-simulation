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
from typing import ClassVar

from geoapps_utils.driver.data import BaseData
from geoh5py.groups import SimPEGGroup, UIJsonGroup
from geoh5py.ui_json import InputFile
from simpeg_drivers.electricals.direct_current.three_dimensions.params import (
    DirectCurrent3DParams,
)
from simpeg_drivers.electromagnetics.frequency_domain.params import (
    FrequencyDomainElectromagneticsParams,
)
from simpeg_drivers.electromagnetics.time_domain.params import (
    TimeDomainElectromagneticsParams,
)
from simpeg_drivers.natural_sources.magnetotellurics.params import (
    MagnetotelluricsParams,
)
from simpeg_drivers.natural_sources.tipper.params import TipperParams
from simpeg_drivers.params import InversionBaseParams
from simpeg_drivers.potential_fields.gravity.params import GravityParams
from simpeg_drivers.potential_fields.magnetic_vector.params import (
    MagneticVectorParams,
)

from . import assets_path
from .mesh.params import MeshParams
from .models.params import ModelParams


PARAM_MAP = {
    "gravity": GravityParams,
    "tdem": TimeDomainElectromagneticsParams,
    "fem": FrequencyDomainElectromagneticsParams,
    "magnetotellurics": MagnetotelluricsParams,
    "direct current 3d": DirectCurrent3DParams,
    "magnetic vector": MagneticVectorParams,
    "tipper": TipperParams,
}


class PlateSimulationParams(BaseData):
    """
    Parameters for the plate simulation driver.

    geoh5: Workspace in which the model will be built and results stored.
    mesh: Parameters for the octree mesh.
    model: Parameters for the background + overburden and plate model.
    simulation: Simpeg group containing simulation options and a survey.  Any
        mesh or starting model selections will be replaced by the objects
        created by the driver.
    """

    name: ClassVar[str] = "plate_simulation"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/plate_simulation.ui.json"
    title: ClassVar[str] = "Plate Simulation"
    run_command: ClassVar[str] = "plate_simulation.driver"
    out_group: UIJsonGroup | None = None

    mesh: MeshParams
    model: ModelParams
    simulation: SimPEGGroup

    def simulation_parameters(self) -> InversionBaseParams:
        """
        Create SimPEG parameters from the simulation options.

        A new SimPEGGroup is created inside the out_group to store the
        result of the forward simulation.
        """
        simulation_options = deepcopy(self.simulation.options)
        simulation_options["geoh5"] = self.geoh5

        input_file = InputFile(ui_json=simulation_options, validate=False)
        if input_file.ui_json is None:
            raise ValueError("Input file must have ui_json set.")

        input_file.ui_json["mesh"]["value"] = None

        if input_file.data is None:
            raise ValueError("Input file data must be set.")

        if input_file.data["inversion_type"] in PARAM_MAP:
            return PARAM_MAP[input_file.data["inversion_type"]](
                input_file, validate=False
            )

        raise NotImplementedError(
            f"Unknown inversion type: {input_file.data['inversion_type']}"
        )
