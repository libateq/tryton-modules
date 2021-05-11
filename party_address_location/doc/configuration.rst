*************
Configuration
*************

The *Party Address Location Module* uses values from settings in the
``[party_address_location]`` section of the
:doc:`configuration file <trytond:topics/configuration>`.

.. _config-party_address_location.earth_radius:

``earth_radius``
================

The ``earth_radius`` configuration setting allows the value used as the earth's
radius to be adjusted in the distance calculation.

The units that the distance is in will be the same as the units that the
earth's radius is in.
So to get distances in miles the earth's radius should be set in miles, and
for kilometres set the earth's radius in kilometres.

As the earth is not a perfect sphere the distances will never be exact, but
using these figures should give a good approximation:

* Use ``3959`` for distances in miles.
* Use ``6371`` for distances in kilometres.

The default value is: ``3959.0``
