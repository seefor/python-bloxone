#!/usr/local/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''
------------------------------------------------------------------------

 Description:

 Module to provide class hierachy to simplify access to the BloxOne APIs

 Date Last Updated: 20210215

 Todo:

 Copyright (c) 2021 Chris Marrison / Infoblox

 Redistribution and use in source and binary forms,
 with or without modification, are permitted provided
 that the following conditions are met:

 1. Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright
 notice, this list of conditions and the following disclaimer in the
 documentation and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------
'''
import bloxone
import logging
import requests
import json

# ** Global Vars **
__version__ = '0.1.0'
__author__ = 'Chris Marrison'
__email__ = 'chris@infoblox.com'
__doc__ = 'https://python-bloxone.readthedocs.io/en/latest/'
__license__ = 'BSD'


class b1oph(bloxone.b1):
    '''
    Class to simplify access to the BloxOne Platform APIs
    '''

    def get(self, objpath, id="", action="", **params):
        '''
        Generic get object wrapper for platform calls

        Parameters:
            objpath (str):  Swagger object path
            id (str):       Optional Object ID
            action (str):   Optional object action, e.g. "nextavailableip"

        Returns:
            response object: Requests response object
        '''

        # Build url
        url = self.host_url + objpath
        url = self._use_obj_id(url,id=id)
        url = self._add_params(url, **params)
        logging.debug("URL: {}".format(url))

        response = self._apiget(url)

        return response

        
    def create(self, objpath, body=""):
        '''
        Generic create object wrapper for platform objects

        Parameters:
            objpath (str):  Swagger object path
            body (str):     JSON formatted data payload

        Returns:
            response object: Requests response object
        '''
        # Build url
        url = self.host_url + objpath
        logging.debug("URL: {}".format(url))

        # Make API Call
        response = self._apipost(url, body)

        return response


    def delete(self, objpath, id=""):
        '''
        Generic delete object wrapper for platform objects

        Parameters:
            objpath (str):  Swagger object path
            id (str):       Object id to delete

        Returns:
            response object: Requests response object
        '''
        # Build url
        url = self.host_url + objpath
        url = self._use_obj_id(url, id=id)
        logging.debug("URL: {}".format(url))

        # Make API Call
        response = self._apidelete(url)

        return response


    def update(self, objpath, id="", body=""):
        '''
        Generic create object wrapper for ddi objects

        Parameters:
            objpath (str):  Swagger object path
            body (str):     JSON formatted data payload

        Returns:
            response object: Requests response object
        '''
        # Build url
        url = self.host_url + objpath
        url = self._use_obj_id(url, id=id)
        logging.debug("URL: {}".format(url))

        # Make API Call
        response = self._apiput(url, body)

        return response


    def get_tags(self, objpath, id=""):
        '''
        Get tags for an object id

        Parameters:
            objpath (str):  Swagger object path

            id (str): id of object

        Returns:
            tags (dict): Dictionary of current tags
                         or empty dict if none
        
        .. todo::
            * make generic, however, this requires the below
            * Lookup dictionary of 'required fields' per object type
        '''
        tags = {}
        response = self.get(objpath, id=id, _fields="tags")
        if response.status_code in self.return_codes_ok:
            tags = json.loads(response.text)
            tags = tags['result']
        else:
            tags = {}
        
        return tags


    # *** Platform API Requests *** 

    def on_prem_hosts(self, **params):
        '''
        Method to retrieve On Prem Hosts
        (undocumented)

        Parameters:
            **params (dict): Generic API parameters

        Returns:
            response object: Requests response object
        '''

        # Call BloxOne API
        response = self.get('/on_prem_hosts', **params)

        # Return response object
        return response 


    def get_id(self, objpath, *, key="", value="", include_path=False):
        '''
        Get object id using key/value pair

        Parameters:
            objpath (str):  Swagger object path
            key (str):      name of key to match
            value (str):    value to match
            include_path (bool): Include path to object id

        Returns:
            id (str):   object id or ""
        '''

        # Local Variables
        id = ""
        filter = key+'=="'+value+'"'
        fields = key + ',id'

        # Make API Call
        response = self.get(objpath, _filter=filter, _fields=fields)

        # Process response
        if response.status_code in self.return_codes_ok:
            obj = response.json()
            # Look for results
            if "results" in obj.keys():
                obj = obj['results']
                if obj:
                    id = obj[0]['id']
                    if not include_path:
                        id = id.rsplit('/',1)[1]
                else:
                    logging.debug("Key {} with value {} not found."
                                  .format(key,value))
            else:
                id = ""
                logging.debug("No results found.")
        else:
            id=""
            logging.debug("HTTP Error occured. {}".format(response.status_code))

        logging.debug("id: {}".format(id)) 

        return id


    def oph_add_tag(self, id="", tagname="", tagvalue=""):
        '''
        Method to add a tag to an existing On Prem Host

        Parameters:
            objpath (str):  Swagger object path
            tagname (str): Name of tag to add
            tagvalue (str): Value to associate

        Returns:
            response object: Requests response object
        '''
        # tags = self.get_tags('/on_prem_hosts', id=id)
        response = self.get('/on_prem_hosts', id=id, _fields="display_name,tags")
        if response.status_code in self.return_codes_ok:
            data = response.json()['result']
        else:
            data = {}
        logging.debug("Existing tags: {}".format(data))
        # Add new tag to data
        if tagname:
            data['tags'].update({tagname: tagvalue})
            logging.debug("New tags: {}".format(data))
        # Update object
        response = self.update('/on_prem_hosts', id=id, body=json.dumps(data))

        return response


    def oph_delete_tag(self, id="", tagname=""):
        '''
        Method to delete a tag from an existing On Prem Host

        Parameters:
            objpath (str):  Swagger object path
            tagname (str): Name of tag to add

        Returns:
            response object: Requests response object
        '''
        # tags = self.get_tags('/on_prem_hosts', id=id)
        response = self.get('/on_prem_hosts', id=id, _fields="display_name,tags")
        if response.status_code in self.return_codes_ok:
            data = response.json()['result']
            logging.debug("Existing tags: {}".format(data))
            # Delete tag from data
            if tagname in data['tags'].keys():
                data['tags'].pop(tagname, True)
                print(json.dumps(data))
                logging.debug("New tags: {}".format(data))
                # Update object
                response = self.update('/on_prem_hosts', id=id, body=json.dumps(data))

        return response


    def auditlog(self, **params):
        '''
        Get the audit log

        Parameters:
            **params (dict): Generic API parameters
        Returns:
            audit_log (list); list of dict
        '''
        # Local variables
        audit_log = []

        url = self.base_url + '/api/auditlog/' + self.api_version +'/logs'
        url = self._add_params(url, **params)

        logging.debug("URL: {}".format(url))

        # Call API
        response = self._apiget(url)

        if response.status_code in self.return_codes_ok:
            if 'results' in response.json().keys():
                audit_log = response.json()['results']
        else:
            audit_log = response.json()
        
        return audit_log


    def get_full_auditlog(self, **params):
        '''
        '''
        all_logs = []
        offset = 0
        limit = 1000

        audit_log = self.auditlog(_offset=str(offset), 
                                  _limit=str(limit), **params)
        while isinstance(audit_log, list) and len(audit_log):
            all_logs += audit_log
            offset += limit + 1
            audit_log = self.auditlog(_offset=str(offset), 
                                      _limit=str(limit), **params)

        return all_logs

