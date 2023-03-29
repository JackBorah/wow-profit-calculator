import os
import sys
import csv
import json
from collections.abc import Callable

from dotenv import load_dotenv
from getwowdataasync import *
import django
from django.db.models import QuerySet
from pprint import pprint
from asgiref.sync import async_to_sync, sync_to_async
from calculator.exceptions import MissingItemRecordError
from .create_paths import create_csv_path, create_json_path

load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models


async def insert_all_data():
    wow_api = await WowApi.create('us')

    print("Inserting connected realms index...")
    await insert_all_connected_realm_index_records(wow_api)
    print("Finished inserting connected realms index!")
    print("Inserting regions...")
    await insert_regions()
    print("Finished inserting regions!")
    print("Inserting realms...")
    realms = await insert_all_realms()
    print("Finished inserting realms!")
    print("Inserting modified crafting slots...")
    await insert_modified_crafting_reagent_slot()
    print("Finished inserting modified crafting slots!")
    print("Inserting dragonflight items...")
    await insert_all_dragonflight_items()
    print("Finished inserting dragonflight items!")
    await insert_optional_material_crafting_stats()
    await insert_dragonflight_profession_tree()

async def insert_all_connected_realm_index_records(wow_api: WowApi):
    json_file_name = "connected_realms_index.json"
    json_file_path = create_json_path(json_file_name)
    get_data_func = wow_api.get_connected_realm_index

    await _if_json_file_doesnt_exist_create_one(json_file_path, get_data_func)

    inserted_records =  _insert_all_connected_realm_index_records()
    os.remove(json_file_path)

    return inserted_records

async def _if_json_file_doesnt_exist_create_one(json_file_path, get_data, *params):
    if not os.path.exists(json_file_path):
        if callable(get_data):
            json_to_write = await get_data(*params)
        else:
            json_to_write = get_data
        await _write_json_to_file(json_file_path, json_to_write)

async def _write_json_to_file(path, json_to_write):
    serialized_json = json.dumps(json_to_write)

    with open(path, "w") as json_file:
        json_file.write(serialized_json)

def _insert_all_connected_realm_index_records(json_file_path):
    index = []
    with open(json_file_path) as unloaded_connected_realms_index:
        connected_realms_index = json.load(unloaded_connected_realms_index)
        for connected_realm in connected_realms_index["connected_realms"]:
            connected_realm_id = get_id_from_url(connected_realm["href"])
            record = models.ConnectedRealmsIndex(connected_realm_id=connected_realm_id)
            index.append(record)
    all_inserted_records = models.ConnectedRealmsIndex.objects.bulk_create(index)
    return all_inserted_records

async def insert_all_realms():
    pass

async def insert_modified_crafting_reagent_slot():
    pass

async def insert_all_dragonflight_items():
    pass

async def insert_optional_material_crafting_stats():
    pass

async def insert_dragonflight_profession_tree():
    pass

def get_data_from_csv(csv_path: str, data_extration_func: Callable):
    with open(csv_path, "r", encoding='utf-8-sig') as file:
        opened_csv = csv.reader(file)
        next(opened_csv)
        return data_extration_func(opened_csv)


# json
# all_realms_json_path = r"calculator\wow_json_data\all_realms.json"
# all_dragonflight_items_json_path = r"calculator\wow_json_data\all_dragonflight_items.json"
# profession_tree_json_path = r"calculator\wow_json_data\dragonflight_profession_tree.json"
# dragonflight_profession_tree_json_path = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_json_data\all_dragonflight_items.json"

async def insert_regions(self): # its async since its being called from an async context and django will raise an error otherwise.
    """Inserts all regions into the db."""
    na = "us"
    eu = "eu"
    kr = "kr"
    regions = [na, eu, kr]
    for region in regions:
        await models.Region.objects.acreate(region=region)


# class Realms(Insert):        
#     async def insert_all_realms(self):
#         realms_index = await self.wowapi.get_all_realms()

#         await self._if_json_file_doesnt_exist_create_one(self.all_realms_json_path, realms_index)

#         self._insert_all_realms()
        
#         os.remove(self.all_realms_json_path)

#     def _insert_all_realms(self):
#         """Inserts all realms into the db from the set region."""
#         region = models.Region.objects.get(region=self.wowapi.region)
#         connected_realms_index = models.ConnectedRealmsIndex.objects.all()
#         realms = []

