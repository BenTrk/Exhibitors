from py_crunchbase import PyCrunchbase, CrunchbaseAPIException
import os
import json
import time

# Setting up pycrunchbase and using the API key
os.environ['PY_CRUNCHBASE_API_KEY'] = '6999e6534ffe557ff57f6fda4ff2ae8a'
pycb = PyCrunchbase()

def cb_search_main(company):
    print("Getting the uuid...")
    try:
        search_what = cb_search_for_uuid(company)
    except CrunchbaseAPIException:
        print("Not free...")
        time.sleep(61)
        search_what = cb_search_for_uuid(company)
    for uuid in search_what:
        print("The uuid is " + uuid)
        try:
            cb_search_for_data(uuid)
        except CrunchbaseAPIException:
            print("Not free...")
            time.sleep(61)
            cb_search_for_data(uuid)

# Getting the uuid for the company
def cb_search_for_uuid(company):
    api = pycb.autocomplete_api()
    uuids = []
    try:
        for entity in api.autocomplete(company).limit(3).execute():
            uuids.append(entity.uuid)
        return uuids
    except CrunchbaseAPIException:
        print("Not free...")
        time.sleep(61)
        for entity in api.autocomplete(company).limit(3).execute():
            uuids.append(entity.uuid)
        return uuids

# Getting data based on uuid    
def cb_search_for_data(uuid):
    api = pycb.search_organizations_api()
    api.select(
        'identifier', 'location_identifiers', 'short_description', 'rank_org', 'created_at', 'facebook', 'linkedin', 'website_url'
    ).where(
        uuid__eq=[uuid]
    )
    for company in api.iterate():
        for item in company:
            with open('companies_data', 'a') as f:
                item_json = json.dumps(item)
                f.write(item_json)
                f.write("\r\n")
