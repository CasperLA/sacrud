# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import unittest
from sacrud.tests.test_models import User, Profile, PHOTO_PATH
from sacrud.action import get_relations, delete_fileobj, read, update, delete
from sacrud.action import get_pk, index, create
from pyramid.testing import DummyRequest
from StringIO import StringIO
import glob
import os


class MockCGIFieldStorage(object):
    pass


class SacrudTests(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        session = Session()
        # You probably need to create some tables and 
        # load some test data, do so here.
        self.session = session
        # To create tables, you typically do:
        #User.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Profile.metadata.create_all(engine)

    def tearDown(self):
        def clear_files():
            for filename in glob.glob("%s/*.html" % (PHOTO_PATH, )):
                os.remove(os.path.join(PHOTO_PATH, filename))
        clear_files()

    def test_relations(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        self.session.commit()
        profile = Profile(user=user)

        self.session.add(profile)
        self.session.commit()

        profile = self.session.query(Profile).get(1)
        self.assertEqual(get_relations(user), [('profile',
                                                [profile, ])])
        self.session.delete(profile)
        self.session.delete(user)

    def test_get_pk(self):
        pk = get_pk(User)
        self.assertEqual("id", pk)

    def test_index(self):
        user = User(u'Vasya', u'Pupkin', u"123")

        self.session.add(user)
        self.session.commit()

        result = index(self.session, User)
        self.assertEqual(result['pk'], 'id')
        self.assertEqual(result["prefix"], "crud")
        self.assertEqual(result["table"], User)
        self.assertEqual(result["row"], [user, ])
        self.session.delete(user)

    def test_create(self):

        request = DummyRequest()
        request['name'] = ["Vasya", ]
        request['fullname'] = ["Vasya Pupkin", ]
        request['password'] = ["123", ]

        create(self.session, User, request)
        user = self.session.query(User).get(1)
        self.assertEqual(user.name, "Vasya")
        self.assertEqual(user.fullname, "Vasya Pupkin")
        self.assertEqual(user.password, "123")

        request = DummyRequest()
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["1", ]

        create(self.session, Profile, request)

        profile = self.session.query(Profile).get(1)
        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(profile.salary, float(23))
        self.assertEqual(profile.user.id, 1)

        self.session.delete(profile)
        self.session.delete(user)

    def test_read(self):
        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        self.session.commit()

        result = read(self.session, User, 1)
        self.assertEqual(result['obj'].id, 1)
        self.assertEqual(result['pk'], "id")
        self.assertEqual(result['prefix'], "crud")
        self.assertEqual(result['table'], User)
        self.assertEqual(result['rel'], [('profile', [])])

    def test_update(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        self.session.commit()

        profile = Profile(user=user, salary="25.7")

        self.session.add(profile)
        self.session.commit()

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        self.session.commit()

        profile = self.session.query(Profile).get(1)
        request = DummyRequest()
        request['phone'] = ["213123123", ]
        request['cv'] = ["Vasya Pupkin was born in Moscow", ]
        request['married'] = ["true", ]
        request["salary"] = ["23.0", ]
        request["user_id"] = ["2", ]

        upload = MockCGIFieldStorage()
        upload.file = StringIO('foo')
        upload.filename = 'foo.html'
        request["photo"] = [upload, ]

        update(self.session, Profile, 1, request)

        self.assertEqual(profile.phone, "213123123")
        self.assertEqual(profile.cv, "Vasya Pupkin was born in Moscow")
        self.assertEqual(profile.married, True)
        self.assertEqual(profile.user.id, 2)
        self.assertEqual(profile.salary, float(23))

    def test_delete(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        self.session.commit()

        profile = Profile(user=user, salary="25.7")

        self.session.add(profile)
        self.session.commit()
        delete(self.session, Profile, 1)
        self.session.commit()
        profile = self.session.query(Profile).get(1)
        self.assertEqual(profile, None)

 