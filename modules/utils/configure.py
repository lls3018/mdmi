#!/usr/bin/python
#-*- coding: utf-8 -*-

import ConfigParser
import json
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

'''
    Default configure file, and sections
    Supports json and ini format
'''
MDMI_CONFIG_FILE = '/opt/mdmi/etc/mdmi.conf'
MDMI_USERCFG_FILE = '/etc/sysconfig/mes.json'     #value would be changed when special section found
SERVICECONFIG_FILE = '/etc/sysconfig/serviceconfig.json'

#special section name
HDB_ADMININFO_SECTION_NAME = 'MesJsonPath'

class _JsonConfigParser(object):
    '''
    class _JsonConfigParser
        This class implements read configure file formatted as json.

    Attributes:
        m_context : Load the settings to avoid repeat read.
    '''
    def __init__(self, cfgfilepath):
        self.m_context = None
        cfgfile = None
        try:
            cfgfile = open(cfgfilepath, 'r')
        except Exception as e:
            err = 'Open configure file error! %s' % repr(e)
            logger.error(err)
            raise Exception(err)
        else:
            self.m_context = json.load(cfgfile)
        finally:
            if cfgfile:
                cfgfile.close()
                cfgfile = None
        pass

    def get_settings(self, section, keys):
        '''
        Read configure settings

        Params:
            section : same as key
            keys : key names.

        Return:
            A dict.
        '''
        ret_dict = {}
        if section:
            ret_dict[section] = self.m_context.get(section)
            if keys:
                for key in keys:
                    ret_dict[key] = self.m_context.get(key)
        else:
            ret_dict = dict(self.m_context)
        return ret_dict
        pass
    pass
#end of class _JsonConfigParser


class _IniConfigParser(ConfigParser.RawConfigParser):
    '''
    class _IniConfigParser
        This class implements read configure file formatted as INI.
    '''
    def get_settings(self, section=None, items=None):
        '''
        Read configure settings

        Params:
            section : Name of the section.

        Return:
            1> An empty list if section not exists.
            2> A list as [(item, value), ...] if item equal None and section exists.
            3> A list as [(section, (item, value), ...), ...] if section not exists and item equal None.
            4> Value of item in the section.
        '''
        ret_list = []
        if section:
            try:
                tmp_list = self.items(section)
            except ConfigParser.NoSectionError, e:
                logger.error(repr(e))
                return ret_list
            if items:
                #convert every item into lower at first
                tmp_items = [ item.lower() for item in items]
                for item in tmp_list:
                    if item[0] in tmp_items:
                        ret_list.append(item)
            else: #items empty
                ret_list = tmp_list
            pass
        else:
            #read all sections and items
            section_list = self.sections()
            for sect in section_list:
                sect_items = self.items(sect)
                sect_tuple = (sect, sect_items)
                ret_list.append(sect_tuple)

        return ret_list
        pass


class MDMiConfigParser(object):
    '''
    class MDMiConfigParser
        This class implements read configure information.
    
    Attributes:
        m_parser : Configer parser.
    '''
    def __init__(self, cfgfile, isjson=False):
        '''
        The constructor.

        Params:
            cfgfile : Path of the configure file.
            isjson : Format of the configure file. It is json when isjson is ture, otherwise it is ini.
        '''
        self.m_parser = None
        self.m_parser = self._get_parser(cfgfile, isjson)
        pass

    def __del__(self):
        del self.m_parser
        self.m_parser = None
        pass

    def read(self, section=None, *items):
        '''
        Get detail information
        
        Params:
            section : Name of the section, key name for json
            items : Items in the section, same as section for json.

        Returns:
            An configure value dict or list.
        '''
        if not self.m_parser:
            raise Exception('Configure file can NOT be opened!')
        #poly fucntion call.
        return self.m_parser.get_settings(section, items)
        pass

    def reset(self, cfgfile, isjson=False):
        '''
        Read new configure file

        Params:
            cfgfile : Path of the configure file.
            isjson : Format of the configure file. It is json when isjson is ture, otherwise it is ini.
        '''
        if self.m_parser: #reset at first
            del self.m_parser
            self.m_parser = None
        self.m_parser = self._get_parser(cfgfile, isjson)
        pass

    def _get_parser(self, cfgfile, isjson=False):
        parser = None
        if isjson:
            parser = _JsonConfigParser(cfgfile)
        else:
            parser = _IniConfigParser()
            parser.read(cfgfile)
        return parser
        pass

#end of Class MDMiConfigParser


