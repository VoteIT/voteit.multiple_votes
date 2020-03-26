from pyramid.httpexceptions import HTTPForbidden
from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from pyramid.traversal import resource_path
from repoze.catalog.query import Eq
from voteit.core.models.interfaces import IMeeting

from voteit.multiple_votes import _


def check_ongoing_poll(context):
    """ Check if a poll is ongoing, return number of ongoing polls """
    meeting = find_interface(context, IMeeting)
    assert IMeeting.providedBy(meeting)
    root = find_root(meeting)
    query = (
        Eq("type_name", "Poll")
        & Eq("path", resource_path(meeting))
        & Eq("workflow_state", "ongoing")
    )
    res = root.catalog.query(query)[0]
    return res.total


def block_during_ongoing_poll(context):
    if check_ongoing_poll(context):
        raise HTTPForbidden(
            _(
                "access_during_ongoing_not_allowed",
                default="During ongoing polls, this action isn't allowed. "
                "Try again when polls have closed.",
            )
        )
