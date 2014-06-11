#!/usr/bin/python

from rsapi import rsapi
from rsapi_repository import rsapi_repository as repo
from rsapi_cookbooks import rsapi_cookbooks as cbook
import simplejson as json
import re
from threading import Timer

class rsapi_working():
    """Class for working functions to support scripts as-needed, and could be used in general

    No API calls should be made directly
    """
    def __init__(self, api_type="dev"):
        """Fairly simple init, not too much it has to call on

        KwArgs:
            api_type (str): Determines what API connection is being opened.  Rightscale maps API:Account, so this determines the API key that will be loaded from config.json in rsapi
        """
        self.api = rsapi(api_type)
        self.repo = repo(api_type)
        self.books = cbook(api_type)
        self.regex = {'gitname': re.compile("(.*)\.git")}
        with open('config.json','r') as f:
            self.config = json.loads(f.read())

    def fetch_repository_map(self):
        """Maps the git repo name to the rightscale ID

        Example: git@place:user/(name).git
        Extracts the name and maps to rightscale ID.

        Returns:
            dict.   Example::
                {'thisisagit': 243757345}

        General formatting is Name: ID, for usage later in quick lookups.  Used in the example rightscale_github.py
        """
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

    def update_template_cookbook(self, cbook, count = 0, tries = 20):
        data = self.books.get_cookbooks()
        repos = []
        for i in data: 
            if i['name'].lower() == cbook.lower():
                repos.append(i['id'])
        intcount = len(repos)
        if (count == intcount or count == 0) and tries > 0:
            t = Timer(15.0, self.update_template_cookbook, [cbook, intcount, tries-1])
            t.start()
        else:
            repos.sort()
            last = repos.pop()
            templatelist = []
            for i in repos:
                attaches = self.books.get_attachments(i)
                for attach in attaches:
                    for link in attach['links']:
                        if link['rel'] == "server_template":
                            templatelist.append(link['href'].split("/")[3])
            for i in templatelist:
                self.books.make_attachment(int(i), last)
