#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of plate-simulation package.
#
#  All rights reserved.
#

import pytest

from plate_simulation.quantities.base import QuantityFactory, Quantity, Conductivity, Density, QuantityError


def test_quantity_factory():

    quantity = QuantityFactory.assemble(0.001, "S/m")
    assert isinstance(quantity, Conductivity)
    quantity = QuantityFactory.assemble(1000.0, "Ohm*m")
    assert isinstance(quantity, Conductivity)
    quantity = QuantityFactory.assemble(0.001, "g/cc")
    assert isinstance(quantity, Density)
    with pytest.raises(QuantityError, match="The provided unit \(nogood\) is not yet supported."):
        QuantityFactory.assemble(0.001, "nogood")


def test_quantity():
    quantity = Quantity.create(0.001, "S/m")
    assert quantity.value == 0.001
    assert isinstance(quantity, Conductivity)
    quantity = Quantity.create(1000.0, "Ohm*m")
    assert quantity.value == 0.001
    assert isinstance(quantity, Conductivity)
    quantity = Quantity.create(0.001, "g/cc")
    assert quantity.value == 0.001
    assert isinstance(quantity, Density)

def test_conductivity():

    cond = Conductivity.create(0.001, "S/m")
    assert cond.value == 0.001
    cond = Conductivity.create(1000.0, "Ohm*m")
    assert cond.value == 0.001
    with pytest.raises(
        QuantityError,
        match="The provided unit \(g/cc\) is not supported for Conductivity."
    ):
        Conductivity.create(0.001, "g/cc")

def test_density():

    dens = Density.create(0.001, "g/cc")
    assert dens.value == 0.001
    with pytest.raises(
        QuantityError,
        match="The provided unit \(S/m\) is not supported for Density."
    ):
        Density.create(0.001, "S/m")