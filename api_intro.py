from datetime import date
import requests

import config

# Client IDs and Secrets from config.py
ob_client_id = config.OB_CLIENT_ID
ob_client_Secret = config.OB_CLIENT_SECRET
sn_client_id = config.SN_CLIENT_ID
sn_client_Secret = config.SN_CLIENT_SECRET

# API base urls
svcnowUrl = "https://oregonstateuniversity-test.apigee.net/v1/servicenow/colleges"
onbaseUrl = "https://oregonstateuniversity-test.apigee.net/v2/onbase-docs/documents"
authUrl = "https://oregonstateuniversity-test.apigee.net/oauth2/token"

def get_access_token(key, secret):
    """
    Retrives an OSU API access token
    :param key: application client ID
    :param secret: applicationclient secret
    :returns: access token string
    """
    data = {"client_id": key, "client_secret": secret, "grant_type": "client_credentials"}
    request = requests.post(authUrl, data=data)
    response = request.json()

    return response["access_token"]

def get_svcnow_colleges(access_token):
    """
    Retrives Banner college data from ServiceNow API
    :param access_token: OSU API access token
    :returns: json college data
    """
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
    request = requests.get(svcnowUrl, headers=headers)
    response = request.json()
    return response["data"]

def get_onbase_documents(access_token):
    """
    Retrives Onbase documents from Onbase Documents API
    :param access_token: OSU API access token
    :returns: json ADMS Deny Document data
    """
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
    endDate = date.today()
    urlFilter = "?filter[documentTypeName]=ADMS Deny&filter[endDate]=" + str(endDate)
    request = requests.get(onbaseUrl + urlFilter, headers=headers)
    response = request.json()
    return response["data"]

def get_onbase_keywords(access_token, id):
    """
    Retrives keywords for a document from Onbase Documents API
    :param access_token: OSU API access token
    :param id: document ID
    :returns: json document keyword data
    """
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
    docUrl = "/" + str(id) + "/keywords"
    request = requests.get(onbaseUrl + docUrl, headers=headers)
    response = request.json()
    return response["data"]["attributes"]["keywords"]

if __name__ == "__main__":
    ob_access_token = get_access_token(ob_client_id, ob_client_Secret)
    sn_access_token = get_access_token(sn_client_id, sn_client_Secret)

    # API Call 1: Service Now API Retrieve Top 5 College Data
    print("API Call 1: Service Now API Retrieve College Data")
    collegeData = get_svcnow_colleges(sn_access_token)
    count = 1
    for college in collegeData:
        print(str(count) + "- College Code: " + college["attributes"]["code"] + ", College Name: " + college["attributes"]["description"])
        count += 1
        if count > 5:
            break
    
    # API Call 2: Get Onbase Documents
    print("API Call 2: Retrieve Onbase Documents")
    documentData = get_onbase_documents(ob_access_token)
    count = 1
    for document in documentData:
        print(str(count) + "- Doc ID: " + document["id"] + ", Doc Name: " + document["attributes"]["name"] + ", Created Date: " + document["attributes"]["storedDate"])
        keywords = get_onbase_keywords(ob_access_token, document["id"])
        for keyword in keywords:
            if keyword["name"] == 'ADMS - Application Term':
                print("-- Application Term: " + keyword["values"][0]["formattedValue"])
            if keyword["name"] == 'ADMS - App Number':
                print("-- Application Number: " + str(keyword["values"][0]["formattedValue"]))
        count += 1
        if count > 5:
            break