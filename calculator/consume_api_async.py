import os
import sys
import asyncio
from dotenv import load_dotenv
from getwowdataasync import *
import django
from django.db.models import Avg, Sum
from pprint import pprint
from asgiref.sync import async_to_sync, sync_to_async


load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models


### improvements from sync version
# combining consume & insert into a single function. Its simpiler, easier to read, and testing consume should be handled by the library not the user
# instead of independent functions extend WowApi and make insert methods. I had to pass the API to every single funcion last time. It seems unessicary if all functions need the same data make it a class.


class Insert(WowApi):
    @classmethod
    async def create(cls, region: str):
        wowapi = await super().create(region)
        self = Insert()
        self.__dict__ = wowapi.__dict__.copy()
        return self

    def insert_all_realms(self):
        """Inserts all realms into the db from the set region."""
        json = async_to_sync(self.connected_realm_search)()
        regions = models.Region.objects.all()
        connected_realms = models.ConnectedRealmsIndex.objects.all()

        for connected_realm in json[
            "results"
        ]:  # each entry in results is a connected realm cluster
            connected_realm_obj = connected_realms.get(
                connected_realm_id=connected_realm["data"]["id"]
            )
            population = connected_realm["data"]["population"]["type"]
            for realm in connected_realm["data"]["realms"]:
                realm_id = realm["id"]
                name = realm["name"]["en_US"]
                timezone = realm["timezone"]
                play_style = realm["type"]["type"]
                region = regions.get(region=realm["region"]["name"]["en_US"])
                record = models.Realm(
                    connected_realm=connected_realm_obj,
                    population=population,
                    realm_id=realm_id,
                    name=name,
                    region=region,
                    timezone=timezone,
                    play_style=play_style,
                )
                record.save()


    def insert_connected_realms_index(self):
        """Inserts connected realm ids into the db."""
        json = async_to_sync(self.get_connected_realm_index)()

        for connected_realm in json["connected_realms"]:
            connected_realm_id = get_id_from_url(connected_realm['href'])
            record = models.ConnectedRealmsIndex(connected_realm_id=connected_realm_id)
            record.save()


    def insert_auctions(self, connected_realm_id: int):
        """Inserts all auctions from a connected realm into the db."""
        connected_realm_obj = models.ConnectedRealmsIndex.objects.get(
            connected_realm_id=connected_realm_id
        )
        json = async_to_sync(self.get_auctions)(connected_realm_id)
        all_items = models.Item.objects.all()
        all_bonuses = models.ItemBonus.objects.all()
        auction_objects = []  # contains auctions for bulk create
        bonus_objects = []  # contains lists of an auctions bonus objects for insert
        timestamp = convert_to_datetime(json["Date"])

        for auction in json["auctions"]:
            item, created = all_items.get_or_create(id=auction.get("item").get("id"))

            auction_obj = models.Auction(
                auction_id=auction.get("id"),
                buyout=auction.get("buyout"),
                bid=auction.get("bid"),
                unit_price=auction.get("unit_price"),
                quantity=auction.get("quantity"),
                time_left=auction.get("time_left"),
                connected_realm=connected_realm_obj,
                item=item,
                pet_level=auction.get("item").get("pet_level"),
                timestamp=timestamp,
            )

            auction_objects.append(auction_obj)

            if auction.get("item").get("bonus_lists"):
                bonuses = []
                for bonus_id in auction.get("item").get("bonus_lists"):
                    bonus_obj, created = all_bonuses.get_or_create(id=bonus_id)
                    bonuses.append(bonus_obj)
                bonus_objects.append(bonuses)

            else:
                bonus_objects.append(None)

        models.Auction.objects.bulk_create(auction_objects)

        for auction in auction_objects:
            auction.bonuses.add(*bonuses)


    def insert_profession_index(self):
        """Inserts all professions into the db."""
        json = async_to_sync(self.get_profession_index)()
        for profession in json["professions"]:
            id = profession["id"]
            name = profession["name"]
            record = models.ProfessionIndex(name=name, id=id)
            record.save()


    def insert_profession_tier(self, profession_id: int):
        """Inserts all profession tiers for a profession into the db."""
        json = async_to_sync(self.get_profession_tiers)(profession_id)
        profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
        if json.get("skill_tiers"):
            for tier in json["skill_tiers"]:
                name = tier["name"]
                id = tier["id"]
                record = models.ProfessionTier(id=id, name=name, profession=profession_obj)
                record.save()

    def insert_recipe_category(self, 
        profession_id: int, profession_tier_id: int
    ) -> None:
        """Inserts data from recipe category into that model and the name and id into the recipe model.

        Args:
            region_api (WowApi): A WowApi object.
            profession_id (int): A professions id. Get from profession index.
            profession_tier_id (int): A profession tier's id. Get from profession tiers.
        """
        json = async_to_sync(self.get_profession_tier_categories)(profession_id, profession_tier_id)
        profession_tier_obj = models.ProfessionTier.objects.get(id=profession_tier_id)

        recipes = []

        if json.get("categories"):
            for category in json["categories"]:
                category_name = category.get("name")
                category_record, created = models.RecipeCategory.objects.get_or_create(
                    name=category_name,
                    profession_tier=profession_tier_obj,
                )
                if created:
                    category_record.save()
                for recipe in category.get("recipes"):
                    recipe_name = recipe.get("name")
                    recipe_id = recipe.get("id")
                    recipe_record = models.Recipe(
                        id=recipe_id,
                        name=recipe_name,
                        recipe_category=category_record,
                    )
                    recipes.append(recipe_record)
        else:
            category_name = json["name"]
            category_record, created = models.RecipeCategory.objects.get_or_create(
                name=category_name,
                profession_tier=profession_tier_obj,
            )
            if created:
                category_record.save()

        models.Recipe.objects.bulk_create(recipes)


    def insert_recipe(self, recipe_id: int):
        """Inserts a recipe along with its items, products, and materials into the db."""
        json = async_to_sync(self.get_recipe)(recipe_id)
        # recipe id, recipe name, product foreignKey, material(s), material quantity
        recipe_id = json["id"]
        recipe_name = json["name"]

        if json.get("crafted_quantity"):
            if json.get("crafted_quantity").get("value"):
                product_quantity = (json.get("crafted_quantity")["value"],)
            else:
                min_quantity = json.get("crafted_quantity")["minimum"]
                max_quantity = json.get("crafted_quantity")["maximum"]
                product_quantity = (min_quantity, max_quantity)
        else:
            product_quantity = (0,)
        product_list = []
        if json.get("crafted_item"):
            product_id = json.get("crafted_item")["id"]
            product_name = json.get("crafted_item")["name"]
            product_item_obj, created = models.Item.objects.get_or_create(
                id=product_id, name=product_name
            )
            product_list.append(product_item_obj)
        if json.get("alliance_crafted_item"):
            alliance_product_id = json.get("alliance_crafted_item")["id"]
            alliance_product_name = json.get("alliance_crafted_item")["name"]
            alliance_product_item_obj, created = models.Item.objects.get_or_create(
                id=alliance_product_id, name=alliance_product_name
            )
            product_list.append(alliance_product_item_obj)
        if json.get("horde_crafted_item"):
            horde_product_id = json.get("horde_crafted_item")["id"]
            horde_product_name = json.get("horde_crafted_item")["name"]
            horde_product_item_obj, created = models.Item.objects.get_or_create(
                id=horde_product_id, name=horde_product_name
            )
            product_list.append(horde_product_item_obj)
        materials_list = []
        if json.get("reagents"):
            for mat in json.get("reagents"):
                mat_id = mat["reagent"]["id"]
                mat_name = mat["reagent"]["name"]
                mat_item_obj, created = models.Item.objects.get_or_create(
                    id=mat_id, name=mat_name
                )
                mat_item_quantity = mat.get("quantity")
                mat_obj, created = models.Material.objects.get_or_create(
                    item=mat_item_obj, quantity=mat_item_quantity
                )
                materials_list.append(mat_obj)
        recipe = models.Recipe.objects.get(id=recipe_id)
        for product_item_obj in product_list:
            if product_item_obj:  # obj or None
                if len(product_quantity) == 1:
                    min_quantity = product_quantity[0]
                    max_quantity = product_quantity[0]
                else:
                    min_quantity = product_quantity[0]
                    max_quantity = product_quantity[1]
                product_record = models.Product(
                    recipe=recipe,
                    item=product_item_obj,
                    min_quantity=min_quantity,
                    max_quantity=max_quantity,
                )
                product_record.save()
        for material in materials_list:
            recipe.mats.add(material)
            recipe.save()

    #TODO
    def insert_item(self):
        """Inserts an item into the db."""
        pass

    def insert_all_item(self):
        """Inserts all items into the db."""
        json = async_to_sync(self.item_search)(
            **{"id": f"({0},)", "orderby": "id", "_pageSize": 1000}
        )
        items = []
        for item in json["items"]:
            id = item['id']
            vendor_buy_price = item['purchase_price']
            vendor_sell_price = item['sell_price']
            vendor_buy_quantity = item['purchase_quantity']
            quality = item['quality']['type']
            name = item['name']
            if item.get('binding'):
                binding = item['binding']['type']
            else:
                binding = None
            item_record = models.Item(
                id=id, vendor_buy_price=vendor_buy_price, 
                vendor_sell_price=vendor_sell_price, 
                vendor_buy_quantity=vendor_buy_quantity, 
                quality=quality, name=name, binding=binding
            )
            items.append(item_record)

            last_id = json["items"][-1]["id"]
            json = async_to_sync(self.item_search)(
                **{"id": f"({last_id},)", "orderby": "id", "_pageSize": 1000},
            )
        models.Item.objects.bulk_create(items)


    def insert_regions(self):
        """Inserts all regions into the db."""
        na = 'North America'
        eu = 'Europe'
        kr = 'Korea'
        regions = [na, eu, kr]
        for region in regions:
            record = models.Region.objects.create(region=region)
            record.save()


    def insert_regional_data(self):
        """Inserts data specific to a region, except for auctions, into the db."""
        self.insert_regions()
        self.insert_connected_realms_index()
        self.insert_all_realms()

    def insert_static_data(self):
        """Inserts data common to all regions like professions, items, ... into the db. """
        self.insert_all_item()
        self.insert_profession_index()
        profession_index_query = models.ProfessionIndex.objects.all()
        for profession_model in profession_index_query:
            self.insert_profession_tier(profession_model.id)
        profession_tier_query = models.ProfessionTier.objects.filter(profession = profession_model)
        for profession_tier_model in profession_tier_query:
            self.insert_recipe_category(profession_model.id, profession_tier_model.id)
        recipe_query = models.Recipe.objects.all()
        for recipe_model in recipe_query:
            self.insert_recipe(recipe_model.id)


