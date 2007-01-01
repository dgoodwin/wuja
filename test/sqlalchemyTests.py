#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" Experimental tests for using sqlalchemy and sqlite. """

import unittest
from sqlalchemy import *

class User(object):
    def __repr__(self):
        return "%s(%r,%r)" % (
            self.__class__.__name__, self.user_name, self.password)



class SQLAlchemyTests(unittest.TestCase):

    def setUp(self):
        self.db = create_engine('sqlite:///:memory:')
        self.metadata = BoundMetaData(self.db)

        # Echo SQL to the console:
        # self.metadata.engine.echo = True
        users_table = Table('users', self.metadata,
            Column('user_id', Integer, primary_key=True),
            Column('user_name', String(40)),
            Column('password', String(10))
        )
        users_table.create()

        usermapper = mapper(User, users_table)

        # Change to this if the table already exists:
        # users_table = Table('users', metadata, autoload=True)

    def test_create_user(self):
        u1 = User()
        session = create_session()
        u1.user_name = "Wu"
        u1.password = "Ja"
        session.save(u1)
        self.assertTrue(u1 in session)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLAlchemyTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

