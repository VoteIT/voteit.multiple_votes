# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from arche.testing import barebone_fixture
from pyramid import testing
from voteit.core.models.meeting import Meeting
from voteit.core.security import ROLE_VOTER
from voteit.multiple_votes import MEETING_NAMESPACE


class MultiVotesTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from voteit.multiple_votes.resources import MultiVotes
        return MultiVotes

    @property
    def _VA(self):
        from voteit.multiple_votes.resources import VoteAssignment
        return VoteAssignment

    def test_get_assignments(self):
        obj = self._cut()
        obj['a1'] = a1 = self._VA(userid_assigned='a', votes=1)
        obj['a2'] = a2 = self._VA(userid_assigned='a', votes=2)
        obj['a3'] = a3 = self._VA(userid_assigned='a', votes=4)
        obj['b1'] = b1 = self._VA(userid_assigned='b', votes=8)
        obj['b2'] = b2 = self._VA(userid_assigned='b', votes=16)
        self.assertEqual([a1, a2, a3], list(obj.get_assignments('a')))
        self.assertEqual([b1, b2], list(obj.get_assignments('b')))
        self.assertEqual([], list(obj.get_assignments('404')))

    def test_get_vote_power(self):
        obj = self._cut()
        obj['a1'] = a1 = self._VA(userid_assigned='a', votes=1)
        obj['a2'] = a2 = self._VA(userid_assigned='a', votes=2)
        obj['a3'] = a3 = self._VA(userid_assigned='a', votes=4)
        obj['b1'] = b1 = self._VA(userid_assigned='b', votes=8)
        obj['b2'] = b2 = self._VA(userid_assigned='b', votes=16)
        self.assertEqual(7, obj.get_vote_power('a'))
        self.assertEqual(24, obj.get_vote_power('b'))
        self.assertEqual(0, obj.get_vote_power('404'))

    def test_vote_count_subscriber(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.include('voteit.multiple_votes.resources')
        root = barebone_fixture()
        root['m'] = m = Meeting()
        m[MEETING_NAMESPACE] = obj = self._cut()
        self.assertEqual(0, obj.total_votes)
        obj['a1'] = a1 = self._VA(userid_assigned='a', votes=1)
        self.assertEqual(1, obj.total_votes)
        obj['a2'] = a2 = self._VA(userid_assigned='a', votes=2)
        self.assertEqual(3, obj.total_votes)
        obj['a3'] = a3 = self._VA(userid_assigned='a', votes=4)
        self.assertEqual(7, obj.total_votes)
        del obj['a3']
        self.assertEqual(3, obj.total_votes)
        a1.update(votes=10)
        self.assertEqual(12, obj.total_votes)

    def test_voter_count_subscriber(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.include('voteit.multiple_votes.resources')
        root = barebone_fixture()
        root['m'] = m = Meeting()
        m[MEETING_NAMESPACE] = obj = self._cut()
        self.assertEqual(0, obj.total_voters)
        obj['a1'] = a1 = self._VA(userid_assigned='a', votes=1)
        self.assertEqual(1, obj.total_voters)
        obj['a2'] = a2 = self._VA(userid_assigned='a', votes=2)
        self.assertEqual(1, obj.total_voters)
        obj['b1'] = b1 = self._VA(userid_assigned='b', votes=4)
        self.assertEqual(2, obj.total_voters)
        del obj['b1']
        self.assertEqual(1, obj.total_voters)
        a1.update(userid_assigned='c')
        self.assertEqual(2, obj.total_voters)

    def test_get_voters(self):
        obj = self._cut()
        obj['a1'] = a1 = self._VA(userid_assigned='a', votes=1)
        obj['b1'] = b1 = self._VA(userid_assigned='b', votes=8)
        self.assertEqual({'a', 'b'}, obj.get_voters())

    def test_recheck_voters(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.include('voteit.multiple_votes.resources')
        root = barebone_fixture()
        root['m'] = m = Meeting()
        m[MEETING_NAMESPACE] = obj = self._cut()
        lr = m.local_roles
        lr.add('someone', ROLE_VOTER)
        obj['a'] = a = self._VA(userid_assigned='a', votes=2)
        obj['b'] = b = self._VA(userid_assigned='b', votes=4)
        obj.recheck_voters()
        self.assertEqual({'a', 'b'}, set(lr.get_any_local_with(ROLE_VOTER)))


class VoteTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from voteit.multiple_votes.resources import VoteAssignment
        return VoteAssignment
