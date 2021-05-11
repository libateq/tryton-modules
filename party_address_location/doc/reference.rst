*********************
Development Reference
*********************

.. view-address_distance_view_list:

Address Distance View List
==========================

The *Party Address Location Module* provides the
``address_distance_view_list`` `View <trytond:topics-views>` that can be used
to list addresses in order of distance to a latitude and longitude.

This works well with :py:class:`~trytond:trytond.model.fields.Many2One` fields
to easily allow users to select an address based on how close it is to a
specific latitude and longitude.

For example:

.. code-block:: python

   address = fields..Many2One(
       'party.address', "Address",
       context={
           'latitude': 51.477806,
           'longitude': -0.001472,
           })

.. code-block:: xml

   <form>
     <label name="address"/>
     <field name="address" view_ids="party_address_location.address_distance_view_list"/>
   </form>
