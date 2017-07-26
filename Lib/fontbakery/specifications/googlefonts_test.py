# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import pytest

from fontbakery.testrunner import (
              PASS
#           , INFO
#           , WARN
#           , ERROR
#           , SKIP
            , FAIL
            , ENDTEST
#            , Section
            )

from fontTools.ttLib import TTFont

@pytest.fixture
def font_1():
  # FIXME: find absolute path via the path of this module
  path = 'data/test/cabin/Cabin-Regular.ttf'
  # return TTFont(path)
  return path

def change_name_table_id(ttFont, nameID, newEntryString, platEncID=0):
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID and nameRecord.platEncID == platEncID:
      nameRecord.string = newEntryString

def delete_name_table_id(ttFont, nameID):
  delete = []
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID:
      delete.append(i)
  for i in sorted(delete, reverse=True):
    del(ttFont['name'].names[i])

def test_id_029(font_1):
  """ This test is run via the testRunner and demonstrate how to get
      (mutable) objects from the conditions cache and change them.

      NOTE: the actual fontbakery tests of conditions should never change
      a condition object.
  """
  from fontbakery.testrunner import TestRunner
  from fontbakery.specifications.googlefonts import specification
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION
  values = dict(fonts=[font_1])
  runner = TestRunner(specification, values, explicit_tests=['com.google.fonts/test/029'])

  print('Test PASS ...')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status == ENDTEST:
     assert message == PASS
     break

  # we could also reuse the `iterargs` that was assigned in the previous
  # for loop, but this here is more explicit
  iterargs = ((u'font', 0),)
  ttFont = runner.get('ttFont', iterargs)

  print('Test failing entry ...')
  # prepare
  change_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION, 'failing entry')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    print(status, 'message', message)
    if status == ENDTEST:
     assert message == FAIL
     break

  print('Test missing entry ...')
  # prepare
  delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status == ENDTEST:
     assert message == FAIL
     break

def test_id_029_shorter(font_1):
  """ This is much more direct, as it calls the test directly.
      However, since these tests are often generators (using yield)
      we still need to get the last (in this case) iteration value,
      using `list(generator)[-1]` here.
  """
  from fontbakery.specifications.googlefonts import \
                                  check_copyright_entries_match_license
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION
  ttFont = TTFont(font_1)
  license = 'OFL.txt'

  print('Test PASS ...')
  # run
  status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
  assert status == PASS

  print('Test failing entry ...')
  # prepare
  change_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION, 'failing')
  # run
  status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
  assert status == FAIL

  print('Test missing entry ...')
  # prepare
  delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
  # run
  status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
  assert status == FAIL
