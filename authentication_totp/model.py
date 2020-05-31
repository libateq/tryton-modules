# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.


# Buttons on models the user cannot write to are made readonly and disabled,
# this hack avoids the button being made readonly in the user preferences.
class UserPreferencesButton(dict):

    def copy(self):
        return self.__class__(self)

    def __setitem__(self, key, value):
        if key == 'readonly':
            return
        return super().__setitem__(key, value)
