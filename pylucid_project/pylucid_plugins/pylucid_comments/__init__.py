# coding: utf-8

def get_model():
    from pylucid_project.pylucid_plugins.pylucid_comments.models import PyLucidComment
    return PyLucidComment

def get_form():
    from pylucid_project.pylucid_plugins.pylucid_comments.forms import PyLucidCommentForm
    return PyLucidCommentForm

def get_form_target():
    # The Plugin must handle this
    return ""
