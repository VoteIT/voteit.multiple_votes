from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectUpdatedEvent
from pyramid.events import subscriber
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_interface
from voteit.core.models.interfaces import IMeeting
from voteit.core.models.interfaces import IVote

from voteit.multiple_votes import MEETING_NAMESPACE


@subscriber([IVote, IObjectAddedEvent])
@subscriber([IVote, IObjectUpdatedEvent])
def multiply_votes(obj, event):
    """ This subscriber multiplies votes for members that have received several votes.
    """
    request = get_current_request()
    userid = request.authenticated_userid
    # Only preform this function on the initial vote object
    if userid != obj.__name__:
        return
    meeting = find_interface(obj, IMeeting)
    try:
        multi_votes = meeting[MEETING_NAMESPACE]
    except KeyError:
        # This system isn't active
        return

    vote_counter = (
        multi_votes.get_vote_power(userid) - 1
    )  # Since the initial vote was added already

    if vote_counter:  # Votes might have been exhausted if they only had one!

        poll = obj.__parent__
        poll_plugin = poll.get_poll_plugin()
        initial_vote = poll[userid]
        vote_data = (
            initial_vote.get_vote_data()
        )  # Just to make sure, get from the initial one

        if IObjectAddedEvent.providedBy(event):
            Vote = poll_plugin.get_vote_class()
            assert IVote.implementedBy(Vote)
            for i in range(vote_counter):
                name = "{}_{}".format(initial_vote.uid, i)
                vote = Vote(creators=[userid])
                vote.set_vote_data(vote_data, notify=False)
                poll[name] = vote

        if IObjectUpdatedEvent.providedBy(event):
            for i in range(vote_counter):
                name = "{}_{}".format(initial_vote.uid, i)
                poll[name].set_vote_data(vote_data, notify=False)


def includeme(config):
    config.scan(__name__)
