# coding: utf-8

"""
    A simple poll plugin
    ~~~~~~~~~~~~~~~~~~~~
    
    Features:
        * insert a specific poll into cms page
        * insert all/all active/all voteable polls into cms page
        * activate/deactivate polls
        * limit view and/or vote to a poll to usertype/usergroup
        * Save
        
    See also:
        http://www.pylucid.org/permalink/375/poll

    :copyleft: 2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from django_tools.decorators import render_to
from django_tools import limit_to_usergroups

from pylucid_project.apps.pylucid.shortcuts import bad_request

from poll.models import Poll, Choice, UserVotes, IPVotes



#CHECK_SESSION = False
CHECK_SESSION = True

#CHECK_COOKIES = False
CHECK_COOKIES = True


def _get_poll_or_404(id):
    id = int(id)
    try:
        poll = Poll.on_site.get(id=id)
    except Poll.DoesNotExist:
        raise Http404(_("Poll with ID %s doesn't exist" % id))
    return poll


def _get_cookie_name(poll):
    return "pylucid_poll_%i" % poll.id


def _ip_limit_reached(request, poll):
    """
    Return True if IP limit reached for this poll.
    """
    if poll.limit_ip == 0:
        # No limit set
        return False

    # Check if IP Address has too many votes
    ip = request.META['REMOTE_ADDR']
    try:
        queryset = IPVotes.objects.only("count").get(poll=poll, ip=ip)
    except IPVotes.DoesNotExist:
        return False
    else:
        count = queryset.count

    if count >= poll.limit_ip:
        if settings.DEBUG:
            messages.debug(request, "We get %i votes from %s and only %i are allowed" % (count, ip, poll.limit_ip))
        return True
    else:
        return False


def _why_cant_vote(request, poll):
    """
    return a message why the user can't vote or return False if he can vote.
    Reasons are:
        * poll is not active
        * user has no permission
        * user has vote in the past
        * To many votes from this IP
    """
    if not poll.active:
        return _("This poll is not active.")

    if not limit_to_usergroups.has_permission(poll, permit_vote=request.user):
        msg = _("You have no permission to vote this poll.")
        if settings.DEBUG:
            verbose_limit_name = limit_to_usergroups.get_verbose_limit_name(poll.permit_vote)
            msg += " (Limited to: %s)" % verbose_limit_name
        return msg

    if CHECK_COOKIES and _get_cookie_name(poll) in request.COOKIES:
        # Save that this user hase vote to this poll
        msg = _("You have vote for this in the past.")
        if settings.DEBUG:
            msg += " (Info from cookie)"
        return msg

    if CHECK_SESSION and poll.id in request.session.get("has_vote_polls", []):
        msg = _("You have vote for this in the past.")
        if settings.DEBUG:
            msg += " (Info from session)"
        return msg

    if request.user.is_authenticated():
        # Save that this user hase vote to this poll
        if UserVotes.objects.filter(poll=poll, user=request.user).count() > 0:
            msg = _("You have vote for this in the past.")
            if settings.DEBUG:
                msg += " (Info from UserVotes model)"
            return msg

    if _ip_limit_reached(request, poll):
        msg = _("No more votes allowed.")
        if settings.DEBUG:
            ip = request.META['REMOTE_ADDR']
            msg += " (Limit of %i votes from %s reached.)" % (poll.limit_ip, ip)
        return msg

    return False # user can vote



@render_to()
def _get_poll_content(request, poll):
    context = {
        "poll": poll,
    }
    why_cant_vote = _why_cant_vote(request, poll)
    if why_cant_vote == False:
        # Use can vote -> display vote form
        context["template_name"] = "poll/vote_form.html"
    else:
        # Use can't vote -> display poll results with a message, why he can't vote
        context.update({
            "poll_message": why_cant_vote,
            "template_name": "poll/results.html",
        })

    return context



def lucidTag(request, id=None):
    """
    Add a poll to the page content.
    
    {% lucidTag poll %}
        Display the newest, voteable poll.
        
    {% lucidTag poll id=X %}
        Display a specific poll.
        (Look into admin changelist to the the right ID)
        
    {% lucidTag poll.all_polls %}
        Display all existing polls.
        Filter with 'hide_deactivated' and/or 'not_voteable'
    
    example:
        {% lucidTag poll id=23 %}
        {% lucidTag poll.all_polls hide_deactivated=True %}
        {% lucidTag poll.all_polls not_voteable=True %}
        {% lucidTag poll.all_polls hide_deactivated=True not_voteable=True %}
    """
    if id is None:
        # Display the newest, voteable poll
        queryset = Poll.on_site.filter(active=True).order_by("createtime")
        polls = limit_to_usergroups.filter_permission(queryset, permit_vote=request.user)
        if not polls:
            return render_to_response(
                "poll/no_active_poll.html", context_instance=RequestContext(request)
            )
        poll = polls[0]
    else:
        # Display a definite poll
        poll = _get_poll_or_404(id)

    if not limit_to_usergroups.has_permission(poll, permit_view=request.user):
        if settings.DEBUG:
            return "[No permissions to see this poll]"
        return ""

    response = _get_poll_content(request, poll)

    return response


def all_polls(request, hide_deactivated=False, not_voteable=False):
    """
    Display all active polls.
    """
    queryset = Poll.on_site.all()
    if hide_deactivated:
        queryset = queryset.filter(active=True)

    queryset = limit_to_usergroups.filter_permission(queryset, permit_view=request.user)

    if not_voteable:
        queryset = limit_to_usergroups.filter_permission(queryset, permit_vote=request.user)

    output = []
    for poll in queryset:
        response = _get_poll_content(request, poll)
        output.append(response.content)

    return "\n".join(output)


def _vote(request):
    id = request.GET["id"]
    poll = _get_poll_or_404(id)

    if not poll.active:
        messages.error(request, _("This poll is not active!"))
        return HttpResponseRedirect(request.path)

    if not limit_to_usergroups.has_permission(poll, permit_vote=request.user):
        msg = _("You have no permission to vote this poll.")
        if settings.DEBUG:
            verbose_limit_name = limit_to_usergroups.get_verbose_limit_name(poll.permit_vote)
            msg += " (Vote limited to: %s)" % verbose_limit_name
        messages.error(request, msg)
        return HttpResponseRedirect(request.path)

    if not limit_to_usergroups.has_permission(poll, permit_view=request.user):
        msg = _("You have no permission to vote this poll.")
        if settings.DEBUG:
            verbose_limit_name = limit_to_usergroups.get_verbose_limit_name(poll.permit_vote)
            msg += " (View limited to: %s)" % verbose_limit_name
        messages.error(request, msg)
        return HttpResponseRedirect(request.path)

    if _ip_limit_reached(request, poll): # debug message are created
        messages.error(request, _("No more votes allowed."))
        return HttpResponseRedirect(request.path)

    try:
        choice = request.POST["choice"]
    except KeyError:
        messages.error(request, _("You didn't select a choice."))
        return HttpResponseRedirect(request.path)

    try:
        selected_choice = poll.choice_set.get(pk=choice)
    except Choice.DoesNotExist:
        messages.error(request, _("Choice is not valid."))
        return HttpResponseRedirect(request.path)

    selected_choice.votes += 1
    selected_choice.save()
    messages.success(request, _("You choice was saved"))

    if "has_vote_polls" in request.session:
        request.session["has_vote_polls"].append(poll.id)
    else:
        request.session["has_vote_polls"] = [poll.id]

    if request.user.is_authenticated():
        # Save that this user hase vote to this poll
        UserVotes.objects.create(poll=poll, user=request.user)

    if poll.limit_ip > 0:
        # Save that this IP has vote to this poll.
        ip = request.META['REMOTE_ADDR']
        ipvotes, created = IPVotes.objects.get_or_create(poll=poll, ip=ip)
        if not created:
            ipvotes.count += 1
            ipvotes.save()

    response = HttpResponseRedirect(request.path)
    # Save that this user hase vote to this poll
    response.set_cookie(_get_cookie_name(poll), value="1")
    return response


def http_get_view(request):
    """
    Login+Logout view via GET parameters
    """
    action = request.GET["poll"]

    if action == "vote":
        return _vote(request)
    else:
        debug_msg = "Wrong get view parameter!"
        return bad_request("pylucid_plugin.poll", "error", debug_msg) # Returns a HttpResponseBadRequest




