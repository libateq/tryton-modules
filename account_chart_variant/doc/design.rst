******
Design
******

The *Account Chart Variant Module* introduces the concept of a chart variant.

.. _model-account.chart_variant:

Chart Variant
=============

The *Chart Variant* concept is used as the name for a particular variant of
a chart of accounts.

Each chart variant defines which `Templates <concept-account.template>`
are specific to a particular chart of accounts.

This allows small changes to be made to a chart of accounts without needing to
duplicate the entire chart of accounts, and also allows combinations of these
variants to be applied together without needing to create a full charts of
accounts for each of the different possible combinations.

This can be used to modify a chart of accounts for a particular combination
of business types, sectors and uses.

.. _model-account.account:

Account
========

The *Account* concept is extended so each top-level account is linked to
any number of `Chart Variants <model-account.chart_variant>`.

.. seealso::

   The `Account <account:model-account.account>` concept is introduced by the
   :doc:`Account Module <account:index>`.

.. _concept-account.template:

Templates
=========

Activating the *Account Chart Variant Module* allows the
`Templates <account:concept-account.template>` that make up a chart of
accounts to be linked to one or more
`Chart Variants <model-account.chart_variant>`.

Any templates that are linked to a chart variant are only used when the
chart of account's top-level account is also linked to the same chart variant.

.. seealso::

   The `Templates <account:concept-account.template>` concept is introduced by
   the :doc:`Account Module <account:index>`.
