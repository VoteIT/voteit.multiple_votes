from voteit.core import security
from voteit.core.views.control_panel import control_panel_category, control_panel_link

from voteit.multiple_votes import _, MEETING_NAMESPACE


def _is_active(context, request, va=None):
    return MEETING_NAMESPACE in request.meeting


def only_when_active(view_action):
    def wrapper(context, request, va, **kw):
        if _is_active(context, request):
            return view_action(context, request, va, **kw)

    return wrapper


def only_when_inactive(view_action):
    def wrapper(context, request, va, **kw):
        if not _is_active(context, request):
            return view_action(context, request, va, **kw)

    return wrapper


@only_when_active
def multivotes_nav(context, request, va, **kw):
    multivotes = request.meeting[MEETING_NAMESPACE]
    return """<li><a href="%s">%s</a></li>""" % (
        request.resource_path(multivotes),
        multivotes.title,
    )


def includeme(config):
    config.add_view_action(
        control_panel_category,
        "control_panel",
        "multivotes",
        panel_group="control_panel_multivotes",
        title=_("Multiple votes"),
        description=_(
            "Allow users to have multiple votes. This will change how you're able to invite users too."
        ),
        permission=security.MODERATE_MEETING,
        check_active=_is_active,
    )
    config.add_view_action(
        only_when_inactive(control_panel_link),
        "control_panel_multivotes",
        "activate",
        title=_("Activate..."),
        view_name="_activate_multivotes",
    )
    config.add_view_action(multivotes_nav, "nav_meeting", "multivotes")
    config.add_view_action(multivotes_nav, "control_panel_multivotes", "multivotes_page")

