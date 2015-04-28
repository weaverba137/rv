# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Create radial velocity plots for all stars.
"""
#
# Import
#
from __future__ import absolute_import, division, print_function, unicode_literals
#
#
#
def main():
    """Main program.
    """
    #
    # Imports
    #
    from os.path import join
    from .fitter import fitter
    from .util import rv_options, rv_data, create_index
    from .plot import diagnostic_plots, rv_plot
    #
    # Parse options
    #
    options = rv_options(description=__doc__)
    #
    # Files
    #
    stars = rv_data(options)
    #
    # Plot All
    #
    if options.plot:
        for s in stars:
            print(s)
            fits = fitter(stars[s],options)
            fit1, fit2 = rv_plot(stars[s],fits,options)
            stars[s]['fit1'] = fit1
            stars[s]['fit2'] = fit2
    #
    # Create index.html
    #
    if options.index:
        indexHtml = create_index(stars)
        with open(join(options.plotDir,'index.html'),'w') as i:
            i.write(indexHtml)
    #
    # Other diagnostics
    #
    if options.diag:
        diagnostic_plots(stars,options)
    #
    #
    #
    return 0
