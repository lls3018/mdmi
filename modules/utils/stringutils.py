#! /usr/bin/python
# fileName: stringutils.py
# encoding=utf-8

import re

def single_quote_to_double(src):
    if src is None:
        return None
    else:
        src = src.replace("'", "\"")
        def replace_symbol(matched):
            str = matched.group("symbol")
            str = str.replace("\"", "'")
            return str
        rtnVal = re.sub(r"(?P<symbol>(?<=\"EnrollmentUserName\": \").*?(?=\",))", replace_symbol, src)
        rtnVal = re.sub(r"(?P<symbol>(?<=\"EnrollmentEmailAddress\": \").*?(?=\",))", replace_symbol, src)
        return rtnVal

def get_admin_name_from_dn(phrase):
    if not phrase:
        return phrase

    pos = phrase.find('(admin)')
    if pos > 0:
        phrase = phrase[:pos].strip()

        if phrase.startswith('cn'):
            phrase = phrase[2:].strip()
        if phrase.startswith('='):
            phrase = phrase[1:].strip()

        return phrase

    return phrase

