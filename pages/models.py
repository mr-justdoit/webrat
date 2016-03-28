# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Content(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    page_id = models.IntegerField()
    html = models.TextField(unique=True, blank=True, null=True)
    created_at = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Content'


class Page(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    url = models.TextField(unique=True)
    created_at = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Page'
