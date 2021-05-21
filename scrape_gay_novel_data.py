import time
import sys
import json
import requests
import datetime
import urllib

import wikipedia as wp
import wikidata.datavalue
from wikidata.client import Client

wd_client = Client()

WD_PROP_DATA = [
        dict(name='author', id=50),
        dict(name='publisher', id=123),
        dict(name='country of origin', id=495),
        dict(name='language', id=407),
        dict(name='publication date', id=577),
        dict(name='title', id=1476),
        dict(name='genre', id=136, multi=True),
]

WD_PROPS = {
        propdat['name']
        :
        wd_client.get(f'P{propdat["id"]}')
        for propdat in WD_PROP_DATA
}

def pages_in_category(cat_name, limit=1000, deep=False):
    pre = 'Category:'
    if cat_name.startswith(pre):
        cat_name = cat_name[len(pre):]
    kw = 'deepcat' if deep else 'incategory' 
    query = f'{kw}:"{cat_name}"'
    res = wp.search(query, results=limit)
    if len(res) >= limit:
        print(f"WARNING: Reached limit of {limit}")
    return res

# unfortunately wp wrapper doesn't give this info
def get_wikidata_id_for_pagename(pagename):
    encoded_title = urllib.parse.quote(pagename)
    url = 'https://www.wikidata.org/wiki/Special:ItemByTitle?site=enwiki&page=' + encoded_title
    resp = requests.get(url)
    dest = resp.url
    assert dest.startswith('https://www.wikidata.org/wiki/'), dest
    assert 'Special:ItemByTitle' not in dest, dest
    qid = dest.split('/')[-1]
    return qid

def get_book_entity(pagename):
    qid = get_wikidata_id_for_pagename(pagename)
    entity = wd_client.get(qid, load=True)
    return entity

def parse_prop_value(value):
    # MonolingualText object
    if hasattr(value, 'locale'):
        return str(value)
    # MultilingualText
    if hasattr(value, 'texts'):
        return value.get('en')
    if isinstance(value, (int, str)):
        return value
    if isinstance(value, datetime.date):
        return value.year
    if hasattr(value, 'label'):
        # recurse
        return parse_prop_value(value.label)
    assert False, f"Can't handle value {value}"

def parse_year_from_attr(entity, prop):
    """Used as a fallback in case of exception...
    "wikidata.datavalue.DatavalueError: time precision other than 9, 11 or 14 is unsupported"
    (i.e. wikidat wrapper can't parse dates with year+month precision)
    """
    datlist = entity.attributes['claims'][prop.id]
    # If there's more than one pub date, then return the earliest
    years = []
    #assert len(datlist) == 1
    for dat in datlist:
        datestr = dat['mainsnak']['datavalue']['value']['time']
        assert datestr[0] == '+'
        yearstr = datestr[1:5]
        year = int(yearstr)
        years.append(year)
    return min(years)

def get_book_data(pagename):
    entity = get_book_entity(pagename)
    res = {}
    for propdat in WD_PROP_DATA:
        propname = propdat['name']
        prop = WD_PROPS[propname]
        multi = propdat.get('multi', False)
        if multi:
            res[propname] = [parse_prop_value(v) for v in entity.getlist(prop)]
            continue
        try:
            value = entity[prop]
        except KeyError:
            res[propname] = None
            continue
        # Can't handle dates like 'September 1992' ("time precision other than 9, 11 or 14 is unsupported")
        except wikidata.datavalue.DatavalueError:
            res[propname] = parse_year_from_attr(entity, prop)
            continue
        res[propname] = parse_prop_value(value)
    res['wiki_title'] = pagename
    res['en_label'] = entity.label.get('en')
    return res

def main(limit=None):
    cands = pages_in_category("Novels with gay themes", limit, deep=True)
    dat = []
    for cand in cands:
        try:
            dat.append(get_book_data(cand))
        except Exception as e:
            print(f"Issue getting data for page {cand}")
            raise e
        if len(dat) % 10 == 0:
            sys.stderr.write(f"{len(dat)}... ")
    dat.sort(key=lambda item: item['publication date'] or 0)
    with open('noveldat.json', 'w') as f:
        json.dump(dat, f, indent=2)


if __name__ == '__main__':
    test = 0 or len(sys.argv) > 1
    if not test:
        t0 = time.time()
        main(limit=500)
        print(f"Finished in {time.time()-t0}s")
    else:
        try:
            title = sys.argv[1]
        except IndexError:
            title = 'The Secret History'
        e = get_book_entity(title)
        bdat = get_book_data(title)
        print(bdat)
