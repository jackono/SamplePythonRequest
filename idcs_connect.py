import requests
import json

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
    userName = 'Alice'
    createFile = 'file1.json'
    updateFile = 'update1.json'
    bulkFile = 'bulk.json'
    
    # Comment out the function you want to test

    # createUser(createFile)
    # print(getUserId(userName))
    # updateUser(userName, updateFile)
    # deleteUser(userName)
    bulkReq(bulkFile)

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

def createUser(createFile):

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth_token,
    }

    contents = open(createFile, "r")

    # Convert file contents into JSON format
    dataString = json.dumps(contents.read())
    data = json.loads(dataString)

    response = requests.post(URL + '/admin/v1/Users', headers=headers, data=data, verify=False)

    # Error handling
    if response.status_code == 201:
        print(response.json()['userName'] + ' has been created')
    else:
        print('An error has occured\n')
        print(response.json())


def getUserId(userName):
    headers = {
    'Authorization': 'Bearer ' + auth_token,
    }
    response = requests.get(URL + '/admin/v1/Users', headers=headers, verify=False)

    res = response.json()
    
    print(res)
    print(response.status_code)
    # Error handling
    if response.status_code == 200:
        for userId in res['Resources']:
            print(userId['userName']) #//Comment out to print()all users
            if userId['userName'] == userName:
                print('ID for ' + userName + ' retrieved ' + userId['id'])
                return userId['id']
    else:
        print(response.json())

def updateUser(userName, updateFile):

    userId = getUserId(userName)

    headers = {
    'Content-Type': 'application/scim+json',
    'Authorization': 'Bearer '+ auth_token,
    }

    contents = open(updateFile, "r")

    # Convert file contents into JSON format
    dataString = json.dumps(contents.read())
    data = json.loads(dataString)

    response = requests.patch(URL + '/admin/v1/Users/' + userId, headers=headers, data=data, verify=False)
    
    # Error handling
    if response.status_code == 200:
        print(userName + ' has been updated')
    else:
        print('An error has occured\n')
        print(response.json())

def deleteUser(userName):
    headers = {
    'Authorization': 'Bearer '+ auth_token,
    }
    userId = getUserId(userName)

    response = requests.delete(URL + '/admin/v1/Users/' + userId, headers=headers)

    # Error handling
    if response.status_code == 204:
        print(userName + ' has been deleted')
    else:
        print('An error has occured\n')
        print(response.json())

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
        print('bulk.json has been successfully imported.')
        print(response.json())
    else:
        print('An error has occured\n')
        print(response.json())

__init__()