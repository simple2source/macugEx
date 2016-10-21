import unittest
import time
import sys

sys.path.append('../app')
from core.tools import set_user_session
from app.api.tools import get_session_user_id, del_session, redis, clean_user_redis, \
    restore_user_struct, ObjectId, db, generate_session, generate_group_id, add_user_groups, del_user_groups, \
    get_user_first_group_id, verify_user_in_group, E_user_nohas_groups, E_user_notin_group


class TestSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._user_id = ObjectId('123' * 4)
        cls.user_id = str(cls._user_id)
        cls.session = generate_session()
        db.user.update({'_id': cls._user_id}, {'set': {'tets': 'test'}}, upsert=True)
        cls.group_id = generate_group_id()

    @classmethod
    def tearDownClass(cls):
        del_session(cls.session)
        clean_user_redis(cls.user_id)
        db.user.delete_one({'_id': cls._user_id})

    def test_basic_session(self):
        set_user_session(self.session, self.user_id)
        user_id = get_session_user_id(self.session)
        self.assertEqual(user_id, self.user_id)

        del_session(self.session)
        user_id = get_session_user_id(self.session)
        self.assertIs(user_id, None)

    def test_user_session(self):
        set_user_session(self.session, self.user_id)
        session = redis.hget('User:%s' % self.user_id, 'session')
        self.assertEqual(session, self.session)

        clean_user_redis(self.user_id)
        session = redis.hget('User:%s' % self.user_id, 'session')
        self.assertIs(session, None)

        restore_user_struct(self.user_id)
        session = redis.hget('User:%s' % self.user_id, 'session')
        self.assertEqual(session, self.session)

    def test_user_groups(self):
        now = time.time()
        group_id = get_user_first_group_id(self.user_id)
        self.assertIs(group_id, None)
        errno = verify_user_in_group(self.user_id, self.group_id)
        self.assertEqual(errno, E_user_nohas_groups)

        add_user_groups(self.user_id, self.group_id, now)
        group_id = get_user_first_group_id(self.user_id)
        self.assertEqual(group_id, self.group_id)
        errno = verify_user_in_group(self.user_id, self.group_id)
        self.assertIs(errno, None)

        del_user_groups(self.user_id, self.group_id, now)
        group_id = get_user_first_group_id(self.user_id)
        self.assertIs(group_id, None)
        errno = verify_user_in_group(self.user_id, self.group_id)
        self.assertEqual(errno, E_user_notin_group)
