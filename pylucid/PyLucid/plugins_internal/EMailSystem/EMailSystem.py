# -*- coding: utf-8 -*-

"""
    PyLucid EMail system Plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A Plugin to send EMails to other installed PyLucid Users.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:JensDiemer $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev$"

from django import newforms as forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.translation import ugettext as _

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from django.conf import settings


class MailForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select a user you would like to write a mail."),
    )
    subject = forms.CharField(
        help_text=_("(The prefix '%s' would be insert.)") % (
            settings.EMAIL_SUBJECT_PREFIX
        ), min_length=5
    )
    mail_text = forms.CharField(widget=forms.Textarea,
        max_length=2048, min_length=20
    )

class EMailForm(forms.Form):
    email = forms.EmailField()


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
            sender = self._get_sender()
        except NoValidSender, e:
            self.page_msg.red(e)
            return

        try:
            send_mail(
                subject = subject,
                message = cleaned_data["mail_text"],
                from_email = sender,
                recipient_list = recipient_list,
            )
        except Exception, msg:
            raise SendMailError(_("Error sending mail: %s") % msg)

    def _get_sender(self):
        test_sender = EMailForm({"email": self.request.user.email})
        if not test_sender.is_valid():
            raise NoValidSender(_(
                "You can't send emails,"
                " your user account has no valid email address."
            ))

        sender = test_sender.cleaned_data["email"]
        return sender

    def user_list(self):
        """
        form for sending mails to the django members.
        """
        # Change the global page title:
        self.context["PAGE"].title = _("EMail system")

        if settings.ALLOW_SEND_MAILS != True:
            self.page_msg(_("Sending mails deny in your settings.py!"))
            return

        try:
            sender = self._get_sender()
        except NoValidSender, e:
            self.page_msg.red(e)
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
            mail_form = MailForm()

        context = {
            "form": mail_form.as_p(),
            "sender": sender,
        }
        self._render_template("mail_form", context)#, debug=True)


class SendMailError(Exception):
    pass

class NoValidSender(Exception):
    """ The current User has no vaild email address in account data. """
    pass