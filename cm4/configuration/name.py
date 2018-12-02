# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 12:44:44 2018

@author: Wu
"""
import re
from cm4.configuration.counter import Counter

class Name(object):
    def __init__(self, ntype=None, schema=None, name_dict=None):
        self.ntype = ntype
        self.name_dict = None
        self.default_schema_dict={
                "instance":"{experiment}-{group}-{user}-{counter}"
                } 
        self.schema = None
        self.schema = self._get_schema(ntype, schema, False)
                
    def _get_schema(self, ntype, schema, throw=True):
            """
            find naming schema according to avalaible info
            if can not found any, throw a execption if `thorw`=True, else return None
            
            """
            if schema:
                return schema
            elif self.schema:
                return self.schema
            elif not schema and ntype in self.default_schema_dict:
                return self.default_schema_dict[ntype]
            else:
                if throw:
                    raise ValueError("Default naimg schema for {} don't exist. Please call set_schema() first!".format(ntype))
                else:
                    return None    
                
    def _impute_count(self, kwargs):
        def _incr(kwargs):
            if not self.name_dict:
                return Counter().get(user=kwargs['user'])
            else:
                return self.name_dict['counter']+1
                           
        if not kwargs and not self.name_dict:
            raise ValueError('No previous name assignment available, cannot generate unique name by incremental.')
            
        elif not kwargs and self.name_dict:
            self.name_dict['counter']=_incr(kwargs)
            kwargs = self.name_dict                  
            
        elif kwargs and 'counter' not in kwargs:
            kwargs.update({'counter':_incr(kwargs)})                                        
                        
        return kwargs
                
    def set_schema(self, ntype=None, schema=None):        
        """
        set naming schema for certain type of resource
        
        :param ntype: the type of resource being named
        :param schema: naming schema
        :return:
        """             
        self.schema = self._get_schema(ntype, schema)
        
    def verify(self, kwargs, ntype=None, schema=None):  
        """
        verify if the info contains in `kwargs` can produce a valid name for `ntype` object
        
        :param ntype: the type of resource being named
        :param schema: naming schema        
        """
        schema = self._get_schema(ntype, schema)
        schema_var= re.findall('\{(.+?)\}', schema)
        violate=[x for x in schema_var if x not in list(kwargs.keys()) and x!='counter']
        if violate:
            raise ValueError('Required information lack in `kwargs`: {}'.format(','.join(violate)))
                
    def get(self, kwargs=None, ntype=None, schema=None):
       
        schema = self._get_schema(ntype, schema)
        kwargs = self._impute_count(kwargs)
        self.verify(kwargs, schema=schema) # check kwargs        
        self.name_dict = kwargs # save current format
        return schema.format(**kwargs)       
    
        
#%% usage/test
#a={'experiment':'a','group':'b','user':'kimball', 'counter':0}
#namer=Name()                
#namer.set_schema('instance')
#print(namer.get(a))
#print(namer.get())
