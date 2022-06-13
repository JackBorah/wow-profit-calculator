import os
import sys
from dotenv import load_dotenv
from getwowdata import WowApi
import django

load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models

us_region_api = WowApi("us", "en_US")
eu_region_api = WowApi("eu", "en_US")
kr_region_api = WowApi("kr", "en_US")

region_api_list = [us_region_api, eu_region_api, kr_region_api]


def consume_realm(region_api: WowApi) -> dict:
    """Consumes the WoW region_api and finds the values to be inserted into the db.

    Args:
        region_api (Wowregion_api): The region_api that will be pulled from.

    Returns:
        The fields in a tuple required by the models.
    """

    json = region_api.connected_realm_search()

    for connected_realm in json[
        "results"
    ]:  # each entry in results is a connected realm cluster
        connected_realm_id = models.ConnectedRealmsIndex.objects.get(
            connected_realm_id=connected_realm["data"]["id"]
        )
        population = connected_realm["data"]["population"]["type"]
        for realm in connected_realm["data"]["realms"]:
            realm_id = realm["id"]
            name = realm["name"]["en_US"]
            region = realm["region"]["name"]["en_US"]
            timezone = realm["timezone"]
            play_style = realm["type"]["type"]
            yield {
                'connected_realm_id':connected_realm_id,
                'population':population,
                'realm_id':realm_id,
                'name':name,
                'region':region,
                'timezone':timezone,
                'play_style':play_style,
            }


def insert_realm(region_api: WowApi):
    """Saves the record to the attached db.

    Args:
        region_api (Wowregion_api): The region_api being consumed.
    """
    for data in consume_realm(region_api):
        record = models.Realm(
            connected_realm = data.get('connected_realm_id'),
            population = data.get('population'),
            realm_id = data.get('realm_id'),
            name = data.get('name'),
            region = data.get('region'),
            timezone = data.get('timezone'),
            play_style = data.get('play_style'),
        )
        record.save()


def consume_connected_realms_index(region_api: WowApi) -> tuple:
    """Yields all connected_realm id's from an region_api.

    Args:
        region_api (WowApi): A WowApi object.
    """
    json = region_api.connected_realm_search()

    for connected_realm in json["results"]:
        yield int(connected_realm["data"]["id"])


def insert_connected_realms_index(region_api: WowApi):
    """Inserts connected_realm_id into the ConnectedRealmsIndex model.

    Args:
        region_api (WowApi): A WowApi object.
    """
    for connected_realm_id in consume_connected_realms_index(region_api):
        record = models.ConnectedRealmsIndex(connected_realm_id)
        record.save()


def consume_auctions(region_api: WowApi, connected_realm_id: int) -> tuple:
    """Yields all auctions fields from an region_api.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of the connected realm where the auctions will come from.
    """
    json = region_api.get_auctions(connected_realm_id)
    for auction in json["auctions"]:
        item_modifier_list = []
        item_bonus_list = []

        auction_id = auction.get("id")
        buyout = auction.get("buyout")
        bid = auction.get("bid")
        unit_price = auction.get("unit_price")
        quantity = auction.get("quantity")
        time_left = auction.get("time_left")
        connected_realm_id = models.ConnectedRealmsIndex.objects.get(
            connected_realm_id=connected_realm_id
        )
        item = models.Item.objects.get(id=auction.get("item").get("id"))
        pet_level = auction.get("item").get("pet_level")
        if auction.get("item").get("bonus_lists"):
            for bonus_id in auction.get("item").get("bonus_lists"):
                item_bonus_list.append(bonus_id)
        if auction.get("item").get("modifiers"):
            for modifier in auction.get("item").get("modifiers"):
                item_modifier_list.append(modifier)
        yield {
            'auction_id':auction_id,
            'buyout':buyout,
            'bid':bid,
            'unit_price':unit_price,
            'quantity':quantity,
            'time_left':time_left,
            'connected_realm_id':connected_realm_id,
            'item':item,
            'pet_level':pet_level,
            'item_bonus_list':item_bonus_list,
            'item_modifier_list':item_modifier_list,
        }


