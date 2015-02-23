
from django.db import models

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=300)
    name = models.CharField(max_length=150)
    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'django_site'