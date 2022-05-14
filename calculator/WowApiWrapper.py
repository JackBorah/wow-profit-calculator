#gets the same access token across multiple requests
#each token lasts a day
#use pprint from import pprint to print out legible json
#illidanAH.json()['auctions'][0] will get the first auction from the illidanAH
#links.self.href is the link from where the current json response came from
from os import access
from pytest import param
import requests
from pprint import pprint

#token data
tokenData = {'grant_type': 'client_credentials'}

#Client ID, secret
auth = ('e1682bd6dd3843a0bfa24d652e9490be', '8COiOaIfT4jgFNOhFsdnzVlY6rgJ7Q2a')

#defaults
region = 'us'
dynamicNamespace = 'dynamic-us'
staticNamespace = 'static-us'
locale = 'en_US'
accessTokenParam = {}


def getAccessToken(tokenData = tokenData, auth = auth):
    accessTokenResponse = requests.post('https://us.battle.net/oauth/token', data=tokenData, auth=auth)
    return accessTokenResponse.json()['access_token']

accessToken = getAccessToken()

def getConnectedRealmIndex(region = region, namespace = dynamicNamespace, locale = locale):
    return requests.get('https://us.api.blizzard.com/data/wow/connected-realm/index', params={'region':region, 'namespace': namespace, 'locale': locale, 'access_token':accessToken}).json()

def getRealm(connectedRealmId, region = region, namespace = dynamicNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/connected-realm/{connectedRealmId}', params={'region':region, 'namespace': namespace, 'locale': locale, 'access_token':accessToken}).json()

def getAuctions(connectedRealmId, region = region, namespace = dynamicNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/connected-realm/{connectedRealmId}/auctions', params={'region':region, 'namespace':namespace, 'locale':locale, 'access_token':accessToken}).json()

def getProfessionIndex(region = region, namespace = staticNamespace, locale = locale):
    return requests.get('https://us.api.blizzard.com/data/wow/profession/index', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

#Includes skill teirs (classic, burning crusade, shadowlands, ...) id
def getProfessionTeirs(professionId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/profession/{professionId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

def getProfessionIcon(professionId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/media/profession/{professionId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

#Includes the categories (weapon mods, belts, ...) and the recipes (id, name) in them
def getProfessionTeirDetails(professionId, skillTierId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/profession/{professionId}/skill-tier/{skillTierId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

def getRecipeDetails(recipeId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/recipe/{recipeId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

def getRecipeIcon(recipeId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/media/recipe/{recipeId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

#consumable, ...
def getItemClasses(region = region, namespace = staticNamespace, locale = locale):
    return requests.get('https://us.api.blizzard.com/data/wow/item-class/index', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

#flasks, vantus runes, ...
def getItemSubclasses(itemClassId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/item-class/{itemClassId}', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

def getItemSetIndex(region = region, namespace = staticNamespace, locale = locale):
    return requests.get('https://us.api.blizzard.com/data/wow/item-set/index?', params={'namespace':namespace, 'region':region, 'locale':locale,'access_token':accessToken}).json()

def getItemList(idStart = 1, pageSize = 1000, page = 1, orderby = 'id', region = region, namespace = staticNamespace):
    return requests.get(f'https://us.api.blizzard.com/data/wow/search/item', params={'namespace':namespace, 'access_token':accessToken, '_pageSize': pageSize,'_page':page, 'orderby': orderby, 'id':f'[{idStart},]'})

def getItemIcon(itemId, region = region, namespace = staticNamespace, locale = locale):
    return requests.get(f'https://us.api.blizzard.com/data/wow/media/item/{itemId}', params={'namespace':namespace, 'region':region, 'locale':locale,'access_token':accessToken}).json()

def getWowToken(region = region, namespace = staticNamespace, locale = locale):
    return requests.get('https://us.api.blizzard.com/data/wow/token/index', params={'namespace':namespace, 'region':region, 'locale':locale, 'access_token':accessToken}).json()

#its annoying but the items with a bonus_list can either be found on wowhead or found in an opaque wow tools query.
#I don't think either of these could be fully automated like pulling data if only they supplied it from the api 
#This seems like I ahve to update it by hand.
#the wowhead page for an item does take a querystring with a bonusId which will return the correct variant of the item

pprint(getItemList().json())
pprint(getItemList().url)