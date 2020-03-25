import colander
from arche.validators import existing_userids
from voteit.core.schemas.common import MeetingUserReferenceWidget

from voteit.multiple_votes import _


class BaseMultiVotesSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=20),
        title=_("Short title, used in navigation too"),
        description=_(
            "multivotes_schema_title_description",
            default="Max 20 chars. Something like 'Organisations' or 'Vote power'. "
            "Basically the reason that someone has several votes.",
        ),
    )


def _only_true_validator(value):
    return value == True  # Only allow pass if checkbox was ticked


class AddMultiVotesSchema(BaseMultiVotesSchema):
    confirm = colander.SchemaNode(
        colander.Bool(),
        title=_("I understand the consequences of adding this"),
        validator=colander.Function(_only_true_validator, _("Confirmation not clicked"))
    )


class MultiVotesSchema(BaseMultiVotesSchema):
    pass


class VoteAssignmentSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title=_(
            "Name of voting asignment - like the organisation that this represents"
        ),
    )
    votes = colander.SchemaNode(
        colander.Int(),
        title=_("Number of votes"),
        description=_("1-500 is a valid number"),
        default=1,
        validator=colander.Range(max=500, min=1),
    )
    userid_assigned = colander.SchemaNode(
        colander.String(),
        title=_("The user assigned"),
        widget=MeetingUserReferenceWidget(multiple=False),
        validator=existing_userids,
        missing=""
    )


def includeme(config):
    config.add_schema('MultiVotes', AddMultiVotesSchema, 'add')
    config.add_schema('MultiVotes', MultiVotesSchema, 'edit')
    config.add_schema('VoteAssignment', VoteAssignmentSchema, ['add', 'edit'])
