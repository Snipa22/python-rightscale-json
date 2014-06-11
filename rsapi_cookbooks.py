#!/usr/bin/python

from rsapi import rsapi
import simplejson as json

class rsapi_cookbooks():
    """Class for handling all cookbook API access

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

    def get_attachments(self, id_num = None, id_type = False):
        """Implements the index function of CookbookAttachments

        Bit more complex, multiple searching schemes.

        KwArgs:
            id_num (int): What ID should I be searching by if I'm not getting everything - None gets everything
            id_type (bool): True - Server_template ID, false = cookbook_ID
        """

        if id_num != None and id_type == False:
            api_uri="%s/cookbooks/%i/cookbook_attachments" % (self.config['apibase'], id_num)
        elif id_num != None and id_type == True:
            api_uri="%s/server_templates/%i/cookbook_attachments" % (self.config['apibase'], id_num)
        else:
            api_uri="%s/cookbook_attachments" % self.config['apibase']
        return self.api.rs_get(api_uri)

    def make_attachment(self, href, id_num = None, id_type = False):
        """Implements the create function of CookbookAttachments

        Bit more complex, multiple searching schemes.

        KwArgs:
            id_num (int): What ID should I be searching by if I'm not getting everything - None gets everything
            id_type (bool): True - Server_template ID, false = cookbook_ID
        """

        if id_num != None and id_type == True:
            api_uri="%s/cookbooks/%i/cookbook_attachments" % (self.config['apibase'], href)
            postdata = {'cookbook_attachment[server_template_href]': '%s/server_templates/%i' % (self.config['apibase'], id_num)}
        elif id_num != None and id_type == False:
            api_uri="%s/server_templates/%i/cookbook_attachments" % (self.config['apibase'], href)
            postdata = {'cookbook_attachment[cookbook_href]': '%s/cookbooks/%i' % (self.config['apibase'], id_num)}
        else:
            api_uri="%s/cookbook_attachments" % self.config['apibase']
            postdata = {'Thisisgonnaerrorbad': 'alpha'}
        return self.api.rs_post(api_uri, 201, postdata)

    def get_cookbooks(self):
        """Implements the index function of Cookbooks

        Gets every coookboon on the accont.  At once.  Oh god.
        """
        api_uri="%s/cookbooks" % self.config['apibase']
        return self.api.rs_get(api_uri)