#         with open(self.all_realms_json_path) as unloaded_all_realms:
#             all_realms = json.load(unloaded_all_realms)
#             for connected_realm in all_realms:  # each entry in results is a connected realm cluster
#                 connected_realm_object = connected_realms_index.get(
#                     connected_realm_id=connected_realm["id"]
#                 )
#                 population = connected_realm["population"]["type"]
#                 for realm in connected_realm["realms"]:
#                     realm_id = realm["id"]
#                     name = realm["slug"]
#                     timezone = realm["timezone"]
#                     play_style = realm["type"]["type"]
#                     region = region
#                     record = models.Realm(
#                         connected_realm=connected_realm_object,
#                         population=population,
#                         realm_id=realm_id,
#                         name=name,
#                         region=region,
#                         timezone=timezone,
#                         play_style=play_style,
#                     )
#                     realms.append(record)
#             return models.Realm.objects.bulk_create(realms)

  
# class ProfessionTree(Insert):
#     async def insert_dragonflight_profession_tree(self):
#         profession_tree_callback = self.wowapi.get_professions_tree_by_expansion

#         await self._if_json_file_doesnt_exist_create_one(self.all_dragonflight_items_json_path, profession_tree_callback, 'df')

#         await self._insert_dragonflight_profession_tree()

#         os.remove(self.all_dragonflight_items_json_path)

#     async def _insert_dragonflight_profession_tree(self):
#         profession_index = ProfessionIndex()
#         recipe_category = RecipeCategory()
#         recipes = Recipe()
#         products = []
#         materials = []
#         spells = Spell()
#         crafting_datas = CraftingData()
#         all_modified_crafting_mats = self._create_modified_crafting_material_info()
#         all_crafting_slots = models.OptionalMaterialSlot.objects.all()
#         all_items = models.Item.objects.all()
#         all_product_quantities = self.get_product_quantity()
#         categories_to_ignore = [
#             "Quest Plans", "Recrafting",
#             "Quest Designs", "Quest Techniques",
#             "Quest Recipes", "Quest Patterns",
#             "Quest Techniques", "Quest Formulas",
#             "Quest Schematics", "Recrafting"
#         ]
#         recipes_to_ignore = ["Rummage Through Scrap"]

#         with open(self.dragonflight_profession_tree_json_path, "r") as unloaded_profession_tree:
#             profession_trees = json.load(unloaded_profession_tree)
#             for profession in profession_trees:
#                 profession_record = profession_index._create_profession_index_record(profession)

#                 for category in profession["categories"]:
#                     if category["name"] in categories_to_ignore:
#                         continue
#                     category_record = recipe_category._create_profession_category_record(profession_record, category)

#                     for recipe_dict in category["recipes"]:
#                         recipe_name = recipe_dict["name"]
#                         recipe_id = recipe_dict["id"]
#                         if recipe_name in recipes_to_ignore:
#                             continue
#                         spell_record = await spells.get_spell_record_by_recipe_id(recipe_id)
#                         crafting_data_record = await crafting_datas.get_crafting_data_record_by_spell_id(spell_record.id)

#                         recipe_record = await recipes.create_recipe_record(recipe_dict, category_record, spell_record, crafting_data_record)

#                         product_records = await self._create_product_record(recipe_record, spell_id, all_items, all_product_quantities)

#                         material_records = await self._create_crafting_material_records(recipe_dict, all_modified_crafting_mats, all_crafting_slots, recipe_record)
#                         materials += material_records
                        
#             inserted_professions_records = await profession_index._bulk_insert()
#             inserted_category_records = await recipe_category._bulk_insert_recipe_categories()
#             inserted_recipe_records = await recipe._bulk_insert_recipes()
#             inserted_product_records = await models.Product.objects.abulk_create(products)
#             inserted_material_records = await models.Material.objects.abulk_create(materials)
#             return [
#                 inserted_professions_records, 
#                 inserted_category_records, 
#                 inserted_recipe_records,
#                 inserted_product_records, 
#                 inserted_material_records
#                 ]


# class ProfessionIndex(Insert):
#     all_profession_records = []

#     def _create_profession_index_record(self, profession: dict):
#         profession_record = models.ProfessionIndex(
#             name=profession["name"],
#             id=profession["id"]
#         )
#         self.all_profession_records.append(profession_record)
#         return profession_record

#     async def _bulk_insert(self):
#         return await models.ProfessionIndex.objects.abulk_create(self.all_profession_records)


# class RecipeCategory():
#     all_recipe_categories = []

#     def _create_profession_category_record(self, profession: models.ProfessionIndex, category: dict):
#         recipe_category_record = models.RecipeCategory(
#             name=category["name"],
#             profession=profession
#         )
#         self.all_recipe_categories.append(recipe_category_record)
#         return recipe_category_record

#     async def _bulk_insert_recipe_categories(self):
#         return await models.RecipeCategory.objects.abulk_create(self.all_recipe_categories)


# class Recipe(Insert):
#     all_recipe_records = []

#     def create_recipe_record(self, recipe: dict, category_record: models.RecipeCategory, spell_record: models.Spell, crafting_data_record: models.CraftingData):
#         recipe_record = models.Recipe(
#             id=recipe["name"],
#             name=recipe["id"],
#             recipe_category=category_record,
#             spell=spell_record,
#             crafting_data=crafting_data_record

