#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid EMail system Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A Plugin to send EMails to other installed PyLucid Users.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:JensDiemer $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

from django import newforms as forms
from django.contrib.auth.models import User
from django.core.mail import send_mail

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from django.conf import settings

TEMPLATE = """
<form method="post" action=".">
  <table class="form">
    {{ form }}
  </table>
  <input type="submit" value="{% trans 'send email' %}" />
</form>
"""

class MailForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select users you a mail wants to send"),
    )
    sender = forms.EmailField()
    subject = forms.CharField(
        help_text=_("(The prefix '%s' would be insert.)") % (
            settings.EMAIL_SUBJECT_PREFIX
        ), min_length=5
    )
    mail_text = forms.CharField(widget=forms.Textarea,
        max_length=2048, min_length=20
    )



class EMailSystem(PyLucidBasePlugin):
    def _send_mail(self, cleaned_data):
        """
        send the mail. raise SendMailError() on errors.
        """
        subject = "%s%s" % (
            settings.EMAIL_SUBJECT_PREFIX, cleaned_data["subject"]
        )

        recipient_list = []
        for user in cleaned_data["users"]:
            if user.email=="":
                self.page_msg(
                    _("Can't send to user '%s',"
                    " because he has a empty email adress!") % user.username
                )
            else:
                recipient_list.append(user.email)

        if recipient_list == []:
            raise SendMailError(_("No recipient left."))

        try:
            send_mail(
                subject = subject,
                message = cleaned_data["mail_text"],
                from_email = cleaned_data["sender"],
                recipient_list = recipient_list,
            )
        except Exception, msg:
            raise SendMailError(_("Error sending mail: %s") % msg)


    def user_list(self):
        """
        form for sending mails to the django members.
        """
        if settings.ALLOW_SEND_MAILS != True:
            self.page_msg(_("Sending mails deny in your settings.py!"))
            return

        if self.request.method == 'POST':
            mail_form = MailForm(self.request.POST)
            if mail_form.is_valid():
                try:
                    self._send_mail(mail_form.cleaned_data)
                except SendMailError, msg:
                    self.page_msg.red(msg)
                else:
                    self.page_msg.green(_("Send mail, OK"))
                    return
        else:
            host = self.request.META.get("HTTP_HOST", settings.EMAIL_HOST)
            # Cut the port number, if exists
            host = host.split(":")[0]

            form_data = {
                "sender": "%s@%s" % (self.request.user, host),
            }
            mail_form = MailForm(form_data)

        context = {
            "form": mail_form.as_p(),
        }

        return self._render_string_template(TEMPLATE, context)#, debug=True)


class SendMailError(Exception):
    pass