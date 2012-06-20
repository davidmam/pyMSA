# Copyright (c) 2012 - N.P. de Klein
#
#     This file is part of Python Mass Spec Analyzer (PyMSA).
#
#     Python Mass Spec Analyzer (PyMSA) is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Python Mass Spec Analyzer (PyMSA) is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Python Mass Spec Analyzer (PyMSA).  If not, see <http://www.gnu.org/licenses/>.")


"""
Running this file creates pyMS_database.db. This script executes the statements in pyMS_database_createStatements.sqlite
"""

import sys
try:
    # to be able to import pysqlite2
    sys.path.append('/sw/opt/lib/python2.6/site-packages/')
except:
    pass
from pysqlite2 import dbapi2 as sqlite
import os


from os.path import realpath
# make a connection to a database
db_conn = sqlite.connect('pyMSA_database.db')

# A cursor object is the means by which we issue SQL statements to our database and then get the results. To run a specific SQL statement use the execute method:
db_curs = db_conn.cursor()


# read in the sql create statements from a text file
sql = open('pyMSA_database_createStatements.sqlite', 'r').read()
db_curs.executescript(sql)
