#!/usr/bin/python

from rsapi import rsapi
from rsapi_repository import rsapi_repository as repo
import simplejson as json
import re

class rsapi_working():
    def __init__(self, api_type="dev"):
        self.api = rsapi(api_type)
        self.repo = repo(api_type)
        self.regex = {'gitname': re.compile("(.*)\.git")}
        with open('config.json','r') as f:
            self.config = json.loads(f.read())

    def fetch_repository_map(self):
        # Designed for use with GitHub only.  Do not rely on for any other type!
        data = self.repo.get_repositories()
        retval={}
        for k in data:
            for k2,v2 in k.iteritems():
                if k2 == "links":
                    repoid = int(v2[0]['href'].split('/').pop())
                if k2 == "source":
                    reponame = self.regex['gitname'].search(v2.split('/').pop()).group(1)
            retval[reponame] = repoid
        return retval