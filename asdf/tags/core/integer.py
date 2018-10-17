# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from numbers import Integral

import numpy as np

from ...asdftypes import AsdfType
from ...yamlutil import custom_tree_to_tagged_tree


class IntegerType(AsdfType):
    """
    Enables the storage of arbitrarily large integer values

    The ASDF Standard mandates that integer literals in the tree can be no
    larger than 52 bits. Use of this class enables the storage of arbitrarily
    large integer values.

    When reading files that contain arbitrarily large integers, the values that
    are restored in the tree will be raw Python `int` instances.

    Parameters
    ----------

    value: `numbers.Integral`
        A Python integral value (e.g. `int` or `numpy.integer`)

    Examples
    --------

    >>> import asdf
    >>> import random
    >>> # Create a large integer value
    >>> largeval = random.getrandombits(100)
    >>> # Store the large integer value to the tree using asdf.IntegerType
    >>> tree = dict(largeval=Asdf.IntegerType(largeval))
    >>> with asdf.AsdfFile(tree) as af:
    ...     af.write_to('largeval.asdf')
    >>> with asdf.open('largeval.asdf') as aa:
    ...     assert aa['largeval'] == largeval
    """

    name = 'core/integer'
    version = '1.0.0'

    def __init__(self, value):
        self._value = value
        self._sign = '-' if value < 0 else '+'

    @classmethod
    def to_tree(cls, node, ctx):
        # pack integer value into 32-bit words
        words = []
        value = int(np.abs(node._value))
        while value > 0:
            words.append(value & 0xffffffff)
            value >>= 32

        tree = dict()
        array = np.array(words, dtype=np.uint32)
        tree['words'] = custom_tree_to_tagged_tree(np.array(words), ctx)
        tree['sign'] = node._sign

        return tree

    @classmethod
    def from_tree(cls, tree, ctx):

        value = 0
        for x in tree['words'][::-1]:
            value <<= 32
            value |= int(x)

        if tree['sign'] == '-':
            value = -value

        return value

    def __eq__(self, other):
        if isinstance(other, Integral):
            return self._value == other
        elif isinstance(other, IntegerType):
            return self._value == other._value
        else:
            raise ValueError(
                "Can't compare IntegralType to unknown type: {}".format(
                    type(other)))

    def __repr__(self):
        return "IntegerType({})".format(self._value)
