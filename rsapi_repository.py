#!/usr/bin/python

from rsapi import rsapi

class rsapi_repository():
    def __init__(self, api_type="dev"):
        self.api = rsapi(api_type)
        with open('config.json','r') as f:
            self.config = f.read()

    def get_repository_status(self, repoid):
        api_uri="%s/repositories/%d.json" (self.config['apibase'], repoid)
        return self.rs_get(api_uri)
            
    def get_repository_assets(self, repoid):
        api_uri="%s/repositories/%d/repository_assets.json" % (self.config['apibase'], repoid)
        return self.rs_get(api_uri)

