===============================
Party Address Location Scenario
===============================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules

Activate modules::

    >>> config = activate_modules('party_address_location')

Create a country::

    >>> Country = Model.get('country.country')
    >>> country = Country(name="United Kingdom")
    >>> country.save()

Create a postal code::

    >>> PostalCode = Model.get('country.postal_code')
    >>> postal_code = PostalCode()
    >>> postal_code.postal_code = "SE10 8XJ"
    >>> postal_code.country = country
    >>> postal_code.latitude = 51.476698
    >>> postal_code.longitude = -0.004502
    >>> postal_code.save()

Create a party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name="Royal Observatory")
    >>> address, = party.addresses
    >>> address.postal_code = "SE10 8XJ"
    >>> party.save()

Check its location::

    >>> address, = party.addresses
    >>> address.latitude
    51.476698
    >>> address.longitude
    -0.004502

Check the distance to somewhere else::

    >>> with config.set_context(latitude=50.043759, longitude=-5.651496):
    ...     party, = Party.find([('name', '=', 'Royal Observatory')])
    ...     address, = party.addresses
    ...     round(address.distance)
    266