#         )
#         self.all_recipe_records.append(recipe_record)
#         return recipe_record

#     async def _bulk_insert_recipes(self):
#         return await models.Recipe.objects.abulk_create(self.all_recipe_records)


# class Product(Insert):
#     crafting_data_item_quality_csv_path = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\CraftingDataItemQuality.csv"

#     crafting_data_ids_by_spell_id_json_path = r"calculator\wow_json_data\crafting_data_ids_by_spell_id.json"
#     product_item_ids_by_crafting_data_id_json_path = r"calculator\wow_json_data\product_item_ids_by_crafting_data_id.json"
#     prodict_item_ids_json_path = r"calculator\wow_json_data\product_item_ids_by_crafting_data_id.json"

#     all_product_quantities = 1
#     all_items = models.Item.objects.all()
#     all_product_records = []
#     spells = None

#     async def bulk_insert_all_product_records(self):        
#         inserted_products = await models.Product.objects.abulk_create(self.all_product_records)
#         return inserted_products

#     async def create_product_record(self, recipe_record: models.Recipe, ) -> None:
#         recipe_id = recipe_record.id
#         spell_id = self.spells.get_recipe_spell_id(recipe_id)
#         products = await self._get_product_item_records(spell_id)
#         quantity = self.all_product_quantities[spell_id]
        

#         for product in products:
#             record = models.Product(
#                 item = product,
#                 quantity = quantity,
#                 quality = quality,
#                 recipe = recipe_record
#             )
#             self.all_product_records.append(record)

#     async def _get_product_item_records(self, spell_id):
#         item_ids = await self._get_product_item_id(spell_id)

#         products = []
#         for item_id in item_ids:
#             product = await self.all_items.aget(id=item_id)
#             products.append(product)
#         return products

#     async def _get_product_item_id(self, spell_id: int):
#         """
#         Product item ids come from 3 different csv's. 
#         1. CraftingData.csv
#         2. SpellEffect.csv
#         3. CraftingDataItemQuality.csv
#         """

#         all_crafting_data_ids_callback = self.get_all_crafting_data_ids_by_spell_id
#         all_product_ids_callback = self.get_all_product_ids_by_crafting_data_id
#         all_product_ids_from_spell_effects_csv_callback = self.get_all_product_ids_from_spell_effect_csv

#         await self._if_json_file_doesnt_exist_create_one(self.crafting_data_ids_by_spell_id_json_path, all_crafting_data_ids_callback)
#         await self._if_json_file_doesnt_exist_create_one(self.prodict_item_ids_json_path, all_product_ids_callback)
#         await self._if_json_file_doesnt_exist_create_one(self.crafting_data_ids_by_spell_id_json_path, all_crafting_data_ids_callback)
        
#         crafting_data_id = self.find_value_in_json_file(self.crafting_data_ids_by_spell_id_json_path, spell_id)
#         product_ids = self.find_value_in_json_file(self.prodict_item_ids_json_path, crafting_data_id)
#         self._add_product_ids_from_spell_effects(product_ids)

#         return product_ids

#     async def get_all_product_ids_by_crafting_data_id(self):
#         all_products = {}
#         print(f"1: {type(all_products)}")

#         self._update_product_ids_from_crafting_data_item_quality(all_products)
#         self._update_product_ids_from_crafting_data(all_products)
#         return all_products        

#     def _update_product_ids_from_crafting_data_item_quality(self, all_products: dict):
#         print(f"2: {type(all_products)}")
#         with open(self.crafting_data_item_quality_csv_path, encoding='utf-8-sig') as file:
#             products_csv = csv.reader(file)
#             next(products_csv)
#             for product in products_csv:
#                 crafting_data_id = int(product[2])
#                 crafted_item_id = int(product[1])

#                 self._add_product_id(all_products, crafting_data_id, crafted_item_id)

#     def _update_product_ids_from_crafting_data(self, all_products: dict):
#         with open(self.crafting_data_csv_path, encoding='utf-8-sig') as file:
#             products_csv = csv.reader(file)
#             next(products_csv)
#             for product in products_csv:
#                 crafting_data_id = int(product[0])
#                 crafted_item_id = int(product[3])
                
#                 if crafted_item_id == 0:
#                     continue

#                 self._add_product_id(all_products, crafting_data_id, crafted_item_id)

#     #TODO test this code that was formally apart of get_all_product_ids_by_crafting_data_id
#     def _add_product_id(self, all_products: dict, crafting_data_id: int, crafted_item_id: int):
#         if not all_products.get(crafting_data_id):
#             all_products[crafting_data_id] = [crafted_item_id]
#         elif all_products.get(crafting_data_id):
#             all_products[crafting_data_id].append(crafted_item_id)
#         else:
#             raise BaseException
 
