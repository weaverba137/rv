**
rv
**

Introduction
============

This is the documentation for rv.

Notes
=====

SDSS-III Projects Related to Radial Velocities
----------------------------------------------

* `133 <https://www.sdss3.org/internal/publications/cgi-bin/projects.pl?action=display_project;number=133>`_
* `176 <https://www.sdss3.org/internal/publications/cgi-bin/projects.pl?action=display_project;number=176>`_
* `236 <https://www.sdss3.org/internal/publications/cgi-bin/projects.pl?action=display_project;number=236>`_
* `251 <https://www.sdss3.org/internal/publications/cgi-bin/projects.pl?action=display_project;number=251>`_
* `296 <https://www.sdss3.org/internal/publications/cgi-bin/projects.pl?action=display_project;number=296>`_

SDSS-III Papers Related to Radial Velocities
--------------------------------------------

* `116 <https://www.sdss3.org/internal/publications/cgi-bin/publications.pl?action=display_pub;number=116>`_;
  `Deshpande *et al.* (2013) <http://adsabs.harvard.edu/abs/2013AJ....146..156D>`_
* `230 <https://www.sdss3.org/internal/publications/cgi-bin/publications.pl?action=display_pub;number=230>`_

Other Links
-----------

* `apogee-rvvar mailing list <https://trac.sdss3.org/tracmailman/browser/private/apogee-rvvar/all/thread.html>`_
* `apogee-mdwarfs mailing list https://trac.sdss3.org/tracmailman/browser/private/apogee-mdwarfs/all/thread.html>`_
   related to paper 116.
* `APOGEE/binaries wiki page <https://trac.sdss3.org/wiki/APOGEE/binaries>`_
* `HD280136 <https://trac.sdss3.org/wiki/APOGEE/HD280136>`_;
  `2M04485261+3858386 <http://skyserver.sdss.org/dr12/en/tools/explore/summary.aspx?apid=apogee.apo25m.s.stars.4257.2M04485261+3858386>`_

Questions
---------

* Is ``vrelerr`` the appropriate column for characterizing the uncertainty in
  ``vhelio``?
  - Yes!

Interesting Ideas
-----------------

* What can APOGEE say about the population of long-period binaries?
* Why do many of the stars have just one big outlier?
* Match against a catalog of binaries.

Interesting RV Plots
====================

Link to All Plots
-----------------

We have an `auto-generated list`_ of all RVs.  *Caution*, this loads slowly!

.. _`auto-generated list`: http://sdss.physics.nyu.edu/apogee-rv/

Weird Outliers
--------------

* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4102.2M21401882+4350520.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4103.2M08185175+3055398.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4105.2M16460934+3534382.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4107.2M18214766+0157091.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4121.2M04350087+5838349.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4124.2M11443145-0031077.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4125.2M12222839-0044391.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4128.2M13090983+1711572.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4128.2M13134107+1614282.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4128.2M13142538+1606481.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4147.2M07324839+2133141.png

Nice Curves
-----------

* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4102.2M21415678+4306484.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4103.2M08140186+3045036.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4105.2M16355605+3552193.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4120.2M00250145+6929551.png
* http://sdss.physics.nyu.edu/apogee-rv/apogee.apo25m.s.stars.4249.2M21234925+4534342.png

Other Documents
===============

.. toctree::
    :maxdepth: 1

    changes.rst

Reference/API
=============

.. automodapi:: rv
    :no-inheritance-diagram:

.. automodapi:: rv.fitter
    :no-inheritance-diagram:

.. automodapi:: rv.model
    :no-inheritance-diagram:

.. automodapi:: rv.plot
    :no-inheritance-diagram:

.. .. automodapi:: rv.rv
..    :no-inheritance-diagram:

.. automodapi:: rv.util
    :no-inheritance-diagram:
    :skip: issubdtype, append, array
