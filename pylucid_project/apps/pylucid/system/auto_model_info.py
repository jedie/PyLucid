# coding: utf-8

"""
    PyLucid auto model info
    ~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""

__version__= "$Rev:$"

import sys

from django.db import models
from django.contrib import admin
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError


class UpdateInfoBaseAdmin(admin.ModelAdmin):
    """
    Base class for all models witch use UpdateInfoBaseModel():
    The save method need the request object as the first argument (For automatic update user ForeignKey).
    Add request object to save() methods witch used in the django admin site.
    See also: http://code.djangoproject.com/wiki/CookBookNewformsAdminAndUser
    """
    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        instance.save(request)
        form.save_m2m()
        return instance

#    def save_formset(self, request, form, formset, change): 
#        def set_user(instance):
#            instance.user = request.user
#            instance.save()
#
#        if formset.model == Comment:
#            instances = formset.save(commit=False)
#            map(set_user, instances)
#            formset.save_m2m()
#            return instances
#        else:
#            return formset.save()

#------------------------------------------------------------------------------

def _get_request_from_args(args):
    """
    Helper function for getting the request object from the method arguments.
    Add a better traceback message if not requets object are in the method arguments.
    
    Used in UpdateInfoBaseModelManager().get_or_create() and UpdateInfoBaseModel().save()
    returns the request object and the args without the request object.
    """
    args = list(args) # convert tuple into list, so we can pop the first argument out.
         
    try:
        request = args.pop(0)
    except IndexError, err:
        # insert more information into the traceback
        etype, evalue, etb = sys.exc_info()
        # FIXME: How can we insert the original called method name?
        evalue = etype('Method needs request object as first argument!')
        raise etype, evalue, etb   
    
    assert isinstance(request, HttpRequest), \
        "First argument must be the request object! (It's type: %s)" % type(request)
    
    assert isinstance(request.user, User)
    
    return request, args



class UpdateInfoBaseModelManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        """
        Same as django.db.models.query.QuerySet().get_or_create(), but here the first
        method argument must be the request object for passing it to the save() method.
        (For automatic update user ForeignKey in all UpdateInfoBaseModel's) 
        """
        assert kwargs, \
                'get_or_create() must be passed at least one keyword argument'
        
        # pop the request object from the arguments, insert a helpfull information in 
        # the traceback, if the request object is not the first argument
        request, args = _get_request_from_args(args)
        
        defaults = kwargs.pop('defaults', {})
        
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            try:
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                obj = self.model(**params)
                sid = transaction.savepoint()
                obj.save(request, force_insert=True)
                transaction.savepoint_commit(sid)
                return obj, True
            except IntegrityError, e:
                transaction.savepoint_rollback(sid)
                try:
                    return self.get(**kwargs), False
                except self.model.DoesNotExist:
                    raise e


class UpdateInfoBaseModel(models.Model):
    """
    Base model with update info attributes, used by many models.
    The createby and lastupdateby ForeignKey would be automaticly updated. This needs the 
    request object as the first argument in the save method.
    
    Important: Every own objects manager should be inherit from UpdateInfoBaseModelManager!
    """
    objects = UpdateInfoBaseModelManager()
    
    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    createby = models.ForeignKey(User, editable=False, related_name="%(class)s_createby",
        help_text="User how create the current page.",)
    lastupdateby = models.ForeignKey(User, editable=False, related_name="%(class)s_lastupdateby",
        help_text="User as last edit the current page.",)
    
    def save(self, *args, **kwargs):
        """
        Automatic update createby and lastupdateby attributes with the request object witch must be
        the first argument.
        """
        # pop the request object from the arguments, insert a helpfull information in 
        # the traceback, if the request object is not the first argument:
        request, args = _get_request_from_args(args)
        
        try:
            current_user = request.user
        except AttributeError, err:
            # insert more information into the traceback
            etype, evalue, etb = sys.exc_info()
            # FIXME: How can we insert the original called method name?
            evalue = etype('request object has no user object!? (Original error: %s)' % err)
            raise etype, evalue, etb
        
        if self.pk == None or kwargs.get("force_insert", False): # New model entry
            self.createby = current_user
        self.lastupdateby = current_user
        return super(UpdateInfoBaseModel, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True