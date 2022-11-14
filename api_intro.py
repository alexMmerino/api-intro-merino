from datetime import date

import requests

import config

# Client IDs and Secrets from config.py
try:
    OB_CLIENT_ID = config.OB_CLIENT_ID
    OB_CLIENT_SECRET = config.OB_CLIENT_SECRET
    SN_CLIENT_ID = config.SN_CLIENT_ID
    SN_CLIENT_SECRET = config.SN_CLIENT_SECRET
    BASE_URL = config.BASE_URL
except AttributeError:
    raise Exception('Config file is missing configuration.')


# API urls
svcnow_url = BASE_URL + 'v1/servicenow/colleges'
onbase_url = BASE_URL + 'v2/onbase-docs/documents'
auth_url = BASE_URL + 'oauth2/token'


def get_access_token(key, secret):
    """
    Retrives an OSU API access token
    :param key: application client ID
    :param secret: applicationclient secret
    :returns: access token string
    """
    data = {'client_id': key, 'client_secret': secret,
            'grant_type': 'client_credentials'}
    request = requests.post(auth_url, data=data)
    response = request.json()
    if 'access_token' in response:
        return response['access_token']
    else:
        raise Exception('Unable to generate access token.')


def get_api_response(access_token, url):
    """
    Retrives data from OSU API
    :param access_token: OSU API access token
    :param url: OSU API endpoint url
    :returns: json data
    """
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {access_token}'}
    request = requests.get(url, headers=headers)
    response = request.json()
    if 'data' in response:
        return response['data']
    else:
        raise Exception(f'Error occured retreiving data from {url}')


if __name__ == '__main__':
    ob_access_token = get_access_token(OB_CLIENT_ID, OB_CLIENT_SECRET)
    sn_access_token = get_access_token(SN_CLIENT_ID, SN_CLIENT_SECRET)

    # API Call 1: Service Now API Retrieve Top 5 College Data
    print('API Call 1: Service Now API Retrieve College Data')
    college_data = get_api_response(sn_access_token, svcnow_url)
    for college in college_data[:5]:
        print(f"- College Code: {college['attributes']['code']}" +
              f", College Name: {college['attributes']['description']}")

    # API Call 2: Get Onbase Documents
    print('API Call 2: Retrieve Onbase Documents')
    end_date = str(date.today())
    url_filter = (f'?filter[documentTypeName]=ADMS Deny&filter[endDate]=' +
                  f'{end_date}')
    document_data = get_api_response(ob_access_token, onbase_url + url_filter)
    for document in document_data[:5]:
        print(f"- Doc ID: {document['id']}, Doc Name: " +
              f"{document['attributes']['name']}, Created Date: " +
              f"{document['attributes']['storedDate']}")
        doc_url = f"/{document['id']}/keywords"

        # API Call 3: Get Onbase Document Keywords
        keyword_data = get_api_response(ob_access_token, onbase_url + doc_url)
        keywords = keyword_data['attributes']['keywords']
        for keyword in keywords:
            if keyword['name'] == 'ADMS - Application Term':
                print('-- Application Term: ' +
                      f"{keyword['values'][0]['formattedValue']}")
            if keyword['name'] == 'ADMS - App Number':
                print('-- Application Number: ' +
                      f"{keyword['values'][0]['formattedValue']}")
