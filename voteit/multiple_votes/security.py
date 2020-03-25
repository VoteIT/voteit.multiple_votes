from arche.models.workflow import Workflow
from voteit.core import security

from voteit.multiple_votes import _


class LockAssignmentWorkflow(Workflow):
    name = "lock_assignment"
    title = _("Lock assignment workflow")
    # description = _("")
    states = {"open": _("Open"), "locked": _("Locked")}
    transitions = {}
    initial_state = "open"

    @classmethod
    def init_acl(cls, registry):
        aclreg = registry.acl
        # Open
        open_name = "%s:open" % cls.name
        open_acl = aclreg.new_acl(open_name, title=_("Open"))
        open_acl.add(security.ROLE_ADMIN, security.ALL_PERMISSIONS)
        open_acl.add(security.ROLE_MODERATOR, [security.MODERATE_MEETING, security.EDIT])
        open_acl.add(security.ROLE_VIEWER, [security.VIEW])
        # Locked
        locked_name = "%s:locked" % cls.name
        locked_acl = aclreg.new_acl(locked_name, title=_("Locked"))
        locked_acl.add(security.ROLE_ADMIN, [security.MODERATE_MEETING, security.VIEW])
        locked_acl.add(security.ROLE_MODERATOR, [security.MODERATE_MEETING])
        locked_acl.add(security.ROLE_VIEWER, [security.VIEW])


LockAssignmentWorkflow.add_transitions(
    from_states="open",
    to_states="locked",
    title=_("Lock vote changes"),
    permission=security.MODERATE_MEETING,
)

LockAssignmentWorkflow.add_transitions(
    from_states="locked",
    to_states="open",
    title=_("Enable vote updates"),
    permission=security.MODERATE_MEETING,
)


def includeme(config):
    config.add_workflow(LockAssignmentWorkflow)
