#!/usr/bin/python

from rsapi import rsapi

class rsapi_repository():
    def __init__(self, api_type="dev"):
        self.api = rsapi(api_type)
        with open('config.json','r') as f:
            self.config = f.read()

    def get_repository_status(self, repoid):
        api_uri="%s/repositories/%d.json" (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)
            
    def get_repository_assets(self, repoid):
        api_uri="%s/repositories/%d/repository_assets.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)

    def create_repository(self, post_val = {}):
        api_uri="%s/repositories" % self.config['apibase']
        if post_val['name'] == "":
            raise rsapi_exception("No name provided for repository")
        if post_val['source'] == "":
            raise rsapi_exception("No source provided for repository")
        if post_val['source_type'] != "git" or post_val['source_type'] != "svn" or post_val['source_type'] != "download":
            raise rsapi_exception("Improper source type defined")
        return self.api.rs_post(api_uri, 201, self.api.rs_hash_generator(post_val, "repository"))