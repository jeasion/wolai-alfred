# -*- coding: UTF-8 -*-
import gzip
import http.client
import json
import os.path
import sys
from io import BytesIO
from payload import Payload

# 参数配置
wolaiSpaceId = os.environ['wolaiSpaceId']
cookie = os.environ['cookie']
userId = os.environ['userId']
userName = os.environ['userName']
useDesktopClient = False
url = "https://www.wolai.com/"
clientUrl = "wolai://" + url

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
    headers = {"Content-type": "application/json", "Cookie": cookie}
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

itemList = []
for searchResultObject in searchResultList:
    item = {
        "type": searchResultObject.get("type"),
        "title": searchResultObject.get("title"),
        "arg": searchResultObject.get("link"),
        "subtitle": ""
    }
    if searchResultObject.get("icon").__contains__("emoji"):
        item["icon"] = searchResultObject.get("icon")[1]
        item["autocomplete"] = searchResultObject.get("title")
        itemList.append(item)

items = {}
if not itemList:
    item = {
        "uid": 1,
        "type": "default",
        "title": "Open Wolai - No results, empty query, or error",
        "arg": getWolaiurl()
    }
    itemList.append(item)
items["items"] = itemList
items_json = json.dumps(items)
sys.stdout.write(items_json)
