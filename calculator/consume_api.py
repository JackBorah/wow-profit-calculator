import os
import sys
import time
from dotenv import load_dotenv
from getwowdata import WowApi
from getwowdata import convert_to_datetime
import django
from pprint import pprint

load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models

def consume_realm(region_api: WowApi) -> dict:
    """Gets all the realms for a region and yields the values to be inserted into the db.

    Args:
        region_api (WowApi): The region_api that will be pulled from.

    Yields:
        The fields in a tuple required by the models.
    """

    json = region_api.connected_realm_search()

    for connected_realm in json[
        "results"
    ]:  # each entry in results is a connected realm cluster
        connected_realm_obj = models.ConnectedRealmsIndex.objects.get(
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
                "connected_realm_obj": connected_realm_obj,
                "population": population,
                "realm_id": realm_id,
                "name": name,
                "region": region,
                "timezone": timezone,
                "play_style": play_style,
            }


def insert_realm(region_api: WowApi) -> None:
    """Saves the realm records to the Realm db.

    Args:
        region_api (WowApi): The region_api being consumed.
    """
    print('Inserting realms...')
    for data in consume_realm(region_api):
        record = models.Realm(
            connected_realm=data.get("connected_realm_obj"),
            population=data.get("population"),
            realm_id=data.get("realm_id"),
            name=data.get("name"),
            region=data.get("region"),
            timezone=data.get("timezone"),
            play_style=data.get("play_style"),
        )
        record.save()
    print('Realms inserted')


def consume_connected_realms_index(region_api: WowApi) -> dict:
    """Yields all connected_realm id's from an region_api.

    Args:
        region_api (WowApi): A WowApi object.
    """
    json = region_api.connected_realm_search()

    for connected_realm in json["results"]:
        yield int(connected_realm["data"]["id"])


def insert_connected_realms_index(region_api: WowApi) -> None:
    """Inserts connected_realm_id into the ConnectedRealmsIndex model.

    Args:
        region_api (WowApi): A WowApi object.
    """
    print('Inserting connected realm index...')
    for connected_realm_id in consume_connected_realms_index(region_api):
        record = models.ConnectedRealmsIndex(connected_realm_id)
        record.save()
    print('Connected realm index inserted')


def consume_auctions(region_api: WowApi, connected_realm_id: int) -> dict:
    """Yields all auctions fields from an region_api.

    Yields auction data to be inserted by insert_auctions. Also
    creates item bonuses or item modifiers if they are not in the
    db already.

    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of the connected realm where the auctions will come from.
    """
    #The body of this is taking a long time
    #Take it apart and time the components
    #How long is: dict.get(), creating and appending to a list
    #get_or_create items, yield vs return, how long is the bonus and modifier loops
    connected_realm_obj = models.ConnectedRealmsIndex.objects.get(
        connected_realm_id=connected_realm_id
    )
    json = region_api.get_auctions(connected_realm_id, timeout = 60)
    all_items = models.Item.objects.all()
    all_bonuses = models.ItemBonus.objects.all()
    timestamp = convert_to_datetime(json['Date'])

    for auction in json["auctions"]:
        #item_modifier_list = []
        item_bonus_list = []

        auction_id = auction.get("id")
        buyout = auction.get("buyout")
        bid = auction.get("bid")
        unit_price = auction.get("unit_price")
        quantity = auction.get("quantity")
        time_left = auction.get("time_left")
        item, created = all_items.get_or_create(id=auction.get("item").get("id"))
        pet_level = auction.get("item").get("pet_level")
        if auction.get("item").get("bonus_lists"):
            for bonus_id in auction.get("item").get("bonus_lists"):
                bonus_obj, created = all_bonuses.get_or_create(id=bonus_id)
                item_bonus_list.append(bonus_obj)
        #useless?
        #if auction.get("item").get("modifiers"):
        #    for modifier in auction.get("item").get("modifiers"):
        #        modifier_obj, created = models.ItemModifier.objects.get_or_create(
        #            modifier_type=modifier["type"], value=modifier["value"]
        #        )
        #        item_modifier_list.append(modifier_obj)
        yield {
            "auction_id": auction_id,
            "buyout": buyout,
            "bid": bid,
            "unit_price": unit_price,
            "quantity": quantity,
            "time_left": time_left,
            "connected_realm_obj": connected_realm_obj,
            "item": item,
            "pet_level": pet_level,
            "item_bonus_list": item_bonus_list,
            "timestamp":timestamp
            #"item_modifier_list": item_modifier_list,
        }


