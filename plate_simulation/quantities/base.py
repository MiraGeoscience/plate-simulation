#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of plate-simulation package.
#
#  All rights reserved.
#

from abc import ABC
from enum import Enum
from typing import Callable, ClassVar, Any
from pydantic import BaseModel, field_validator, model_validator


class QuantityError(Exception):
    pass

class Conversions:
    """Utility class to store unit conversion functions."""

    @staticmethod
    def null(value):
        return value

    @staticmethod
    def reciprocal(value):
        return 1. / value


class Quantity(BaseModel):
    """
    Abstract Physical quantity with value and conversions.

    Units are added in subclasses.

    :param value: Value given to the model component.
    :unit: Unit of the value.
    :conversion: Function to convert the value to the desired unit.
    """

    value: Any
    conversions: list[Callable] = [Conversions.null]

    @model_validator(mode="after")
    def convert(self):
        for conversion in self.conversions:
            self.value = conversion(self.value)

    @classmethod
    def create(cls, value, unit: str):
        """
        Assemble a Quantity from the factory.

        :param value: data value.
        :param unit: data unit.
        """

        if hasattr(cls, "Units") and unit not in [k.value for k in cls.Units]:
            raise QuantityError(
                f"The provided unit ({unit}) is not supported for {cls.__name__}."
            )

        return QuantityFactory.assemble(value, unit)


class Conductivity(Quantity):
    """Represents a conductivity value with units of S/m."""

    class Units(Enum):
        siemens_per_meter = "S/m"
        ohm_meter = "Ohm*m"

    unit: ClassVar[Units] = Units("S/m")


class Density(Quantity):
    """Represents a density value with units of g/cm3."""

    class Units(Enum):
        grams_per_cc = "g/cc"

    unit: ClassVar[Units] = Units("g/cc")


class QuantityFactory(BaseModel):
    """ Factory to create a Quantity with a specific unit."""

    @staticmethod
    def assemble(value: Any, unit: str) -> Quantity:

        if unit == "Ohm*m":
            return Conductivity(value=value, conversions=[Conversions.reciprocal])
        if unit == "S/m":
            return Conductivity(value=value)
        if unit == "g/cc":
            return Density(value=value)

        raise QuantityError(f"The provided unit ({unit}) is not yet supported.")

