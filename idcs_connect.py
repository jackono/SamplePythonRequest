import requests
import shutil
import os
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def __init__():
    global URL
    global auth_token

    # open config file to retrieve needed settings
    with open('config.json', 'r') as f:
        conf = json.load(f)
    URL = conf['BaseUrl']

    # pass client id and secret as parameter to get auth token
    auth_token = getAuth(conf['ClientId'], conf['ClientSecret'])

    # Test Data
    bulkFile = 'bulk_patch.json'

    reqPath = './Request/'
    archPath = './Archive/'
    
    # process multiple json files
    for filename in os.listdir(reqPath):
        if filename.endswith(".json"):
            bulkFile = reqPath + filename
            
            parseFile(bulkFile)
            # move processed file in archive folder
            shutil.move(bulkFile, archPath)

    print('All files were successfully loaded.')


def getAuth(clientId, clientSecret): 

    data = {
    'grant_type': 'client_credentials',
    'scope': 'urn:opc:idm:__myscopes__'
    }

    # Request for auth token
    response = requests.post(URL + '/oauth2/v1/token', data=data, verify=False, auth=(clientId, clientSecret))

    # Parses response into JSON format
    res = response.json()
    
    # Parse access token
    auth_token = res['access_token']

    return auth_token

def getId(userName, path):
    headers = {
    'Authorization': 'Bearer ' + auth_token,
    }
    if path == '/Groups':
        params = (
        ('attributes', 'members'),
        ('filter','displayName eq "' + userName + '"'),
        )
    else:
        params = (
        ('attributes', userName),
        ('filter','userName sw "' + userName + '"'),
        )
    response = requests.get(URL + '/admin/v1' + path, headers=headers, params=params, verify=False)

    res = response.json()
    
    # Error handling
    # print(res)
    # print(response.status_code)
    if response.status_code == 200:
        return res['Resources'][0]['id']
    else:
        print(json.dumps(response.json(), indent=2))

def parseFile(bulkFile):

    with open(bulkFile, "r+") as contents:

    # Convert file contents into JSON format
        data = json.loads(contents.read())

        for bulkData in data['Operations']:
            if(bulkData['method'] != 'POST'):
                path = bulkData['path'].rsplit('/', 1)[0]
                operation = bulkData['data']['Operations']
                userId = getId(bulkData['path'].rsplit('/', 1)[-1] ,path)
                bulkData['path'] = path + '/' + userId
                for op in operation:
                    if op['op'] == 'add' or op['op'] == 'remove':
                        groupUserId = op['value'][0]['value']
                        op['value'][0]['value'] = getId(groupUserId ,'/Users')

        dataString = json.dumps(data)
        contents.seek(0)
        contents.write(dataString)
        contents.truncate()
        contents.close()
    
    bulkReq(bulkFile)

def bulkReq(bulkFile):
    headers = {
    'Content-Type': 'application/scim+json',
    'Authorization': 'Bearer '+ auth_token,
    }

    contents = open(bulkFile, "r")
    dataString = json.dumps(contents.read())
    data = json.loads(dataString)

    response = requests.post(URL + '/admin/v1/Bulk', headers=headers, data=data, verify=False)

    if response.status_code == 201:
        print(bulkFile + ' has been successfully imported.')
        print(json.dumps(response.json(), indent=2))
    else:
        print('An error has occured\n')
        print(json.dumps(response.json(), indent=2))

__init__()