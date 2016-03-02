# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
==
rv
==

Radial velocity webapp using Flask.

This is an Astropy affiliated package.
"""

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

# For egg_info test builds to pass, put package imports here.
if not _ASTROPY_SETUP_:
    # from example_mod import *
    pass


def main():
    """Entry point for the command-line script, :command:`rv`.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    #
    # Imports
    #
    from pkg_resources import resource_filename
    from os import symlink
    from os.path import exists, join
    from shutil import copy
    from .fitter import fitter
    from .util import rv_options, rv_data, create_index
    from .plot import diagnostic_plots, rv_plot
    #
    # Parse options
    #
    options = rv_options(description=("Create radial velocity plots " +
                                      "for all stars."))
    #
    # Files
    #
    stars = rv_data(options)
    #
    # Plot All
    #
    if not exists(join(options.plotDir, 'insufficient.png')):
        copy(resource_filename('rv', 'static/img/insufficient.png'),
             options.plotDir)
    if options.plot:
        for s in stars:
            if stars[s].fittable:
                print(s)
                if not stars[s].valid_flags:
                    print(("{0} has inconsistent APOGEE_STARFLAG " +
                           "values!").format(s))
                fits = fitter(stars[s], options)
                fit1, fit2 = rv_plot(stars[s], fits, options)
                stars[s].fit1 = fit1
                stars[s].fit2 = fit2
            else:
                print("{0} has insufficient data.".format(s))
                symlink(join(options.plotDir, 'insufficient.png'),
                        join(options.plotDir, s+'.png'))
        diagnostic_plots(stars, options)
    #
    # Create index.html
    #
    if options.index:
        indexHtml = create_index(stars)
        with open(join(options.plotDir, 'index.html'), 'w') as i:
            i.write(indexHtml)
    return 0
