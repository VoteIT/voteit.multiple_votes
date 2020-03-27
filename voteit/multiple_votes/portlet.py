# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from arche.portlets import get_portlet_manager
from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectWillBeRemovedEvent
from pyramid.events import subscriber
from pyramid.traversal import find_interface
from voteit.core import security
from voteit.core.models.interfaces import IMeeting, IAgendaItem
from voteit.core.portlets.agenda_item import PollsInline
from voteit.core.portlets.agenda_item import PollsPortlet

from voteit.multiple_votes import MEETING_NAMESPACE
from voteit.multiple_votes.interfaces import IMultiVotes


MULTI_VOTES_POLLS_PORTLET = "mv_ai_polls"
DEFAULT_POLLS_PORTLET = PollsPortlet.name
MULTI_VOTES_POLLS_VIEW_NAME = "__mv_ai_polls__"


class MVPollsPortlet(PollsPortlet):
    name = MULTI_VOTES_POLLS_PORTLET
    view_name = MULTI_VOTES_POLLS_VIEW_NAME


class MVPollsInline(PollsInline):
    def get_voted_estimate(self, poll):
        """ Progress bar for all assigned votes vs actual incoming votes.
        """
        mv = self.request.meeting[MEETING_NAMESPACE]
        vote_count = getattr(poll, '_mv_votes_count', None)
        if vote_count is None:
            vote_count = mv.assigned_votes
        response = {"added": len(poll), "total": vote_count}
        if response["total"] != 0:
            try:
                response["percentage"] = int(
                    round(
                        100 * Decimal(response["added"]) / Decimal(response["total"]), 0
                    )
                )
            except ZeroDivisionError:
                response["percentage"] = 0
        else:
            response["percentage"] = 0
        return response


def adjust_poll_portlet(context, mv_version=True):
    """ Adjust poll portlet to this type"""
    PSLOT = "agenda_item"
    if mv_version:
        portlet_name = MULTI_VOTES_POLLS_PORTLET
        remove_portlet_name = DEFAULT_POLLS_PORTLET
    else:
        portlet_name = DEFAULT_POLLS_PORTLET
        remove_portlet_name = MULTI_VOTES_POLLS_PORTLET
    meeting = find_interface(context, IMeeting)
    assert meeting
    manager = get_portlet_manager(meeting)
    unwanted_portlet = None
    for p in manager.get_portlets(PSLOT, remove_portlet_name):
        unwanted_portlet = p
    if unwanted_portlet:
        manager.remove(PSLOT, unwanted_portlet.uid)
    if not manager.get_portlets(PSLOT, portlet_name):
        added_portlet = manager.add(PSLOT, portlet_name)
        portlet_folder = manager[PSLOT]
        order = list(portlet_folder.order)
        order.remove(added_portlet.uid)
        order.insert(0, added_portlet.uid)
        portlet_folder.order = order


@subscriber([IMultiVotes, IObjectAddedEvent])
@subscriber([IMultiVotes, IObjectWillBeRemovedEvent])
def toggle_portlet(context, event):
    adjust_poll_portlet(context, mv_version=IObjectAddedEvent.providedBy(event))


def includeme(config):
    config.add_portlet(MVPollsPortlet)
    # Custom version of polls inline view - __ai_polls__
    config.add_view(
        MVPollsInline,
        name=MULTI_VOTES_POLLS_VIEW_NAME,
        context=IAgendaItem,
        permission=security.VIEW,
        renderer="voteit.core:templates/portlets/polls_inline.pt",
    )
    config.scan(__name__)
