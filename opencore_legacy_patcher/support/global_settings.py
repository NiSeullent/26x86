"""
global_settings.py: Library for querying and writing 26x86 settings

Stores data in ~/Library/Preferences/com.sharhene777.26x86.plist only.
Independent from legacy OCLP configuration paths — 26x86 never reads OCLP plists.
"""

from pathlib import Path

from ..constants import Constants

from .settings_store import SettingsStore


class GlobalEnviromentSettings:
    """
    Library for querying and writing 26x86 user settings
    """

    def __init__(self) -> None:
        constants = Constants()
        self.bundle_id:             str = constants.bundle_id
        self.app_support_path:     Path = constants.app_support_path
        self._store = SettingsStore(constants)
        self.settings_plist_path = self._store.preferences_path
        self.global_settings_plist = str(self.settings_plist_path)

    def read_property(self, property_name: str):
        """
        Reads a property from the settings file
        """
        return self._store.read(property_name)

    def delete_property(self, property_name: str) -> None:
        """
        Deletes a property from the settings file
        """
        self._store.delete(property_name)

    def write_property(self, property_name: str, property_value) -> None:
        """
        Writes a property to the settings file
        """
        self._store.write(property_name, property_value)
