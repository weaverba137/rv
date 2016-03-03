# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import re
from .. import __version__ as rv_version


class TestRV(object):
    """Test the top-level rv functions.
    """

    def setup(self):
        self.versionre = re.compile(r'''
                                    ([0-9]+!)?  # epoch
                                    ([0-9]+)    # major
                                    (\.[0-9]+)* # minor
                                    ((a|b|rc|\.post|\.dev)[0-9]+)?''',
                                    re.X)

    def teardown(self):
        pass

    def test_version(self):
        """Ensure the version conforms to PEP386/PEP440.
        """
        assert self.versionre.match(rv_version) is not None
