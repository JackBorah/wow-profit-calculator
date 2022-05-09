#gets the same access token across multiple requests
#each token lasts a day
#use pprint from import pprint to print out legible json
#illidanAH.json()['auctions'][0] will get the first auction from the illidanAH
#links.self.href is the link from where the current json response came from
import requests
from pprint import pprint

#token data
tokenData = {'grant_type': 'client_credentials'}

#Client ID, secret
auth = ('e1682bd6dd3843a0bfa24d652e9490be', '8COiOaIfT4jgFNOhFsdnzVlY6rgJ7Q2a')

#defaults
region = 'us'
namespace = 'dynamic-us'
locale = 'en_US'

accessTokenResponse = requests.post('https://us.battle.net/oauth/token', data=tokenData, auth=auth)
accessToken = accessTokenResponse.json()['access_token']
accessTokenQuery = {'access_token': accessToken}
#Connected-Realms
connectedRealmsIndex = requests.get('https://us.api.blizzard.com/data/wow/connected-realm/index', params={'region':region, 'namespace': namespace, 'locale': locale, 'access_token':accessToken})
connectedRealmUrl = connectedRealmsIndex.json()['connected_realms'][0]['href']
#Realm
connectedRealmsDetail = requests.get(connectedRealmUrl, params=accessTokenQuery)
connectedRealmsAucitonsUrl = connectedRealmsDetail.json()['auctions']['href']
#Connected-Realm Auctions
connectedRealmAuctions = requests.get(connectedRealmsAucitonsUrl, params=accessTokenQuery)

#Professions
professionIndex = requests.get('https://us.api.blizzard.com/data/wow/profession/index', params={'namespace':'static-us', 'region':region, 'locale':locale, 'access_token':accessToken})


#pprint(connectedRealmsIndex.json())
#pprint(connectedRealmsDetail.json())
#pprint(connectedRealmAuctions.json())

for auctionDict in connectedRealmAuctions.json()['auctions']:
    if auctionDict['item']['id'] == 178926:
        pprint(auctionDict)

#its annoying but the items with a bonus_list can either be found on wowhead or found in an opaque wow tools query.
#I don't think either of these could be fully automated like pulling data if only they supplied it from the api 
#This seems like I ahve to update it by hand.
#the wowhead page for an item does take a querystring with a bonusId which will return the correct variant of the item
