# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import getLogger

from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectRemovedEvent
from arche.interfaces import IObjectUpdatedEvent
from arche.interfaces import IWorkflowAfterTransition
from arche.interfaces import IWorkflowBeforeTransition
from arche.resources import Base
from arche.resources import Content
from arche.resources import ContextACLMixin
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPForbidden
from pyramid.traversal import find_interface
from voteit.core.interfaces import IWorkflowStateChange
from voteit.core.models.interfaces import IMeeting
from voteit.core.models.interfaces import IPoll
from voteit.core.security import MODERATE_MEETING, ROLE_VIEWER
from voteit.core.security import ROLE_VOTER
from voteit.irl.models.interfaces import IElectoralRegister
from zope.interface import implementer

from voteit.multiple_votes import _, MEETING_NAMESPACE
from voteit.multiple_votes.interfaces import IMultiVotes, IVoteAssignment
from voteit.multiple_votes.permissions import ADD_VOTE_ASSIGNMENT
from voteit.multiple_votes.utils import check_ongoing_poll


logger = getLogger(__name__)


@implementer(IMultiVotes)
class MultiVotes(Content, ContextACLMixin):
    """ A container for vote assignment when the multi vote system is activated. """

    type_name = "MultiVotes"
    type_title = _("MultiVotes")
    type_description = ""
    add_permission = MODERATE_MEETING
    css_icon = "glyphicon glyphicon-folder-open"
    nav_visible = True
    listing_visible = True
    search_visible = False
    title = _("MultiVotes")
    total_votes = 0
    total_voters = 0
    assigned_votes = 0

    def get_sorted_values(self):
        """ Return all contained Group object sorted on title. """
        return sorted(self.values(), key=lambda x: x.title.lower())

    def get_assignments(self, userid):
        """ Get the users assignments. """
        for v in self.values():
            if v.userid_assigned == userid:
                yield v

    def get_vote_power(self, userid):
        """ How many votes should this user have based on the number of assignments they have.
        """
        votes = 0
        for v in self.get_assignments(userid):
            votes += v.votes
        return votes

    def update_totals(self):
        total_votes = 0
        assigned_votes = 0
        voters = set()
        for v in self.values():
            total_votes += v.votes
            if v.userid_assigned:
                assigned_votes += v.votes
                voters.add(v.userid_assigned)
        self.total_votes = total_votes
        self.total_voters = len(voters)
        self.assigned_votes = assigned_votes

    def get_voters(self):
        results = set()
        for v in self.values():
            if v.userid_assigned:
                results.add(v.userid_assigned)
        return results

    def recheck_voters(self):
        """ Perform a check against the current voters and who's actually in a vote assignment. """
        meeting = self.__parent__
        lr = meeting.local_roles
        current_role_voters = frozenset(lr.get_any_local_with(ROLE_VOTER))
        current_mv_voters = self.get_voters()
        # Make sure the voting role matches the users that should have a vote.
        # Invitations and similar doesn't matter in a multivote meeting
        remove_userids = current_role_voters - current_mv_voters
        add_userids = current_mv_voters - current_role_voters
        for userid in remove_userids:
            lr.remove(userid, ROLE_VOTER, event=False)
        for userid in add_userids:
            lr.add(userid, ROLE_VOTER, event=False)
        if remove_userids or add_userids:
            # Send one event afterwards to avoid clutter
            lr.send_event()


@implementer(IVoteAssignment)
class VoteAssignment(Base):
    """ Votes are assigned with this item when using multi-vote system. A single user is assigned votes. """

    type_name = "VoteAssignment"
    type_title = _("Vote Assignment")
    type_description = ""
    add_permission = ADD_VOTE_ASSIGNMENT
    naming_attr = "uid"
    title = ""
    votes = 1
    userid_assigned = None


@subscriber([IMultiVotes, IWorkflowBeforeTransition])
def block_during_ongoing_poll(context, event):
    if check_ongoing_poll(context):
        raise HTTPForbidden(
            _(
                "access_during_ongoing_not_allowed",
                default="During ongoing polls, this action isn't allowed. "
                "Try again when polls have closed.",
            )
        )


@subscriber([IMultiVotes, IWorkflowAfterTransition])
def update_voters(context, event):
    if event.to_state == 'locked':
        context.recheck_voters()
        # Update registry
        meeting = context.__parent__
        er = IElectoralRegister(meeting, None)
        if er is not None:
            if er.new_register_needed():
                voter_userids = er.currently_set_voters()
                er.new_register(voter_userids)


@subscriber([IPoll, IWorkflowStateChange])
def block_starting_polls_with_multivotes_open(context, event):
    if event.new_state == "ongoing":
        meeting = find_interface(context, IMeeting)
        if MEETING_NAMESPACE in meeting:
            mv = meeting[MEETING_NAMESPACE]
            if mv.wf_state == "open":
                raise HTTPForbidden(
                    _(
                        "You may not start polls unless you've locked the assignment of votes. See multivotes."
                    )
                )


@subscriber([IVoteAssignment, IObjectAddedEvent])
@subscriber([IVoteAssignment, IObjectUpdatedEvent])
def update_cached_totals_new_count(context, event):
    """ Added or updated objects. """
    multi_votes = find_interface(context, IMultiVotes)
    multi_votes.update_totals()


@subscriber([IVoteAssignment, IObjectRemovedEvent])
def update_cached_totals_removed(context, event):
    """ Removed objects """
    multi_votes = event.parent
    multi_votes.update_totals()


@subscriber([IVoteAssignment, IObjectAddedEvent])
@subscriber([IVoteAssignment, IObjectUpdatedEvent])
def add_user_to_meeting(context, event):
    """ Make sure the added user can see the meeting. """
    if context.userid_assigned is not None:
        meeting = find_interface(context, IMeeting)
        meeting.local_roles.add(context.userid_assigned, ROLE_VIEWER)


def includeme(config):
    config.add_content_factory(MultiVotes)
    config.set_content_workflow("MultiVotes", "lock_assignment")
    config.add_content_factory(VoteAssignment, addable_to="MultiVotes")
    config.scan(__name__)