#     def find_value_in_json_file(self, json_file_path, key):
#         with open(json_file_path, "r", encoding='utf-8-sig') as json_file:
#             json_dict = json.load(json_file)
#         return json_dict[str(key)]

#     async def get_all_product_ids_from_spell_effect_csv(self):
#         with open(self.spell_effect_csv_path, encoding='utf-8-sig') as file:
#             spell_effects_csv = csv.reader(file)
#             next(spell_effects_csv)
#             for spell in spell_effects_csv:
#                 spell_id = int(spell[35])
#                 crafted_item_id = int(spell[11])
                
#                 if crafted_item_id == 0:
#                     continue

#                 self._add_product_id(all_products, crafting_data_id, crafted_item_id)

#     def get_product_quantity(self) -> dict:
#         product_quantites = {}
#         with open(self.spell_effect_csv_path, encoding='utf-8-sig') as file:
#             recipe_spells_csv = csv.reader(file)
#             next(recipe_spells_csv)
#             for spell in recipe_spells_csv:
#                 product_quantity = float(spell[23])
#                 spell_id = int(spell[35])
#                 product_quantites.update({spell_id:product_quantity})
#         return product_quantites      


# class Spell(Insert):
#     spell_name_csv_path = r"calculator\wow_csv_data\SpellName.csv"

#     # all_spells_by_spell_name_json_path = r"calculator\wow_json_data\all_spells_by_spell_name.json"
#     # all_spells_by_recipe_id_json_path = r"calculator\wow_json_data\all_spells_by_recipe_id.json"
#     # all_crafting_data_ids_by_spell_id_json_path = r"calculator\wow_json_data\all_crafting_data_ids_by_spell_id.json"

#     all_spells_by_spell_name = {}
#     all_spells_by_recipe_id = {}
#     all_crafting_data_ids_by_spell_id = {}

#     # def get_recipe_spell_id(self, spell_name: str) -> int:
#     #     if self.all_spells_by_recipe_id:
#     #         self._if_json_file_doesnt_exist_create_one()
#     #         self._set_all_spell_ids_by_spell_name()

#     #     return self.all_spells_by_recipe_id[spell_name]

#     def get_spell_record_by_recipe_id(self, recipe_id: int) -> models.Spell:
#         if not models.Spell.objects.all():
#             self._bulk_insert_all_spell_records()

#         if not self.all_spells_by_recipe_id:
#             self._create_dict_of_spell_records_by_recipe_id()

#         return self.all_spells_by_recipe_id[recipe_id]

#     async def _bulk_insert_all_spell_records(self) -> None:
#         spell_records = []
#         with open(self.spell_name_csv_path, encoding='utf-8-sig') as file:
#             spell_name_csv = csv.reader(file)
#             next(spell_name_csv)
#             for spell in spell_name_csv:
#                 spell_id = int(spell[0])
#                 spell_name = spell[1]
#                 spell_record = models.Spell(
#                     id=spell_id,
#                     name=spell_name
#                 )
#                 spell_records.append(spell_record)
#                 # is_spell_in_spells = spells.get(spell_name)
#                 # if is_spell_in_spells and type(is_spell_in_spells) != list:
#                 #     temp = spells[spell_name]
#                 #     spells[spell_name] = [temp]
#                 #     spells[spell_name].append(spell_id)
#                 # elif type(is_spell_in_spells) == list:
#                 #     spells[spell_name].append(spell_id)
#                 # else:
#                 #     spells[spell_name] = spell_id
#         return await models.Spell.objects.abulk_create(spell_records)

#     def _create_dict_of_spell_records_by_recipe_id(self) -> dict[int: models.Spell]:
#         with open(self.skill_line_ability_csv_path, encoding='utf-8-sig') as file:
#             skill_line_ability_csv = csv.reader(file)
#             next(skill_line_ability_csv)
#             for recipe in skill_line_ability_csv:
#                 temp_recipe_id = int(recipe[3])
#                 spell_id = int(recipe[5])
#                 spell_record = models.Spell.objects.get(id=spell_id)
                
#                 self.all_spells_by_recipe_id[temp_recipe_id] = spell_record


# class CraftingData():
#     crafting_data_csv_path = r"calculator\wow_csv_data\CraftingData.csv"

#     all_crafting_data_ids_by_spell_id = {}

#     async def get_crafting_data_record_by_spell_id(self, spell_id: int) -> models.CraftingData:
#         if not models.CraftingData.objects.all():
#             await self._bulk_insert_all_crafting_data_records()

#         if not self.all_crafting_data_ids_by_spell_id:
#             self._create_dict_of_crafting_data_ids_by_spell_id()

#         return self.all_crafting_data_ids_by_spell_id[spell_id]

