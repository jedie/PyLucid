# coding: utf-8

"""
    A simple poll plugin
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models import aggregates
from django.utils.translation import ugettext_lazy as _

from django_tools import limit_to_usergroups
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.base_models.many2many import AutoSiteM2M



class Poll(AutoSiteM2M, UpdateInfoBaseModel):
    """   
    inherited attributes from AutoSiteM2M:
        sites     -> ManyToManyField to Site
        on_site   -> sites.managers.CurrentSiteManager instance
        site_info -> a string with all site names, for admin.ModelAdmin list_display

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    question = models.CharField(max_length=200)
    active = models.BooleanField(default=True,
        help_text=_("Can users vote to this poll or just see the result?"),
    )

    permit_vote = limit_to_usergroups.UsergroupsModelField(help_text=_("Limit vote to user-types/user-groups."))
    permit_view = limit_to_usergroups.UsergroupsModelField(help_text=_("Limit result view to user-types/user-groups."))

    limit_ip = models.IntegerField(
        default=10,
        help_text=_("Limit votes from the same IP - 0 == unlimited"),
    )

    def __unicode__(self):
        return self.question

    class Meta:
        ordering = ('-createtime', '-lastupdatetime')


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0, editable=False)

    def percent(self):
        result = Choice.objects.filter(poll=self.poll).aggregate(aggregates.Sum("votes"))
        votes_sum = result["votes__sum"]
        return float(self.votes) / votes_sum * 100

    def __unicode__(self):
        return self.choice


class UserVotes(models.Model):
    """ Save witch user has vote to the poll """
    poll = models.ForeignKey(Poll)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return u"%s - %s" % (self.user.username, self.poll.question)


class IPVotes(models.Model):
    poll = models.ForeignKey(Poll)
    ip = models.IPAddressField()
    count = models.IntegerField(default=1)
    def __unicode__(self):
        return u"%s - %s" % (self.ip, self.poll.question)
