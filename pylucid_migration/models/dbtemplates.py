"""
    model created by inspectdb for django-dbtemplates
"""
from django.db import models

class DBTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    content = models.TextField()
    creation_date = models.DateTimeField()
    last_changed = models.DateTimeField()
    class Meta:
        app_label = u'pylucid_migration'
        db_table = u'django_template'