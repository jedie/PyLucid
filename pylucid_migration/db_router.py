
"""
    Multi-Database-Router
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""



class LegacyRouter(object):
    """
    point all read-operations on "legacy" models to the "legacy" DB
    Forbid write-operations and syncdb/migrate.
    """
    def db_for_read(self, model, **hints):
        """
        if old pylucid v1 model: read from legacy DB
        """
        if model._meta.app_label == "pylucid_migration":
            return "legacy"
        return "default"

    def db_for_write(self, model, **hints):
        """
        permit write to old v1 models
        """
        return False

    def allow_relation(self, obj1, obj2, **hints):
        """
        Forbid relations from/to v1 models to/from new app models.
        """
        obj1_is_legacy = (obj1._meta.app_label == "pylucid_migration")
        obj2_is_legacy = (obj2._meta.app_label == "pylucid_migration")
        return obj1_is_legacy == obj2_is_legacy

    def allow_migrate(self, db, model):
        """
        Forbid migrate old v1 models.
        """
        if db == "legacy":
            return False
        if model._meta.app_label == "pylucid_migration":
            return False
        return True