#     async def _bulk_insert_all_crafting_data_records(self) -> None:
#         crafting_data_records = []
#         with open(self.crafting_data_csv_path, "r", encoding='utf-8-sig') as file:
#             crafting_data_csv = csv.reader(file)
#             next(crafting_data_csv)
#             for line in crafting_data_csv:
#                 crafting_data_id = int(line[0])
#                 crafting_data_record = CraftingData(
#                     id = crafting_data_id
#                 )
#                 crafting_data_records.append(crafting_data_record)
#         return await models.CraftingData.objects.abulk_create(crafting_data_records)

#     def _create_dict_of_crafting_data_ids_by_spell_id(self) -> None:
#         crafting_data_ids = {}
#         with open(self.spell_effect_csv_path, "r", encoding='utf-8-sig') as file:
#             spell_effect_csv = csv.reader(file)
#             next(spell_effect_csv)
#             for line in spell_effect_csv:
#                 crafting_data_id = int(line[25])
#                 crafting_data_record = models.CraftingData.objects.get(crafting_data_id)
#                 spell_id = int(line[35])

#                 crafting_data_ids[spell_id] = crafting_data_record
#         self.all_crafting_data_ids_by_spell_id = crafting_data_ids


# class CraftingQuality():
#     crafting_quality_csv_path = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\CraftingQuality.csv"

#     async def bulk_insert_all_spell_records(self) -> None:
#         crafting_quality_records = []
#         with open(self.crafting_quality_csv_path, "r", encoding='utf-8-sig') as file:
#             crafting_data_csv = csv.reader(file)
#             next(crafting_data_csv)
#             for line in crafting_data_csv:
#                 crafting_quality_id = int(line[0])
#                 crafting_quality_tier = int(line[1])
#                 crafting_quality_record = CraftingData(
#                     id = crafting_quality_id,
#                     quality_tier = crafting_quality_tier
#                 )
#                 crafting_quality_records.append(crafting_quality_record)
#         return await models.CraftingQuality.objects.abulk_create(crafting_quality_records)


# class Material(Insert):
#     def _create_modified_crafting_material_record(self, material: dict, recipe: models.Recipe, quantities: dict, slot: models.OptionalMaterialSlot):
#         display_order = material["display_order"]
#         quantity = quantities[display_order]
#         recraft_quantity = 0 # TODO get the correct recraft values
#         optional_material_slot = slot
#         name = material["slot_type"]["name"]

#         return models.Material(
#             name=name,
#             quantity=quantity,
#             recraft_quantity=recraft_quantity,
#             optional_material_slot=optional_material_slot,
#             recipe=recipe,
#             display_order=display_order,
#         ) 

#     def _create_modified_crafting_material_info(self) -> dict:
#         """ 
#         {
#             spell_id : {
#                 modified_crafting_slot : {
#                     display_order:1, 
#                     quantity:1,
#                     recraft_quantity:1
#                 },
#                 modified_craafting_slot: {...}
#             }
#         }
#         """
#         materials = {}
#         with open(self.modified_crafting_spells_csv_path, encoding='utf-8-sig') as file:
#             spell_slots_csv = csv.reader(file)
#             next(spell_slots_csv)
#             for material in spell_slots_csv:
#                 recipe_spell_id = int(material[1])
#                 modified_crafting_slot = int(material[3])
        
#                 if recipe_spell_id not in materials:
#                     materials[recipe_spell_id] = {}
#                     materials[recipe_spell_id].update({
#                         modified_crafting_slot : {
#                             "display_order" : int(material[2]),
#                             "quantity" : int(material[5]),
#                             "recraft_quantity" : int(material[6])
#                         }
#                     })
#                 else:
#                     materials[recipe_spell_id].update({
#                         modified_crafting_slot : {
#                             "display_order" : int(material[2]),
#                             "quantity" : int(material[5]),
#                             "recraft_quantity" : int(material[6])
#                         }
#                     })
#         return materials

#     def _create_material_record(self, material: dict, recipe: models.Recipe):
#         name = material["reagent"]["name"]
#         quantity = material["quantity"]
#         recraft_quantity = None
#         optional_material_slot = None
#         display_order = None

#         return models.Material(
#             name=name,
#             quantity=quantity,
#             recraft_quantity=recraft_quantity,
#             optional_material_slot=optional_material_slot,
#             recipe=recipe,
#             display_order=display_order,
#         )        

#     async def _create_crafting_material_records(self, recipe: dict, all_modified_crafting_mats: dict, all_crafting_slots: QuerySet, recipe_record: models.Recipe) -> list[models.Material]:
#         materials = []
#         spell_id = await self.get_recipe_spell_id_by_recipe_id(recipe["id"])
#         combined_material_list = self._get_list_of_recipe_materials(recipe)
#         quantities = self._get_material_quantities(spell_id, combined_material_list, all_modified_crafting_mats)