def calculate_market_price(item_id: int):
    """Calculates the market price of an item.
    
    Args:
        item_id (int): The id of an item.
    """
    #excludes records with no buyout
    auctions_with_buyout = models.Auction.objects.filter(item_id=item_id).exclude(buyout=None)
    #excludes records with no unit_price
    auctions_with_unit_price = models.Auction.objects.filter(item_id=item_id).exclude(unit_price=None)

    if auctions_with_buyout.count() != 0:
        quantity_sum = auctions_with_buyout.aggregate(Sum('quantity'))['quantity__sum']
        ordered_buyouts = auctions_with_buyout.values_list('buyout', flat=True).order_by('buyout')
        bottom_10percent = round(quantity_sum * .1)
        market_price = ordered_buyouts.filter(buyout__lt=ordered_buyouts[bottom_10percent]).aggregate(Avg('buyout'))
        return market_price
    elif auctions_with_unit_price.count() != 0:
        quantity_sum = auctions_with_unit_price.aggregate(Sum('quantity'))['quantity__sum']
        ordered_buyouts = auctions_with_unit_price.values_list('unit_price', flat=True).order_by('unit_price')
        bottom_10percent = round(quantity_sum * .1)
        market_price = ordered_buyouts.filter(unit_price__lt=ordered_buyouts[bottom_10percent]).aggregate(Avg('unit_price'))
        return market_price

def calculate_avg_region_market_price(item_id: int, connected_realm_id: int):
    """Calcluate the avg of an items market price in a region.
    
    Args:
        item_id (int): The id of an item.
        connected_realm_id (int): The id of a connected realm.
    """
    pass


def calculate_median_region_market_price(item_id: int, connected_realm_id: int):
    """Calcluate the median of an items market price in a region.
    
    Args:
        item_id (int): The id of an item.
        connected_realm_id (int): The id of a connected realm.
    """
    pass


def calculate_recipe_profit(recipe_id: int, connected_realm_id: int):
    """Calcluate the profit from a recipe.
    
    Args:
        item_id (int): The id of an item.
        connected_realm_id (int): The id of a connected realm.
    """
    pass

def calculate_region_recipe_profit(recipe_id: int):
    """Calcluate the profit from a recipe.
    
    Args:
        item_id (int): The id of an item.
    """
    pass


#TODO
# New models have to be inserted
# How will RecipeProfit, PriceData, and the new item fields be inserted?
# Profits will have to be calculated each hour too.
# There are a couple thousand recipes per server and dozens of connected realms to calculate for.
# Thats a lot of dynos calculating and inserting auctions each hour.

#async def main():


if __name__ == "__main__":
    pass