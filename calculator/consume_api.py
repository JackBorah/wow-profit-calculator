from itertools import product
import os
import sys
from dotenv import load_dotenv
from getwowdata import WowApi
import django
from pprint import pprint

load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models

us_region_api = WowApi("us", "en_US")
eu_region_api = WowApi("eu", "en_US")
kr_region_api = WowApi("kr", "en_US")

region_api_list = [us_region_api, eu_region_api, kr_region_api]


def consume_realm(region_api: WowApi) -> list:
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
                "connected_realm_id": connected_realm_id,
                "population": population,
                "realm_id": realm_id,
                "name": name,
                "region": region,
                "timezone": timezone,
                "play_style": play_style,
            }


def insert_realm(region_api: WowApi):
    """Saves the record to the attached db.

    Args:
        region_api (Wowregion_api): The region_api being consumed.
    """
    for data in consume_realm(region_api):
        record = models.Realm(
            connected_realm=data.get("connected_realm_id"),
            population=data.get("population"),
            realm_id=data.get("realm_id"),
            name=data.get("name"),
            region=data.get("region"),
            timezone=data.get("timezone"),
            play_style=data.get("play_style"),
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


def consume_auctions(region_api: WowApi, connected_realm_id: int) -> list:
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
                bonus_obj, bool = models.ItemBonus.objects.get_or_create(id=bonus_id)
                item_bonus_list.append(bonus_obj)
        if auction.get("item").get("modifiers"):
            for modifier in auction.get("item").get("modifiers"):
                modifier_obj, bool = models.ItemModifier.objects.get_or_create(
                    modifier_type=modifier["type"], value=modifier["value"]
                )
                item_modifier_list.append(modifier_obj)
        yield {
            "auction_id": auction_id,
            "buyout": buyout,
            "bid": bid,
            "unit_price": unit_price,
            "quantity": quantity,
            "time_left": time_left,
            "connected_realm_id": connected_realm_id,
            "item": item,
            "pet_level": pet_level,
            "item_bonus_list": item_bonus_list,
            "item_modifier_list": item_modifier_list,
        }


def insert_auction(region_api: WowApi, connected_realm_id: int):
    for data in consume_auctions(region_api, connected_realm_id):
        auction = models.Auction(
            auction_id=data.get("auction_id"),
            buyout=data["buyout"],
            bid=data["bid"],
            unit_price=data["unit_price"],
            quantity=data["quantity"],
            time_left=data["time_left"],
            connected_realm=data["connected_realm_id"],
            item=data["item"],
            pet_level=data["pet_level"],
        )
        auction.save()
        for bonus_obj in data["item_bonus_list"]:
            bonus_obj.auctions.add(auction)
        for modifier_obj in data["item_modifier_list"]:
            modifier_obj.auctions.add(auction)


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
        item_modifiers = models.ItemModifier.objects.filter(
            modifier_type=data[0], value=data[1]
        )
        if not item_modifiers:  # If no record then add it to table
            record = models.ItemModifier(modifier_type=data[0], value=data[1])
            record.save()


def consume_profession_index(region_api: WowApi) -> tuple:
    json = region_api.get_profession_index()
    for profession in json["professions"]:
        id = profession.get("id")
        name = profession.get("name")
        yield {"name": name, "id": id}


def insert_profession_index(region_api: WowApi):
    for data in consume_profession_index(region_api):
        record = models.ProfessionIndex(name=data.get("name"), id=data.get("id"))
        record.save()


def consume_profession_tier(region_api: WowApi, profession_id: int) -> dict:
    json = region_api.get_profession_tiers(profession_id)
    profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
    for tier in json["skill_tiers"]:
        name = tier.get("name")
        id = tier.get("id")
        yield {"id": id, "name": name, "profession": profession_obj}


def insert_profession_tier(region_api: WowApi, profession_id: int):
    for tier in consume_profession_tier(region_api, profession_id):
        profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
        name = tier.get("name")
        id = tier.get("id")
        record = models.ProfessionTier(id=id, name=name, profession=profession_obj)
        record.save()


def consume_recipe_category(
    region_api: WowApi, profession_id: int, skill_tier_id: int
) -> tuple:
    json = region_api.get_profession_tier_categories(profession_id, skill_tier_id)
    skill_tier_obj = models.ProfessionTier.objects.get(id=skill_tier_id)
    for category in json.get("categories"):
        category_name = category.get("name")
        yield {
            "category_name": category_name,
            "profession_tier_obj": skill_tier_obj,
        }
        for recipe in category.get("recipes"):
            recipe_name = recipe.get("name")
            recipe_id = recipe.get("id")
            yield {
                "recipe_name": recipe_name,
                "recipe_id": recipe_id,
            }


def insert_recipe_category(region_api: WowApi, profession_id: int, skill_tier_id: int):
    """Inserts data from recipe category into that model and the name and id into the recipe model."""
    for category in consume_recipe_category(region_api, profession_id, skill_tier_id):
        category_record, created = models.RecipeCategory.objects.get_or_create(
            name=category.get("category_name"),
            profession_tier=category.get("profession_tier_obj"),
        )
        if created:
            category_record.save()
        if category.get("recipe_name"):
            recipe_record = models.Recipe(
                id=category.get("recipe_id"),
                name=category.get("recipe_name"),
                recipe_category=category_record,
            )
            recipe_record.save()


def consume_recipe(region_api: WowApi, recipe_id: int) -> tuple:
    json = region_api.get_recipe(recipe_id)
    #recipe id, recipe name, product foreignKey, material(s), material quantity
    recipe_id = json.get('id')
    recipe_name = json.get('name')
    product_id = json.get('crafted_item').get('id')
    product_obj = models.Item.objects.get(id=product_id)
    product_quantity = json.get('crafted_quantity').get('value')
    materials_list = []
    for mat in json.get('reagents'):
        mat_item_obj = models.Item.objects.get(id = mat.get('reagent').get('id'))
        mat_item_quantity = mat.get('quantity')
        mat_obj, created = models.Material.objects.get_or_create(item = mat_item_obj, quantity = mat_item_quantity)
        materials_list.append(mat_obj)
    return {
        'recipe_name':recipe_name,
        'product_obj':product_obj,
        'product_quantity':product_quantity,
        'materials_list':materials_list
    }

def insert_recipe(region_api: WowApi, recipe_id: int):
    recipe = consume_recipe(region_api, recipe_id)
    record = models.Recipe.objects.get(id=recipe_id)
    record.product = recipe.get('product_obj')
    record.product_quantity = recipe.get('product_quantity')
    for material in recipe.get('materials_list'):
        record.mats.add(material)
        record.save()


def consume_all_item(region_api: WowApi) -> tuple:
    """Yields all item data revelant to the item model."""
    json = region_api.item_search(**{"id": f"({0},)"})
    while json[
        "results"
    ]:  # as long as json is redefined by the loop body and that is visable to the while loop it will work
        for item in json["results"]:
            item_id = item["data"]["id"]
            name = item["data"]["name"]["en_US"]
            yield {'item_id': item_id, 'name':name}
        last_id = json["results"][-1]["data"]["id"]
        json = region_api.item_search(
            **{"id": f"({last_id},)", "orderby": "id", "_pageSize": 1000}
        )

def insert_all_item(region_api: WowApi):
    """Inserts all items into the Item model."""
    count = 0
    for data in consume_all_item(region_api):
        record = models.Item(id=data.get('item_id'), name=data.get('name'))
        print(f"\r{count} items queried", end="")
        record.save()


if __name__ == "__main__":
    insert_connected_realms_index(us_region_api)
    insert_realm(us_region_api)
    insert_all_item(us_region_api)
    insert_auction(us_region_api, 4)