def insert_auction(region_api: WowApi, connected_realm_id: int) -> None:
    """Inserts auction records from conusme_auction into the auction model
    
    Args:
        region_api (WowApi): A WowApi object.
        connected_realm_id (int): The id of the connected realm where the auctions will come from.
    """
    print(f'Inserting auctions from realm {connected_realm_id}...')
    for data in consume_auctions(region_api, connected_realm_id):

        auction_id = data['auction_id']
        auction = models.Auction(
            auction_id=data.get("auction_id"),
            buyout=data["buyout"],
            bid=data["bid"],
            unit_price=data["unit_price"],
            quantity=data["quantity"],
            time_left=data["time_left"],
            connected_realm=data["connected_realm_obj"],
            item=data["item"],
            pet_level=data["pet_level"],
            timestamp=data['timestamp']
        )
        auction.save()
        for bonus_obj in data["item_bonus_list"]:
            bonus_obj.auctions.add(auction)
        #useless?
        #for modifier_obj in data["item_modifier_list"]:
        #    modifier_obj.auctions.add(auction)
    print(f'Auctions from realm {connected_realm_id} inserted.')


def consume_item_bonus(region_api: WowApi, connected_realm_id: int) -> dict:
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


def insert_item_bonus(region_api: WowApi, connected_realm_id: int) -> None:
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
    print('Item bonuses inserted')


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


def insert_item_modifiers(region_api: WowApi, connected_realm_id: int) -> None:
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
    print('Item modifiers inserted')


def consume_profession_index(region_api: WowApi) -> dict:
    """Yields profession names and id from profession index API.

    Args: 
        region_api (WowApi): A WowApi object.
    """
    json = region_api.get_profession_index()
    for profession in json["professions"]:
        id = profession.get("id")
        name = profession.get("name")
        yield {"name": name, "id": id}


def insert_profession_index(region_api: WowApi) -> None:
    """Inserts records into the profession index model.
    
    Args: 
        region_api (WowApi): A WowApi object.
    """
    print('Inserting profession index...')
    for data in consume_profession_index(region_api):
        record = models.ProfessionIndex(name=data.get("name"), id=data.get("id"))
        record.save()
    print('Profession index inserted')


def consume_profession_tier(region_api: WowApi, profession_id: int) -> dict:
    """Yields data from profession skill tier API.
    
    Args: 
        region_api (WowApi): A WowApi object.
        profession_id (int): A professions id. Get from profession index.
    """
    json = region_api.get_profession_tiers(profession_id)
    profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
    if json.get('skill_tiers'):
        for tier in json["skill_tiers"]:
            name = tier.get("name")
            id = tier.get("id")
            yield {"id": id, "name": name, "profession": profession_obj}

def insert_profession_tier(region_api: WowApi, profession_id: int) -> None:
    """Inserts data from consume_profession_tier into the profession tier model.
    
    Args: 
        region_api (WowApi): A WowApi object.
        profession_id (int): A professions id. Get from profession index.
    """
    print(f'Inserting profession: {profession_id} tiers...')
    for tier in consume_profession_tier(region_api, profession_id):
        profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
        name = tier.get("name")
        id = tier.get("id")
        record = models.ProfessionTier(id=id, name=name, profession=profession_obj)
        record.save()
    print(f'Profession: {profession_id} tiers inserted')


