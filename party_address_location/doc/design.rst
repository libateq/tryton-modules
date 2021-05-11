******
Design
******

.. _model-party.address:

Address
========

The *Address* concept is used to store postal addresses.

When the *Party Address Location Module* is active a latitude and longitude
can be stored for each address.
The latitude and longitude for an address are both updated when the address's
`Postal Code <model-country.postal_code>` is changed.

For each address the distance to the ``latitude`` and ``longitude`` in the
:py:attr:`~trytond:trytond.transaction.Transaction.context` is also available.

.. seealso::

   The `Address <party:model-party.address>` concept is introduced by the
   :doc:`Party Module <party:index>`.

.. _model-country.postal_code:

Postal Code
===========

The *Postal Code* concept is used to store postal codes.

With the *Party Address Location Module* active Postal Codes gain a latitude
and longitude which is used to store their location.

.. seealso::

   The `Postal Code <country:model-country.postal_code>` concept is introduced
   by the :doc:`Country Module <country:index>`.
