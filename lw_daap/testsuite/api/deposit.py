# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.


#!/usr/bin/env python

import requests
import json
import codecs
import sys

site_url = "https://daap-prod.aeonium.eu/"
create_url = site_url + "api/deposit/depositions/?access_token=%s"
files_url = site_url + "api/deposit/depositions/%d/files?access_token=%s"
publish_url = site_url + "api/deposit/depositions/%d/actions/publish?access_token=%s"
access_token="VKUvgwp7NTyxD1McAIGUHoiAHdKTalE7NOvhggSnAQ9pC51v8TgaAUSDkO45"

def create(metadata):
  try:
    data = '{ "metadata": ' + metadata + '}'
    r = requests.post(create_url % access_token,
			  data=data, headers={"Content-Type": "application/json"},
        verify=False)
    if 'id' in r.json():
      recid = r.json()['id']
      print "RECORD %d => %s, %s" % (recid, r.status_code, r.reason)
      return recid
    else:
      print "CANT CREATE RECORD"
      print json.dumps(r.json(), indent=3)
      return None
  except:
    raise

def upload(recid, rfile):
  try:
    data = rfile
    files = {'file': open(rfile['filename'], 'rb')}
    r = requests.post(files_url % (recid, access_token), data=data, files=files, verify=False)
    print " --> FILE %s => %s, %s" % (rfile['filename'], r.status_code, r.reason)
  except:
    raise


def publish(recid):
  try:
    r = requests.post(publish_url % (recid, access_token), verify=False)
    print " --> PUBLISH => %s, %s" % (r.status_code, r.reason)
  except:
    raise


if __name__ == "__main__":
  try:
    fd = open(sys.argv[1])
    records = json.load(fd)
  except:
    raise

  for record in records['records']:
    recid = create(json.dumps(record['metadata']))
    if recid:
      files = record['files']
      for f in files:
        upload(recid, f)
      publish(recid)
    print '\r'





