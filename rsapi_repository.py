#!/usr/bin/python

from rsapi import rsapi
import simplejson as json

#ToDo
#index - Done
#show - Done
#create - Done
#update - Done
#destroy - Done
#cookbook_import - Done
#cookbook_import_preview - Not doing
#refetch - Done
#resolve - Done

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

    def get_repositories(self, namefilter=None, view=False):
        """Implements the index function of Repositories

        Provides a dict of all repositories available from the base API key

        KwArgs:
            namefilter (dict): Dictionary in the format: {'description': ['desc1', 'desc2'], 'name': ['name1', 'name2']}
            view (bool): False = Default, true = Extended

        Works:
            System will return repositories as expected
            System will accept 1 description + 1 filter, additionals will override ther original.

        ToDo:
            System does not fully work because python sanely handles duplicate keys.  RS will need to provide an alternate method for handling filters

        """
        api_uri="%s/repositories" % self.config['apibase']
        data = {}
        if namefilter:
            for k,v in namefilter.iteritems():
                data.update(self.api.rs_array_generator(v,k))
        if view:
            data['view'] = 'extended'
        else:
            data['view'] = 'default'
        return self.api.rs_get(api_uri, payload=data)

    def get_repository_status(self, repoid, view=False):
        """Implements the show function of Repositories

        Provides a dict of all available repostory information.

        Complete - Works!

        KwArgs:
            view (bool): False = Default, true = Extended

        Args:
            repoid (int): Rightscale ID of the repository
        """
        api_uri="%s/repositories/%d.json" % (self.config['apibase'], repoid)
        data = {}
        if view:
            data['view'] = 'extended'
        else:
            data['view'] = 'default'
        return self.api.rs_get(api_uri, payload=data)

    def add_repository(self, post_val = {}):
        """Implements the add function of Repositories

        Complete - Works!

        KwArgs:
            postval (dict): Dictionary of valid information to add a new repository to Rightscale
        """
        api_uri="%s/repositories" % self.config['apibase']
        try:
            if post_val['name'] == "":
                raise self.api.rsapi_exception("No name provided for repository")
            if post_val['source'] == "":
                raise self.api.rsapi_exception("No source provided for repository")
            if post_val['source_type'] != "git" and post_val['source_type'] != "svn" and post_val['source_type'] != "download":
                raise self.api.rsapi_exception("Improper source type defined")
        except KeyError:
            return False
        return self.api.rs_post(api_uri, 201, self.api.rs_hash_generator(post_val, "repository"))

    def update_repository(self, repoid, cred, cred_type=True):
        """Implements the update function of Repositories

        Designed to update a repository's credentials as-needed.

        Args:
            repoid (int): Rightscale ID of the repository
            cred_type (bool): True for credential, false for raw text
            cred (str): Value to insert
        """
        api_uri="%s/repositories/%d" % (self.config['apibase'], repoid)
        if cred_type:
            update_data = "cred:" + cred
        else:
            update_data = "text:" + cred
        return self.api.rs_put(api_uri, 204, update_data)

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

    def refetch_repository(self, repoid, commitid, auto_import=False):
        """Implements the refetch function of Repositories

        Schedules import of cookbook from remote repository.

        Complete - Works!

        Args:
            repoid (dict): Rightscale ID of the repository
            commitid (string): String of the latest commit to ensure that the API imports correctly
            auto_import (bool): Sets if the system should auto-import or not
        """
        if auto_import:
            postdata = {'auto_import': 'true'}
        else:
            postdata = {'auto_import': 'false'}
        api_uri="%s/repositories/%d/refetch.json" % (self.config['apibase'], repoid)
        refetch = self.api.rs_post(api_uri, 204, postdata)
        return refetch


    def resolve_repository(self, books = None):
        """Implements the resolve function of Repositories

        Designed to provide a dict with all repositories that have the listed cookbooks imported

        ToDo:
            System does not fully work because python sanely handles duplicate keys.  RS will need to provide an alternate method for handling the books list

        Args:
            books (list): List of books to check for
        """
        api_uri="%s/repositories/resolve" % self.config['apibase']
        if isinstance(books, list):
            booklist = self.api.rs_array_generator(books, "imported_cookbook_name")
            return self.api.rs_post(api_uri, 200, booklist)
        else:
            return self.api.rs_post(api_uri, 200, booklist)

    def get_repository_assets(self, repoid):
        """Implements the index function of RepositoryAssets

        Provides a dict of specific assets in the repository

        Args:
            repoid (int): Rightscale ID of the repository
        """
        api_uri="%s/repositories/%d/repository_assets.json" % (self.config['apibase'], repoid)
        return self.api.rs_get(api_uri)