#         for material in combined_material_list:
#             if material.get("slot_type"):
#                 slot = await all_crafting_slots.aget(id=material["slot_type"]["id"])
#                 material_record = self._create_modified_crafting_material_record(material, recipe_record, quantities, slot)
#             else:
#                 material_record = self._create_material_record(material, recipe_record)
#             materials.append(material_record)
#         return materials

#     def _get_list_of_recipe_materials(self, recipe: dict) -> list[dict]:
#         if recipe.get("reagents") and recipe.get("modified_crafting_slots"):
#             recipe_material_list = recipe["reagents"] + recipe["modified_crafting_slots"]
#         elif not recipe.get("modified_crafting_slots"):
#             recipe_material_list = recipe["reagents"]
#         elif not recipe.get("reagents"):
#             recipe_material_list = recipe["modified_crafting_slots"]
#         else:
#             raise BaseException

#         return recipe_material_list

#     def _get_material_quantities(self, spell_id: int, recipe_material_list: list, all_modified_crafting_mats: dict):
#         quantities = []
#         for material in recipe_material_list:
#             if material.get("slot_type"):
#                 modified_crafting_slot = material["slot_type"]["id"]
#                 quantities.append(all_modified_crafting_mats[spell_id][modified_crafting_slot]["quantity"])
#             else:
#                 quantities.append(material["quantity"])

#         return quantities


# class ModifiedCraftingCategory(Insert):
#     modified_crafting_category_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingCategory.csv"

#     def bulk_insert_all_modified_crafting_categories(self):
#         records = self.get_data_from_csv(
#             self.modified_crafting_category_csv,
#             self.extract_all_modified_crafting_category_records
#         )
#         return models.ModifiedCraftingCategory.objects.bulk_create(records)

#     def extract_all_modified_crafting_category_records(
#         self, 
#         opened_csv
#     ) -> dict:
#         categories = []
#         for line in opened_csv:
#             category_id = int(line[0])
#             name = int(line[1])
#             description = int(line[2])
#             category_record = models.ModifiedCraftingCategory(
#                 id=category_id,
#                 name=name,
#                 description=description
#             )
#             categories.append(category_record)
#         return categories


# class ModifiedCraftingReagentItem(Insert):
#     modified_crafting_reagent_item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingReagentItem.csv"

#     def bulk_insert_all_modified_crafting_reagent_items(self):
#         records = self.get_data_from_csv(
#             self.modified_crafting_reagent_item_csv,
#             self.extract_all_modified_crafting_reagent_item_records
#         )
#         return models.ModifiedCraftingReagentItem.objects.bulk_create(records)
    
#     def extract_all_modified_crafting_reagent_item_records(
#             self,
#             opened_csv
#         ):
#         MCR_item_records = []
#         all_modified_crafting_categories = models.ModifiedCraftingCategory.objects.all()
#         for line in opened_csv:
#             MCR_item_id = int(line[0])
#             description = line[1]
#             MCR_category_id = int(line[2])
#             category_record = all_modified_crafting_categories.get(id=MCR_category_id)
#             MCR_item_record = models.ModifiedCraftingReagentItem(
#                 id=MCR_item_id,
#                 description=description,
#                 modified_crafting_category=category_record
#             )
#             MCR_item_records.append(MCR_item_record)
#         return MCR_item_records


# class ModifiedCraftingReagentSlot(Insert):
#     modified_crafting_reagent_slot_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingReagentSlot.csv"
#     MCRslotXMCRcategory_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\MCRSlotXMCRCategory.csv"

#     def bulk_insert_all_modified_crafting_reagent_slot(self):
#         records = self.get_data_from_csv(
#             self.modified_crafting_reagent_slot_csv,
#             self.extract_all_modified_crafting_reagent_slot_records
#         )
#         inserted_records = models.ModifiedCraftingReagentSlot.objects.bulk_create(records)
#         self.fill_in_many_to_many_rel_with_MCcategory()
#         return inserted_records

#     def extract_all_modified_crafting_reagent_slot_records(
#         self, 
#         opened_csv
#     ) -> dict:
#         slots = []
#         for line in opened_csv:
#             name = int(line[0])
#             slot_id = int(line[1])
#             category_record = models.ModifiedCraftingReagentSlot(
#                 id=slot_id,
#                 name=name,
#             )
#             slots.append(category_record)
#         return slots

#     def fill_in_many_to_many_rel_with_MCcategory(
#             self
#         ):
#         self.get_data_from_csv(
#             self.MCRslotXMCRcategory_csv,
#             self._fill_in_many_to_many_rel_with_MCcategory
#         )

#     def _fill_in_many_to_many_rel_with_MCcategory(
#             self,
#             opened_csv
#         ):
#         all_categories = models.ModifiedCraftingCategory.objects.all()
#         all_slots = models.ModifiedCraftingReagentSlot.objects.all()
#         for line in opened_csv:
#             category_id = line[1]
#             slot_id = line[3]

