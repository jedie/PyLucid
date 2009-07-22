from pylucid_comments.models import PyLucidComment
from pylucid_comments.forms import PyLucidCommentForm

def get_model():
    return PyLucidComment

def get_form():
    return PyLucidCommentForm

def get_form_target():
    # The Plugin must handle this
    return ""
