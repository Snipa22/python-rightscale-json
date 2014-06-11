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

    def import_cookbooks(self, repoid, commitid, trial=0):
        status_json = self.repo.get_repository_status(repoid)
        if "completed successfully" in status_json['fetch_status']['output'] and status_json['fetch_status']['succeeded_commit'] == commitid:
            assets = self.repo.get_repository_assets(repoid)
            hrefs = []
            for cb in assets:
                for link_sub in cb['links']:
                    hrefs.append(link_sub['href'])
            href_array = self.api.rs_array_generator(hrefs, "asset_hrefs")
            api_uri="%s/repositories/%d/cookbook_import" % (self.config['apibase'], repoid)
            return self.api.rs_post(api_uri, 204, href_array)
        else:
            if trial < 20:
                trial +=1
                t = Timer(15, self.import_cookbooks, (repoid, commitid, trial))
                t.start()

    def refetch_repository(self, repoid, commitid):
        api_uri="%s/repositories/%d/refetch.json" % (self.config['apibase'], repoid)
        refetch = self.api.rs_post(api_uri, 204)
        self.import_cookbooks(repoid, commitid)
        return refetch

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