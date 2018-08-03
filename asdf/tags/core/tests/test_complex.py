# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

import re

import pytest

import asdf
from asdf.tests import helpers


@pytest.mark.parametrize('invalid', [
    '3 + 4i', '3+-4i', '3-+4i', '3i+4i', 'X3+4iX', '3+X4i', '3+4', '3i+4'
    '3+4z', '3.+4i', '3+4.i', '3e-4.0+4i', '3+4e4.0i', ''
])
def test_invalid_complex(invalid):
    yaml = """
a: !core/complex-1.0.0
  {}
    """.format(invalid)

    buff = helpers.yaml_to_asdf(yaml)
    with pytest.raises(asdf.ValidationError):
        with asdf.AsdfFile.open(buff):
            pass


@pytest.mark.parametrize('valid', [
    '3+4j', '(3+4j)', '.3+4j', '3+.4j', '3e10+4j', '3e-10+4j', '3+4e10j',
    '3.0+4j', '3+4.0j', '3.0+4.0j', '3+4e-10j', '3+4J', '3+4i', '3+4I', 'inf',
    'inf+infj', 'inf+infi', 'infj', 'infi', 'INFi', 'INFI', '3+infj', 'inf+4j'
])
def test_valid_complex(valid):
    yaml = """
a: !core/complex-1.0.0
  {}
    """.format(valid)

    buff = helpers.yaml_to_asdf(yaml)
    with asdf.AsdfFile.open(buff) as af:
        assert af.tree['a'] == complex(re.sub(r'[iI]$', r'j', valid))


def test_roundtrip(tmpdir):
    tree = {
        'a': 0+0j,
        'b': 1+1j,
        'c': -1+1j,
        'd': -1-1j
        }

    helpers.assert_roundtrip_tree(tree, tmpdir)
