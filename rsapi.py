#!/usr/bin/python

import requests
import simplejson as json
import sys
import re
from threading import Timer

rs_errors = {301: "API Moved, check response", 400: "Missing paramater",
401: "Bad login/instance token", 403: "Not enough roles to execute",
404: "Unknown/bad route.  Check your URI", 405: "Bad method, make sure you're not derpin",
406: "Generic error.  Derp", 422: "Multiple possible errors, look at the response",
500: "Oooooh.  Rightscale derped!  Ping RS with everything ya got"}

class rsapi:
    """Class for interfacing with RS + RS Support functions

    This exists for error handling, as well as generating the weird ways that RS handles it's hashes/arrays
    """
    def __init__(self, api_type="dev", debug_mode=False):
        """Init the class

        Can have debug mode turned on, sets API type, also sets the base headers because RS requires it in a header.
        Also inits the login to rightscale, for good measure.

        KwArgs:
            api_type (str): Needed to map to the login stored in the config.json
            debug_mode (bool): Turns on/off debug mode.
        """
        self.headers = {'X-API-Version': '1.5'}
        with open('config.json','r') as f:
            self.config = json.loads(f.read())
        self.rs_login(api_type)
        self.debug = debug_mode

    def rs_login(self, api_type="dev"):
        """Logs in to rightscale, sets the Bearer token

        Performs all login functions, only function that does raw POST requests without running through rs_post

        KwArgs:
            api_type (str): Needed to map to the login stored in the config.json
        """
        payload = {'refresh_token' : self.config['logins'][api_type], 'grant_type': 'refresh_token'}
        r = requests.post("%s/oauth2" % self.config['apibase'], data=payload, headers=self.headers)
        if self.rs_error_check(r, 200) == False:
            sys.exit(0)
        jsondata = json.loads(r.text)
        self.headers['Authorization'] = "Bearer %s" % jsondata['access_token']

    def rs_array_generator(self, data, param):
        """Generates arrays for POST data from lists

        Due to the way Rightscale handles "arrays" in post requests, this is required to turn a list into an "array"

        Args:
            data (list): List of values to be added to the "array"
            param (str): Name of the array value

        Example: rs_array_generator(['alpha', 'beta', 'gamma'], "zeta")

        Returns:
            dict.   example::
                {'zeta[]': 'alpha', 'zeta[]': 'beta', 'zeta[]': 'gamma'}

        This is ready to be pushed directly into a POST request as a param

        """
        retVal = {}
        for i in data:
            retVal[param+"[]"] = i
        return retVal

    def rs_hash_generator(self, data, param):
        """Generates hashes for POST data from dicts

        Due to the way Rightscale handles "hashes" in dict requests, this is required to turn a list into an "hashes"

        Args:
            data (dict): List of values to be added to the "array"
            param (str): Name of the array value

        Example: rs_hash_generator({'oranges':'orange', 'banana': 'yellow', 'logins': {'name':'data', 'pass':'data2'}}, "zeta")

        Returns:
            dict.   example::
                {'zeta[oranges]': 'orange', 'zeta[banana]': 'yellow', 'zeta[logins][name]': 'data', 'zeta[logins][pass]': 'data2'}

        This is ready to be pushed directly into a POST request as a param.  THIS IS A RECURSIVE FUNCTION.  USER BEWARE.

        """
        retval = {}
        for k,v in data.iteritems():
            if type(v) is dict:
                intval = rs_hash_generator(v, param)
                for a,c in intval.iteritems():
                    m = re.search('\[([a-zA-Z0-9]*)\]', a)
                    retval[param+"["+k+"][" + m.group(1) + "]"] = c
            else:
                retval[param+"["+k+"]"] = v
        return retval

    def rs_get(self, api_uri, resp_id=200, payload = None):
        """Performs a GET request to the RS API

        Basic, bog-standard authenticated GET request

        Args:
            api_uri (string): API call to be made, full URI.
            resp_id (int): Expected result from the API.  Flags an exception if not valid.
            payload (dict): Payload to be sent, can be null

        returns:
            string or dict: Varies depending on the result of the API.
        """
        if self.debug == True:
            print "GET: API_URI: %s\nHeaders: %s\nData: %s\n" % (api_uri, self.headers, payload)
        if payload == None:
            r = requests.get(api_uri, headers=self.headers)
        else:
            r = requests.get(api_uri, headers=self.headers, params=payload)
        return self.rs_error_check(r, resp_id)

    def rs_post(self, api_uri, resp_id=200, payload = None):
        """Performs a POST request to the RS API

        Basic, bog-standard authenticated POST request

        Args:
            api_uri (string): API call to be made, full URI.
            resp_id (int): Expected result from the API.  Flags an exception if not valid.
            payload (dict): Payload to be sent, can be null

        returns:
            string or dict: Varies depending on the result of the API.
        """
        if self.debug == True:
            print "POST: API_URI: %s\nHeaders: %s\nData: %s\n" % (api_uri, self.headers, payload)
        if payload == None:
            r = requests.post(api_uri, headers=self.headers)
        else:
            r = requests.post(api_uri, headers=self.headers, data=payload)
        return self.rs_error_check(r, resp_id)

    def rs_put(self, api_uri, resp_id=200, payload = None):
        """Performs a PUT request to the RS API

        Basic, bog-standard authenticated PUT request

        Args:
            api_uri (string): API call to be made, full URI.
            resp_id (int): Expected result from the API.  Flags an exception if not valid.
            payload (dict): Payload to be sent, can be null

        returns:
            string or dict: Varies depending on the result of the API.
        """
        if self.debug == True:
            print "PUT: API_URI: %s\nHeaders: %s\nData: %s\n" % (api_uri, self.headers, payload)
        if payload == None:
            r = requests.put(api_uri, headers=self.headers)
        else:
            r = requests.put(api_uri, headers=self.headers, data=payload)
        return self.rs_error_check(r, resp_id)

    def rs_delete(self, api_uri, resp_id=200, want_to=False):
        """Performs a DELETE request to the RS API

        Basic, bog-standard authenticated DELETE request

        Args:
            api_uri (string): API call to be made, full URI.
            resp_id (int): Expected result from the API.  Flags an exception if not valid.
            want_to (bool): Needs to be set True to run

        returns:
            string or dict: Varies depending on the result of the API.

        There's a whole lot of no validation in this in RS.  Be careful por favour!
        """
        if want_to == False:
            return False
        if self.debug == True:
            print "Delete: API_URI: %s\nHeaders: %s\n" % (api_uri, self.headers)
        r = requests.delete(api_uri, headers=self.headers)
        return self.rs_error_check(r, resp_id)


    def rs_error_check(self, r, resp_id):
        """Provides validation after a request to the RS API

        Verifies if the response value is correct

        Args:
            r (response object): Response object from post/get/put/etc.
            resp_id (int): Expected result from the API.
        returns:
            string or None: String if the result is valid, None if we flag an exception
        """
        if r.status_code == resp_id:
            try:
                return json.loads(r.text)
            except:
                return r.text
        else:
            try:
                if r.status_code not in rs_errors:
                    raise rsapi_exception("API Call %s failed with %d error code.\nResponse body is: %s" % (r.url, r.status_code, r.text))
                else:
                    raise rsapi_exception("API Call %s failed with %d error code and RS Error: %s.\nResponse body is: %s" % (r.url, r.status_code, rs_errors[r.status_code], r.text))
            except rsapi_exception, e:
                print "Exception! " + e.value
                return None

class rsapi_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
