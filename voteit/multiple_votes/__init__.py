from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory("voteit.multiple_votes")
MEETING_NAMESPACE = "_multiple_votes"


def includeme(config):
    config.include('.security')
    config.include('.resources')
    config.include('.schemas')
    config.include('.portlet')
    config.include('.voting')
    # Views
    config.include('.actions')
    config.include('.views')
