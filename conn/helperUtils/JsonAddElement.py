#!/usr/bin/python

"""
developer skype: alec_host
"""
import ast
import json

class JsonElementManager():

    def _append_nth_element(self,json_string,new_element):

        element_to_append = {"SMS": new_element}

        store = json.loads((json_string))
    
        store["DATA"].append(element_to_append)
    
        return json.dumps(json.loads(json.dumps(store)))

    def _append_1st_element(self,new_element):

        store = ({"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Available notification[s]","DATA": [{"SMS": new_element}]})

        return json.dumps(json.loads(json.dumps(store)))

