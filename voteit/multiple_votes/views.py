from __future__ import unicode_literals

from decimal import Decimal
from decimal import InvalidOperation

from arche.views.base import DefaultAddForm
from arche.views.base import BaseView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from voteit.core import security
from voteit.core.models.interfaces import IMeeting

from voteit.multiple_votes import MEETING_NAMESPACE
from voteit.multiple_votes.interfaces import IMultiVotes
from voteit.multiple_votes.interfaces import IVoteAssignment
from voteit.multiple_votes.permissions import ADD_VOTE_ASSIGNMENT


@view_config(
    context=IMultiVotes,
    permission=security.VIEW,
    renderer="voteit.multiple_votes:templates/multivotes.pt",
)
class MultiVoteView(BaseView):
    def __call__(self):
        return {}

    @property
    def can_add(self):
        return self.request.is_moderator and self.request.has_permission(
            ADD_VOTE_ASSIGNMENT
        )

    def can_edit_obj(self, obj):
        return self.request.is_moderator and self.request.has_permission(
            security.EDIT, obj
        )

    def get_assigned_perc(self):
        try:
            return int(
                round(
                    100
                    * Decimal(self.context.assigned_votes)
                    / Decimal(self.context.total_votes),
                    0,
                )
            )
        except (ZeroDivisionError, InvalidOperation):
            return 0


@view_config(
    name="_activate_multivotes",
    context=IMeeting,
    permission=security.MODERATE_MEETING,
    renderer="voteit.multiple_votes:templates/activate_form.pt",
)
class ActivateMultiVotes(DefaultAddForm):
    title = ""
    type_name = "MultiVotes"

    def save_success(self, appstruct):
        del appstruct["confirm"]
        multi_votes = self.request.content_factories[self.type_name](**appstruct)
        self.context[MEETING_NAMESPACE] = multi_votes
        return HTTPFound(location=self.request.resource_url(multi_votes))


@view_config(context=IVoteAssignment)
def redirect_parent(context, request):
    return HTTPFound(
        location=request.resource_path(context.__parent__, anchor=context.uid)
    )


def includeme(config):
    config.scan(__name__)
