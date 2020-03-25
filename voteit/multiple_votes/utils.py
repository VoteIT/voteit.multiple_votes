from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from pyramid.traversal import resource_path
from repoze.catalog.query import Eq
from voteit.core.models.interfaces import IMeeting


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
