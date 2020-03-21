import logging

from pyramid.i18n import TranslationStringFactory

log = logging.getLogger(__name__)


_ = TranslationStringFactory("voteit.multiple_votes")


def includeme(config):
    pass