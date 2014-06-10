#!/usr/bin/python

from rsapi import rsapi
from rsapi_repository import rsapi_repository as repo

class rsapi_working():
    def __init__(self, api_type="dev"):
        self.api = rsapi(api_type)
        self.repo = repo(api_type)
        with open('config.json','r') as f:
            self.config = f.read()

    def import_cookbooks(repoid, commitid, trial=0):
        status_json = self.repo.get_repository_status(repoid)
        if "completed successfully" in status_json['fetch_status']['output'] and status_json['fetch_status']['succeeded_commit'] == commitid:
            assets = self.repo.get_repository_assets(repoid)
            hrefs = []
            for cb in assets:
                for link_sub in cb['links']:
                    hrefs.append(link_sub['href'])
            href_array = self.api.rs_array_generator(hrefs, "asset_hrefs")
            api_uri="%s/repositories/%d/cookbook_import.json" % (self.config['apibase'], repoid)
            return self.api.rs_post(api_uri, 204, href_array)
        else:
            if trial < 20:
                trial +=1
                t = Timer(15, self.import_cookbooks, (repoid, commitid, trial))
                t.start()

    def refetch_repository(self, repoid, commitid):
        api_uri="%s/repositories/%d/refetch.json" % (self.config['apibase'], repoid)
        refetch = self.api.rs_post(api_uri, 204)
        working.import_cookbooks(repoid, commitid)
        return refetch