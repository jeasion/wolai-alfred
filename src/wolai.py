# -*- coding: UTF-8 -*-
import gzip
import http.client
import json
import os.path
import sys
from io import BytesIO
from payload import Payload

debug = False
wolaiSpaceId = None
cookie = None
userId = None
userName = None
useDesktopClient = None
url = "https://www.wolai.com/"
clientUrl = "wolai://" + url

# 参数配置
if debug:
    with open("config.json") as json_file:
        config = json.load(json_file)

    wolaiSpaceId = config["wolaiSpaceId"]
    cookie = config['cookie']
    userId = config['userId']
    userName = config['userName']
    useDesktopClient = config["useDesktopClient"]
    alfredQuery = config["alfredQuery"]

else:
    wolaiSpaceId = os.environ['wolaiSpaceId']
    cookie = os.environ['cookie']
    userId = os.environ['userId']
    userName = os.environ['userName']
    useDesktopClient = False

    # query参数
    alfredQuery = str(sys.argv[1])

if (useDesktopClient == 'true') | (useDesktopClient == 'True') | (useDesktopClient == 'TRUE'):
    useDesktopClient = True
else:
    useDesktopClient = False


def buildWolaiSearchData():
    query = {
        "query": alfredQuery,
        "workspaceId": wolaiSpaceId,
        "fuzzy": "true",
        "order": "desc",
        "active": "1",
        "pageId": ""
    }

    jsonData = json.dumps(query)
    return jsonData


def getWolaiurl():
    if useDesktopClient:
        return clientUrl + userName + "/"
    else:
        return url + userName + "/"


searchResultList = []
if alfredQuery and alfredQuery.strip():
    headers = {"Content-type": "application/json", "Cookie": cookie, "jeasion": "test"}
    conn = http.client.HTTPSConnection("api.wolai.com")
    conn.request("POST", "/v1/search/advancedSearch", buildWolaiSearchData(), headers)
    response = conn.getresponse()
    buff = BytesIO(response.read())
    data = gzip.GzipFile(fileobj=buff).read().decode("utf-8")

    dataStr = json.dumps(data).replace("<em>", "").replace("</em>", "")
    data = json.loads(dataStr)
    conn.close()

    searchResults = Payload(data)
    try:
        result = searchResults.data.get('result').get("items")
        for x in result:
            clientLink = getWolaiurl() + x.get("id")
            link = getWolaiurl() + x.get("id")
            x["clientLink"] = clientLink
            x["webLink"] = url + x.get("id")
            x["link"] = link
            searchResultList.append(x)
    except:
        pass

map = {}
for searchResultObject in searchResultList:
    item = {
        "type": searchResultObject.get("type"),
        "title": searchResultObject.get("title"),
        "arg": searchResultObject.get("link"),
        "subtitle": ""
    }
    key = searchResultObject.get("link")
    if key not in map:
        map[key] = item

items = {}
if not map:
    item = {
        "uid": 1,
        "type": "default",
        "title": "Open Wolai - No results, empty query, or error",
        "arg": getWolaiurl()
    }
    map["empty"] = item
items_json = json.dumps(list(map.values()))

if debug:
    print(items_json)
else:
    sys.stdout.write(items_json)
