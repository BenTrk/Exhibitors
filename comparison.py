import re
import json

def get_companies_from_companies():
    # Get a list of companies from the companies JSON file
    companies_list = []
    with open('companies') as c:
        lines = c.readlines()
        for line in lines:
            if line.strip() == "":
                continue
            else:
                data = json.loads(line)
                company_from_companies = company(data['company_name'], data['company_country'], data['company_stand'], data['company_desc'])
                companies_list.append(company_from_companies)
    return companies_list

def compare():
    # Get the list from get_companies_from_companies
    companies_list = get_companies_from_companies()
    # Iterate through
    for company in companies_list:
        # Get the company at hand, strip from things in brackets and Gmbh
        company_name = company.name
        company_name = re.sub(r'\([^)]*\)', '', company_name).strip()
        company_name = re.sub(r'\b(?:GmbH|AG)\b', '', company_name, flags=re.IGNORECASE).strip()
        print(company_name)

        # Go through the list in companies_data to check for company name
        data = compare_with_companies_data(company_name)
        # Check if there was a match
        if data == 'No match':
            is_match = False
        else:
            is_match = True
        
        # If match, save
        if is_match:
            # Save mechanism
            # Get the data, put it together with conference information
            # use a POJO object to get all fields and easy translation to JSON
            company.created_at = data['created_at']
            try:
                for location in data['location_identifiers']:
                    company.locations.append(location['value'])
                linkedin = data.get('linkedin', {}).get('value')
                company.social.append({'linedin': linkedin})
                facebook = data.get('facebook', {}).get('value')
                company.social.append({'facebook': facebook})
                website_url = data.get('website_url')
                company.social.append({'website_url': website_url})
            except:
                print('Some data was missing.')
        # If no match, check partial matches
        else:
            compare_partial_with_companies_data()
        
    # Do something with the enriched companies list, like save it to a JSON as enriched_companies
    company_dicts = []
    for company_enriched in companies_list:
        company_dict = company_enriched.to_dict()
        company_dicts.append(company_dict)
    with open('companies_enriched', 'a') as json_file:
        json.dump(company_dicts, json_file, indent=4)            

def compare_with_companies_data(company_name):
    with open('companies_data') as cd:
        lines = cd.readlines()
        for line in lines:
            if line.strip() == "":
                continue
            else:
                data = json.loads(line)
                company = data['identifier']['value']
                if company == company_name:
                    return data
        return 'No match'

def compare_partial_with_companies_data():
    #Currently, it's a dummy function. Write it if necessary.
    return True

class company():
    # All data that is needed... in locations save the locations, in social, save linkedin, facebook, and website
    def __init__(self, name, country, stand, desc, created_at=None, locations=None, social=None):
        if locations == None:
            locations = []
        self.locations = locations
        if social == None:
            social = []
        self.social = social
        if created_at == None:
            created_at = '1900-01-01T01:01:01Z'
        self.created_at = created_at
        self.name = name
        self.country = country
        self.stand = stand
        self.desc = desc
        self.created_at = created_at
    
    def to_dict(self):
        return {
            "name": self.name,
            "country": self.country,
            "stand": self.stand,
            "desc": self.desc,
            "created_at": self.created_at,
            "locations": self.locations,
            "social": self.social
        }