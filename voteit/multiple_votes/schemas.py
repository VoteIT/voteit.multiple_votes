import colander
import deform
from arche.validators import existing_userids
from pyramid.threadlocal import get_current_request
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
        validator=colander.Function(
            _only_true_validator, _("Confirmation not clicked")
        ),
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
        missing="",
    )


def splitrows(text):
    results = []
    for row in text.splitlines():
        results.append(row.split("\t"))
    return results


class VoteAssignmenRow(colander.TupleSchema):
    title = colander.SchemaNode(colander.String())
    votes = colander.SchemaNode(
        colander.Int(), validator=colander.Range(max=500, min=1)
    )
    email = colander.SchemaNode(
        colander.String(), validator=colander.Email(), missing=""
    )


def validate_rows(node, value):
    i = 1
    schema = VoteAssignmenRow()
    for row in value:
        if len(row) == 2:
            # To avoid trim
            row.append("")
        if len(row) == 3:
            try:
                schema.deserialize(row)
            except colander.Invalid as exc:
                request = get_current_request()
                for (k, v) in exc.asdict(translate=request.localizer.translate).items():
                    # Only one error needed
                    msg = _(
                        "colander_csv_error",
                        default="Row ${num} - item ${item} error: ${err_msg}",
                        mapping={"num": i, "item": k, "err_msg": v},
                    )
                    raise colander.Invalid(node, msg)
        elif len(row) == 1 and not row[0]:
            pass
        else:
            raise colander.Invalid(
                node, _("Row ${num} must have 3 elements", mapping={"num": i})
            )
        i += 1


class VoteAssignmentCreateCSV(colander.Schema):
    csv_items = colander.SchemaNode(
        colander.String(),
        title=_(
            "paste_spreadsheet_text_description",
            default="Paste rows from Excel, Google docs, Libre-office or similar.",
        ),
        description=_(
            "paste_spreadsheet_text_description",
            default="Columns must be: Title of organisation, Number of votes, user email (or blank).",
        ),
        widget=deform.widget.TextAreaWidget(rows=10),
        preparer=splitrows,
        validator=validate_rows,
    )


def includeme(config):
    config.add_schema("MultiVotes", AddMultiVotesSchema, "add")
    config.add_schema("MultiVotes", MultiVotesSchema, "edit")
    config.add_schema("VoteAssignment", VoteAssignmentSchema, ["add", "edit"])
    config.add_schema("VoteAssignment", VoteAssignmentCreateCSV, ["create_csv"])
