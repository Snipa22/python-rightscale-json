#!/usr/bin/python

from rsapi import rsapi
import simplejson as json

class rsapi_repository():
    """Class for handling all repository API access

    Pretty much if the call has to access an API URI for repositories, it ends up here.
    """
    def __init__(self, api_type="dev"):
        """Fairly simple init, not too much it has to call on

        KwArgs:
            api_type (str): Determines what API connection is being opened.  Rightscale maps API:Account, so this determines the API key that will be loaded from config.json in rsapi
        """
        self.api = rsapi(api_type)
        with open('config.json','r') as f:
            self.config = json.loads(f.read())

    def get_repositories(self):
        """Implements the index function of Repositories

        Provides a dict of all repositories available from the base API key
        """
        api_uri="%s/repositories" % self.config['apibase']
        return self.api.rs_get(api_uri)

    def get_repository_status(self, repoid):
        """Implements the show function of Repositories

        Provides a dict of all available repostory information.

        Args:
            repoid (int): Rightscale ID of the repository
        """
        api_uri="%s/repositories/%d.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)
            
    def get_repository_assets(self, repoid):
        """Implements the index function of RepositoryAssets

        Provides a dict of specific assets in the repository

        Args:
            repoid (int): Rightscale ID of the repository
        """
        api_uri="%s/repositories/%d/repository_assets.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)

    def add_repository(self, post_val = {}):
        """Implements the add function of Repositories

        UNTESTED - Designed to add a new repository progrmatically wi

        KwArgs:
            postval (dict): Dictionary of valid information to add a new repository to Rightscale
        """
        api_uri="%s/repositories" % self.config['apibase']
        if post_val['name'] == "":
            raise rsapi_exception("No name provided for repository")
        if post_val['source'] == "":
            raise rsapi_exception("No source provided for repository")
        if post_val['source_type'] != "git" or post_val['source_type'] != "svn" or post_val['source_type'] != "download":
            raise rsapi_exception("Improper source type defined")
        return self.api.rs_post(api_uri, 201, self.api.rs_hash_generator(post_val, "repository"))

    def import_cookbooks(self, repoid, commitid, trial=0):
        """Implements the cookbook_import function of Repositories

        Imports cookbooks once they've been refreshed by refetch_repository

        Args:
            repoid (dict): Rightscale ID of the repository
            commitid (string): String of the latest commit to ensure that the API imported correctly

        KwArgs:
            trial = Number of tries so far, system is timer based for 15 second delays
        """
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
        """Implements the refetch function of Repositories

        Schedules import of cookbook from remote repository.  Schedules run of import_cookbooks to pull latest versions if good.

        Args:
            repoid (dict): Rightscale ID of the repository
            commitid (string): String of the latest commit to ensure that the API imports correctly
        """
        api_uri="%s/repositories/%d/refetch.json" % (self.config['apibase'], repoid)
        refetch = self.api.rs_post(api_uri, 204)
        self.import_cookbooks(repoid, commitid)
        return refetch