#             category_record = all_categories.get(id=category_id)
#             slot_record = all_slots.get(id=slot_id)

#             slot_record.modified_crafting_category.add(category_record)

#     async def insert_modified_crafting_reagent_slot(self):
#         json = await self.wowapi.get_modified_crafting_reagent_slot_type_index()
#         slots = []
#         for slot in json["slot_types"]: # a single slot is missing a name :)
#             name = slot.get("name")
#             id = slot["id"]
#             slots.append(models.OptionalMaterialSlot(name=name, id=id))
#         return await models.OptionalMaterialSlot.objects.abulk_create(slots)


# class Item(Insert):
#     item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\Item.csv"
#     item_sparse_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ItemSparse.csv"
#     modified_crafting_item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingItem.csv"

#     MC_categories_id_by_MC_reagent_item_id = {}
#     all_items_records = []

#     def insert_all_items(self):
#         all_item_data_without_names = self.get_data_from_csv(
#             self.item_csv, 
#             self.extract_data_from_item_csv
#         )
#         item_names_by_id = self.get_data_from_csv(
#             self,
#             self.item_sparse_csv,
#             self.extract_data_from_itemSparse_csv
#         )
#         all_qualities = models.CraftingQuality.objects.all()
#         all_MCR_items = models.ModifiedCraftingReagentItem.objects.all()
#         item_records = []
#         for item_dict in all_item_data_without_names:
#             item_id = item_dict["id"]
#             modified_crafting_reagent_item_id = item_dict["modified_crafting_reagent_item_id"]
#             MCR_item_record = all_MCR_items.get(id=modified_crafting_reagent_item_id)
#             name = item_names_by_id["item_id"]
#             crafting_quality_id = item_dict["crafting_quality_id"]
#             crafting_quality_record = all_qualities.get(id=crafting_quality_id)
#             binding = item_dict["binding"]

#             item_records.append(self.create_item_record(
#                 item_id, crafting_quality_record,
#                 name, binding, MCR_item_record
#             ))
#             models.Item.objects.bulk_create(item_records)

#     def extract_data_from_item_csv(self, opened_csv) -> dict:
#         items = []
#         for line in opened_csv:
#             item_id = int(line[0])
#             modified_crafting_reagent_item_id = int(line[10])
#             binding = line[4]
#             crafting_quality_id = int(line[11])

#             items.append(
#                 {
#                     "id":item_id,
#                     "modified_crafting_reagent_item_id":modified_crafting_reagent_item_id,
#                     "crafting_quality_id":crafting_quality_id,
#                     "binding":binding
#                 }
#             )
#         return items
    
#     def extract_data_from_itemSparse_csv(self, opened_csv):
#         items = {}
#         for line in opened_csv:
#             item_id = int(line[0])
#             name = line[6]
#             items[item_id] = name
#         return items

#     def extract_data_from_modified_crafting_reagent_item_csv(
#             self,
#             opened_csv
#     ) -> dict:
#         modified_crafting_category_by_modified_crafting_reagent_item_id = {}
#         for line in opened_csv:
#             modified_crafting_reagent_id = int(line[0])
#             modified_crafting_category_item_id = int(line[2])
            
#             modified_crafting_category_by_modified_crafting_reagent_item_id[item_id] = {
#                 "modified_crafting_reagent_item_id":modified_crafting_reagent_id,
#                 "modified_crafting_category_id":modified_crafting_category_item_id, 
#             }
#         return modified_crafting_category_by_modified_crafting_reagent_item_id

#     def extract_data_from_modified_crafting_item_csv(
#             self,
#             opened_csv
#     ) -> dict:
#         modified_crafting_item_data = {}
#         for line in opened_csv:
#             item_id = int(line[0])
#             modified_crafting_reagent_item_id = int(line[1])
#             modified_crafting_item_data[item_id] = {
#                 "id":item_id,
#                 "modified_crafting_reagent_item_id" : modified_crafting_reagent_item_id, 
#             }
#         return modified_crafting_item_data

#     def create_item_record(
#             self, item_id: int, quality: models.CraftingQuality,
#             name: str, binding: str, 
#             MCR_item: models.OptionalMaterialSlot
#         ):
#         item_record = Item(
#             id=item_id,
#             quality = quality,
#             name=name,
#             binding=binding,
#             MCR_item=MCR_item
#         )
#         self.all_items_records.append(item_record)

#     def set_MC_categories_id_by_MC_reagent_item_id(self):
#         MC_categories_id_by_MC_reagent_item_id = {}
#         with open(self.modified_crafting_reagent_item_csv, "r", encoding='utf-8-sig') as file:
#             modified_crafting_reagent_item_csv = csv.reader(file)
#             next(modified_crafting_reagent_item_csv)
#             for line in modified_crafting_reagent_item_csv:
#                 modified_crafting_reagent_item_id = int(line[0])
#                 modified_crafting_category_id = int(line[2])

