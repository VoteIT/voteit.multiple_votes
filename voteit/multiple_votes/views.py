from __future__ import unicode_literals

from decimal import Decimal
from decimal import InvalidOperation

from arche.views.base import DefaultAddForm
from arche.views.base import BaseView
from arche.views.base import BaseForm
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config
from voteit.core import security
from voteit.core.models.interfaces import IMeeting

from voteit.multiple_votes import MEETING_NAMESPACE
from voteit.multiple_votes.interfaces import IMultiVotes
from voteit.multiple_votes.interfaces import IVoteAssignment
from voteit.multiple_votes.permissions import ADD_VOTE_ASSIGNMENT
from voteit.multiple_votes.schemas import VoteAssignmentSchema
from voteit.multiple_votes.utils import block_during_ongoing_poll
from voteit.multiple_votes import _


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

    def __call__(self):
        block_during_ongoing_poll(self.context)
        return super(ActivateMultiVotes, self).__call__()

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


@view_config(
    name="create_assignments",
    context=IMultiVotes,
    permission=security.MODERATE_MEETING,
    renderer="arche:templates/form.pt",
)
class CreateAndAssignForm(BaseForm):
    title = _("Create and assign")
    type_name = "VoteAssignment"
    schema_name = "create_csv"

    def __call__(self):
        block_during_ongoing_poll(self.context)
        if not self.request.has_permission(ADD_VOTE_ASSIGNMENT, self.context):
            if self.context.wf_state == 'locked':
                msg = _("Not alled when assignment is locked. Open it to use this")
                self.flash_messages.add(msg, type="danger")
                raise HTTPFound(location=self.request.resource_url(self.context))
            else:
                raise HTTPForbidden(_("Forbidden"))
        return super(CreateAndAssignForm, self).__call__()

    def save_success(self, appstruct):
        factory = self.request.content_factories["VoteAssignment"]
        get_user_by_email = self.request.root["users"].get_user_by_email
        va_schema = VoteAssignmentSchema().bind(
            context=self.context, request=self.request
        )
        obj_count = 0
        assign_count = 0
        not_found_count = 0
        for row in appstruct["csv_items"]:
            userid = ""
            email = row[2]
            if email:
                # Only assign users that can be found via a validated email address
                # Blank assignment is ok
                user = get_user_by_email(email, only_validated=True)
                if user is None:
                    not_found_count += 1
                else:  # email not found
                    userid = user.userid
                    assign_count += 1
            payload = {"title": row[0], "votes": row[1], "userid_assigned": userid}
            kw = va_schema.deserialize(payload)
            obj = factory(**kw)
            self.context[obj.uid] = obj
            obj_count += 1
        msg = _(
            "created_msg_summary",
            default="Created ${obj_count} objects. ${assign_count} users were assigned via email. "
            "${not_found_count} email addresses didn't match a registered user.",
            mapping={
                "obj_count": obj_count,
                "assign_count": assign_count,
                "not_found_count": not_found_count,
            },
        )
        self.flash_messages.add(msg, type="info", auto_destruct=False)
        return HTTPFound(location=self.request.resource_url(self.context))


def includeme(config):
    config.scan(__name__)
