fedora-stats
============

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>


A simple application aiming at generate automatically and easily the statitics
from https://fedoraproject.org/wiki/Statistics


Get this project:
-----------------
Source:

- http://ambre.pingoured.fr/cgit
- https://github.com/pypingou/fedora-stats (mirror)

Dependencies:
-------------
The dependency list is therefore:

.. _python: http://www.python.org
.. _python-jinja2: http://jinja.pocoo.org/

- `python`_ (Tested on 2.6 and 2.7)
- `python-jinja2`_


Run the project:
----------------

Clone the source::

 git clone https://github.com/pypingou/fedora-stats.git

Run the python script::

 python generate_stats.py

View the output in the ``output`` folder generated in the same folder as is
the ``generate_stats.py`` script.

This project is aimed at being run via a cron job every week (as some of the
statistics are updated weekly) and then the page being exposed as static html.


License:
--------

This project is licensed GPLv2+.

