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
    def __init__(self, api_type="dev"):
        self.headers = {'X-API-Version': '1.5'}
        with open('config.json','r') as f:
            self.config = json.loads(f.read())
        self.rs_login(api_type)


    def rs_login(self, api_type="dev"):
        payload = {'refresh_token' : self.config['logins'][api_type], 'grant_type': 'refresh_token'}
        r = requests.post("%s/oauth2" % self.config['apibase'], data=payload, headers=self.headers)
        if self.rs_error_check(r, 200) == False:
            sys.exit(0)
        jsondata = json.loads(r.text)
        self.headers['Authorization'] = "Bearer %s" % jsondata['access_token']

    def rs_array_generator(self, data, param):
        retVal = {}
        for i in data:
            retVal[param+"[]"] = data
        return retVal

    def rs_hash_generator(self, data, param):
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

    def rs_get(self, api_uri, resp_id=200):
        r = requests.get(api_uri, headers=self.headers)
        val = self.rs_error_check(r, resp_id)
        if val == "":
            return val
        return json.loads(val)

    def rs_post(self, api_uri, resp_id=200, payload = None):
        if payload == None:
            r = requests.post(api_uri, headers=self.headers)
        else:
            r = requests.post(api_uri, headers=self.headers, data=payload)
        val = self.rs_error_check(r, resp_id)
        if val == "" or val == None:
            return val
        return json.loads(val)

    def rs_error_check(self, r, resp_id):
        if r.status_code == resp_id:
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