def consume_recipe_category(
    region_api: WowApi, profession_id: int, skill_tier_id: int
) -> dict:
    """Consumes recipe category data from the recipe categories API.
    
    Args: 
        region_api (WowApi): A WowApi object.
        profession_id (int): A professions id. Get from profession index.
        skill_tier_id (int): A skill tiers id. Get from profession tiers.
    """
    json = region_api.get_profession_tier_categories(profession_id, skill_tier_id)
    skill_tier_obj = models.ProfessionTier.objects.get(id=skill_tier_id)
    if json.get('categories'):
        for category in json["categories"]:
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
    else:
        category_name = json['name']
        profession_tier_obj = skill_tier_obj
        yield {'category_name':category_name, 'profession_tier_obj':profession_tier_obj}

def insert_recipe_category(region_api: WowApi, profession_id: int, skill_tier_id: int) -> None:
    """Inserts data from recipe category into that model and the name and id into the recipe model.

    Args: 
        region_api (WowApi): A WowApi object.
        profession_id (int): A professions id. Get from profession index.
        skill_tier_id (int): A skill tiers id. Get from profession tiers.
    """
    print(f'Inserting profession: {profession_id}, and skill tier: {skill_tier_id}...')
    for category in consume_recipe_category(region_api, profession_id, skill_tier_id):
        if category.get('category_name'):
            category_record, created = models.RecipeCategory.objects.get_or_create(
                name=category["category_name"],
                profession_tier=category["profession_tier_obj"],
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
    print(f'Profession: {profession_id}, category: {skill_tier_id} inserted')


def consume_recipe(region_api: WowApi, recipe_id: int) -> dict:
    """Yields data from the recipe API and populates material model.
    
    Args:
        region_api (WowApi): A WowApi object.
        recipe_id (int): The id of a recipe. 
    """
    json = region_api.get_recipe(recipe_id)
    #recipe id, recipe name, product foreignKey, material(s), material quantity
    recipe_id = json['id']
    recipe_name = json['name']
    #If 'crafted_quantity key exists return its values in a tuple
    #Else return a default of (0,)
    if json.get('crafted_quantity'):
        if json.get('crafted_quantity').get('value'):
            product_quantity = (json.get('crafted_quantity')['value'],)
        else:
            min_quantity = json.get('crafted_quantity')['minimum']
            max_quantity = json.get('crafted_quantity')['maximum']
            product_quantity = (min_quantity,max_quantity)
    else:
        product_quantity = (0,)
    product_list = []
    if json.get('crafted_item'):
        product_id = json.get('crafted_item')['id']
        product_name = json.get('crafted_item')['name']
        product_item_obj, created = models.Item.objects.get_or_create(id=product_id, name=product_name)
        product_list.append(product_item_obj)
    if json.get('alliance_crafted_item'):
        alliance_product_id = json.get('alliance_crafted_item')['id']
        alliance_product_name = json.get('alliance_crafted_item')['name']
        alliance_product_item_obj, created = models.Item.objects.get_or_create(id=alliance_product_id, name=alliance_product_name)
        product_list.append(alliance_product_item_obj)
    if json.get('horde_crafted_item'):
        horde_product_id = json.get('horde_crafted_item')['id']
        horde_product_name = json.get('horde_crafted_item')['name']
        horde_product_item_obj, created = models.Item.objects.get_or_create(id=horde_product_id, name=horde_product_name)
        product_list.append(horde_product_item_obj)
    materials_list = []
    if json.get('reagents'):
        for mat in json.get('reagents'):
            mat_id = mat['reagent']['id']
            mat_name = mat['reagent']['name']
            mat_item_obj, created = models.Item.objects.get_or_create(id = mat_id, name = mat_name)
            mat_item_quantity = mat.get('quantity')
            mat_obj, created = models.Material.objects.get_or_create(item = mat_item_obj, quantity = mat_item_quantity)
            materials_list.append(mat_obj)
    return {
        'recipe_name':recipe_name, #str
        'product_quantity':product_quantity, #tuple
        'materials_list':materials_list, #list
        'product_list': product_list #list
    }

def insert_recipe(region_api: WowApi, recipe_id: int) -> None:
    """Inserts records from consume recipe into the recipe model.

    Requires recipe categories to be inserted first as this function
    gets an incomplete recipe from the db and fills the rest of its 
    fields out.

    Args:
        region_api (WowApi): A WowApi object.
        recipe_id (int): The id of a recipe. 
    """
    consume_recipe_data = consume_recipe(region_api, recipe_id)
    recipe = models.Recipe.objects.get(id=recipe_id)
    for product_item_obj in consume_recipe_data['product_list']:
        if product_item_obj: #obj or None
            if len(consume_recipe_data['product_quantity']) == 1:
                min_quantity = consume_recipe_data.get('product_quantity')[0]
                max_quantity = consume_recipe_data.get('product_quantity')[0]
            else:
                min_quantity = consume_recipe_data.get('product_quantity')[0]
                max_quantity = consume_recipe_data.get('product_quantity')[1]
            product_record = models.Product(recipe=recipe, item=product_item_obj, min_quantity=min_quantity, max_quantity=max_quantity)
            product_record.save()
    for material in consume_recipe_data['materials_list']:
        recipe.mats.add(material)
        recipe.save()


def consume_all_item(region_api: WowApi) -> dict:
    """Yields data for all items.
    
    Args:
        region_api (WowApi): A WowApi object.
    """
    json = region_api.item_search(**{"id": f"({0},)", "orderby": "id", "_pageSize": 1000},
            timeout=(3, 60))
    while json[
        "results"
    ]:  # as long as json is redefined by the loop body and that is visable to the while loop it will work
        for item in json["results"]:
            item_id = item["data"]["id"]
            name = item["data"]["name"]["en_US"]
            yield {'item_id': item_id, 'name':name}
        last_id = json["results"][-1]["data"]["id"]
        json = region_api.item_search(
            **{"id": f"({last_id},)", "orderby": "id", "_pageSize": 1000},
            timeout=(3, 60)
        )

def insert_all_item(region_api: WowApi) -> None:
    """Inserts all items into the Item model.
    
    Args: 
        region_api (WowApi): A WowApi object.
    """
    count = 0
    for data in consume_all_item(region_api):
        record = models.Item(id=data.get('item_id'), name=data.get('name'))
        record.save()

        count += 1
    print('All items inserted')



if __name__ == "__main__":
    us_region_api = WowApi("us", "en_US")
    eu_region_api = WowApi("eu", "en_US")
    kr_region_api = WowApi("kr", "en_US")

    region_api_list = [us_region_api, eu_region_api, kr_region_api]
    #for region_api in region_api_list:
    #    insert_connected_realms_index(region_api)
    #    insert_realm(region_api)


    #I assume the data below is the same in all regions?
    #insert_all_item(us_region_api)
    #insert_profession_index(us_region_api)
    #profession_index_query = models.ProfessionIndex.objects.all()
    #for profession_model in profession_index_query:
    #    insert_profession_tier(us_region_api, profession_model.id)
    #    profession_tier_query = models.ProfessionTier.objects.filter(profession = profession_model)
    #    for profession_tier_model in profession_tier_query:
    #        insert_recipe_category(us_region_api, profession_model.id, profession_tier_model.id)
    #recipe_query = models.Recipe.objects.all()
    #for recipe_model in recipe_query:
    #    insert_recipe(us_region_api, recipe_model.id)

    for region_api in region_api_list:
        #ConnectedRealmIndex before Realm insert
        connected_realms_query = models.ConnectedRealmsIndex.objects.all()
        for realm in connected_realms_query:
            #auction requires: connectedRealmIndex and Items
            insert_auction(region_api, realm.connected_realm_id)

#need to multithread the auction consume and insert so it doesnt take a couple minutes a server
#optimize inserting into db
#try and optimize consuming more
#aiohttp to get all auctions json asap
