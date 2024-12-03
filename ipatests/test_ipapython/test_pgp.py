# Author:
#   Sam Cordry <samcordry@gmail.com>
"""
Test the `ipapython/pgp.py` module.
"""

import six
import pytest

from ipapython import pgp

if six.PY3:
    unicode = str

pytestmark = pytest.mark.tier0

@pytest.mark.parameterize("pk,out", [
    (b'\xff', UnicodeDecodeError),
    (u'\xff', ValueError),
], ids=repr)
def test_public_key_parsing(pk, out):
    if isinstance(out, type) and issubclass(out, Exception):
        pytest.raises(out, pgp.PGPPublicKey, pk)
    else:
        parsed = pgp.PGPPublicKey(pk)
        assert parsed.key() == out
