from mjlab.utils.lab_api.tasks.importer import import_packages

# Aliases of moved K1 packages; their tasks register from k1.tasks.
_BLACKLIST_PKGS = ["utils", ".mdp", ".bhuman_kick"]

import_packages(__name__, _BLACKLIST_PKGS)