def insert_auction(region_api: WowApi, connected_realm_id: WowApi):
    for data in consume_auctions(region_api, connected_realm_id):
        auction = models.Auction(
            auction_id=data['auction_id'],
            buyout=data['buyout'],
            bid=data['bid'],
            unit_price=data['unit_price'],
            quantity=data['quantity'],
            time_left=data['time_left'],
            connected_realm_id=data['connected_realm_id'],
            item=data['item'],
            pet_level=data['pet_level'],
        )
        auction.save()
        for bonus_object in data['item_bonus_list']:
            auction.ItemBonus_set.add(bonus_object)
        for modifier_obj in data['item_modifier_list']:
            auction.ItemModifier_set.add(modifier_obj)

def consume_item_bonus(region_api: WowApi, connected_realm_id: int) -> tuple:
    """Yields all item bonuses from auctions.

    The results depends on what is currently posted to the auction house. So,
    This will proballly return an incomplete list of bonuses.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of a connected realm.
    """
    json = region_api.get_auctions(connected_realm_id)
    for auction in json["auctions"]:
        if auction.get("item").get("bonus_lists"):
            for bonus_id in auction["item"]["bonus_lists"]:
                yield bonus_id


def insert_item_bonus(region_api: WowApi, connected_realm_id: int):
    """Inserts item bonuses into ItemBonus model.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of a connected realm.
    """
    for data in consume_item_bonus(region_api, connected_realm_id):
        item_bonus = models.ItemBonus.objects.filter(id=data)
        if not item_bonus:  # If no record then add it to table
            record = models.ItemBonus(id=data)
            record.save()


def consume_item_modifiers(region_api: WowApi, connected_realm_id: int) -> tuple:
    """Yields all item modifiers from auctions.

    The results depends on what is currently posted to the auction house. So,
    This will proballly return an incomplete list of modifiers.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of a connected realm.
    """
    json = region_api.get_auctions(connected_realm_id)
    for auction in json["auctions"]:
        if auction.get("item").get("modifiers"):
            for modifier in auction["item"]["modifiers"]:
                mod_type = int(modifier["type"])
                value = int(modifier["value"])
                yield (mod_type, value)


def insert_item_modifiers(region_api: WowApi, connected_realm_id: int):
    """Inserts item modifiers into ItemModifier model.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of a connected realm.
    """
    for data in consume_item_modifiers(region_api, connected_realm_id):
        item_modifiers = models.ItemModifier.objects.filter(modifier_type=data[0], value=data[1])
        if not item_modifiers:  # If no record then add it to table
            record = models.ItemModifier(modifier_type=data[0], value=data[1])
            record.save()


def consume_profession_index(region_api: WowApi) -> tuple:
    pass


def insert_profession_index(region_api: WowApi):
    pass


def consume_profession_teir(region_api: WowApi) -> tuple:
    pass


def insert_profession_teir(region_api: WowApi):
    pass


def consume_recipe_catagory(region_api: WowApi) -> tuple:
    pass


def insert_recipe_catagory(region_api: WowApi):
    pass


def consume_recipe(region_api: WowApi) -> tuple:
    pass


def insert_recipe(region_api: WowApi):
    pass


def consume_material(region_api: WowApi) -> tuple:
    pass


def insert_material(region_api: WowApi):
    pass


def consume_all_item(region_api: WowApi) -> tuple:
    """Yields all item data revelant to the item model.
    """
    json = region_api.item_search(**{'id':f'({0},)'})
    while json['results']: #as long as json is redefined by the loop body and that is visable to the while loop it will work
        last_id = json['results'][-1]['data']['id']
        json = region_api.item_search(**{'id':f'({last_id},)', 'orderby': 'id', '_pageSize': 1000})
        for item in json['results']:
            item_id = item['data']['id']
            name = item['data']['name']['en_US']
            yield (item_id, name)


def insert_all_item(region_api: WowApi):
    """Inserts all items into the Item model.
    """
    count = 0
    for data in consume_all_item(region_api):
        record = models.Item(id = data[0], name = data[1])
        print(f'\r{count}', end='')
        record.save()


if __name__ == "__main__":
#    insert_connected_realms_index(us_region_api)
#    insert_realm(us_region_api)
#    insert_all_item(us_region_api)
    insert_item_bonus(us_region_api, 4)
    insert_item_modifiers(us_region_api, 4)
    insert_auction(us_region_api, 4)
