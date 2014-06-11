#!/usr/bin/python

from rsapi import rsapi
import simplejson as json

class rsapi_repository():
    """Class for handling all repository API access
    """
    def __init__(self, api_type="dev"):
        self.api = rsapi(api_type)
        with open('config.json','r') as f:
            self.config = json.loads(f.read())

    def get_repositories(self):
        """Implements the index function of Repositories

        Provides a standard python dict of all repositories available from the base API key

        """
        api_uri="%s/repositories" % self.config['apibase']
        return self.api.rs_get(api_uri)

    def get_repository_status(self, repoid):
        api_uri="%s/repositories/%d.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)
            
    def get_repository_assets(self, repoid):
        api_uri="%s/repositories/%d/repository_assets.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)

    def add_repository(self, post_val = {}):
        api_uri="%s/repositories" % self.config['apibase']
        if post_val['name'] == "":
            raise rsapi_exception("No name provided for repository")
        if post_val['source'] == "":
            raise rsapi_exception("No source provided for repository")
        if post_val['source_type'] != "git" or post_val['source_type'] != "svn" or post_val['source_type'] != "download":
            raise rsapi_exception("Improper source type defined")
        return self.api.rs_post(api_uri, 201, self.api.rs_hash_generator(post_val, "repository"))

    def import_cookbooks(self, repoid, commitid, trial=0):
        status_json = self.get_repository_status(repoid)
        if "completed successfully" in status_json['fetch_status']['output'] and status_json['fetch_status']['succeeded_commit'] == commitid:
            assets = self.get_repository_assets(repoid)
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