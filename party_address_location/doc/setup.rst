*****
Setup
*****

.. _Loading and updating postal codes with locations:

Loading and updating postal codes with locations
================================================

There are latitudes and longitudes associated with
`Postal Codes <model-country.postal_code>` in the `GeoNames Database`_.
To load and update the postal codes along with their latitude and longitudes
in Tryton you can use the :command:`trytond_import_postal_codes_locations`
script.

.. _GeoNames Database: https://www.geonames.org/

It is run with:

.. code-block:: bash

   trytond_import_postal_codes_locations -c trytond.conf -d <database> <two_letter_country_code>

.. seealso::

   To load and update the postal codes without their latitude and longitude
   see `country:Loading and updating postal codes`.