#                 MC_categories_id_by_MC_reagent_item_id[modified_crafting_reagent_item_id] = modified_crafting_category_id
#         self.MC_categories_id_by_MC_reagent_item_id = MC_categories_id_by_MC_reagent_item_id

#     async def insert_all_dragonflight_items_from_api(self):
#         dragonflight_items = await self.wowapi.get_items_by_expansion("df")

#         await self._if_json_file_doesnt_exist_create_one(self.all_dragonflight_items_json_path, dragonflight_items)

#         self._insert_all_dragonflight_items()

#         os.remove(self.all_dragonflight_items_json_path)
  
#     def _insert_all_dragonflight_items_from_api(self):
#         items = []
#         all_qualities = self.get_all_item_crafting_qualities()
#         all_optional_material_slots = models.OptionalMaterialSlot.objects.all()

#         with open(self.all_dragonflight_items_json_path) as unloaded_dragonflight_items:
#             all_dragonflight_items = json.load(unloaded_dragonflight_items)
#             for item in all_dragonflight_items:            
#                 if item.get("modified_crafting"):
#                     quality = all_qualities[item["id"]]
#                     optional_material_slot_id = item["modified_crafting"]["id"]
#                     optional_material_slot, _ = all_optional_material_slots.get_or_create(id=optional_material_slot_id)
#                 else:
#                     quality = None
#                     optional_material_slot = None

#                 if item.get("preview_item"):
#                     if item.get("preview_item").get("binding"):
#                         binding = item["preview_item"]["binding"]["name"]
#                     else:
#                         binding = None
#                 else:
#                     binding = None
            
#                 item = models.Item(
#                     id=item["id"],
#                     name=item["name"],
#                     vendor_buy_price = item["purchase_price"],
#                     vendor_sell_price = item["sell_price"],
#                     vendor_buy_quantity = item["purchase_quantity"],
#                     quality = quality,
#                     binding = binding,
#                     optional_material_slot = optional_material_slot
#                 )
#                 items.append(item)
#             return models.Item.objects.bulk_create(items)

#     def get_all_item_crafting_qualities(self) -> dict:
#         modified_crafting_items = {}
#         with open(self.modified_crafting_qualities_csv_path, encoding='utf-8-sig') as file:
#             modified_crafting_item = csv.reader(file)
#             next(modified_crafting_item)
#             for modified_crafting_item in modified_crafting_item:
#                 item_id = int(modified_crafting_item[0])
#                 quality = int(modified_crafting_item[2])
#                 modified_crafting_items[item_id] = quality
#         return modified_crafting_items


# class CraftingStats(Insert):
#     optional_material_crafting_stats_csv_path = r"calculator\wow_csv_data\wowprofitcalculator - OptionalMaterialCraftingStats.csv"

#     async def insert_optional_material_crafting_stats(self):
#         crafting_stats = []
#         items = models.Item.objects.all()
#         with open(self.optional_material_crafting_stats_csv_path, encoding='utf-8-sig') as file:
#             crafting_stats_csv = csv.reader(file)
#             next(crafting_stats_csv)
#             for single_items_crafting_stats in crafting_stats_csv:
#                 crafting_stats.append(await self._create_crafting_stat_record(single_items_crafting_stats, items))
#         return await models.CraftingStats.objects.abulk_create(crafting_stats)

#     async def _create_crafting_stat_record(self, single_items_crafting_stats, items):
#         name = single_items_crafting_stats[0]
#         quality = single_items_crafting_stats[1]
#         items = items.filter(name=name)

#         if await sync_to_async(len)(items) > 1: # some items have multiple qualities and need further filtering
#             item = await items.aget(quality=quality)
#         elif await sync_to_async(len)(items) == 1: # item has only one quality return it
#             item = await items.aget() 
#         else:
#             raise MissingItemRecordError(f"Unable to find item record for {name}\nfrom existing items records: {items}")
#         return models.CraftingStats(
#             item = item,
#             inspiration = self.convert_to_int_or_none(single_items_crafting_stats[2]),
#             skill_from_inspiration = self.convert_to_float_or_none(single_items_crafting_stats[3]),
#             multicraft = self.convert_to_int_or_none(single_items_crafting_stats[4]),
#             resourcefulness = self.convert_to_int_or_none(single_items_crafting_stats[5]),
#             increase_material_from_resourcefulness = self.convert_to_float_or_none(single_items_crafting_stats[6]),
#             skill = self.convert_to_int_or_none(single_items_crafting_stats[7]),
#             crafting_speed = self.convert_to_float_or_none(single_items_crafting_stats[8]),
#         )


# def convert_to_int_or_none(number: str):
#     try:
#         return int(number)
#     except ValueError:
#         return None

# def convert_to_float_or_none(number: str):
#     try:
#         return float(number)
#     except ValueError:
#         return None     
