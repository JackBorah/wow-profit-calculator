import os
import sys
from typing import List, Dict

from asgiref.sync import sync_to_async, async_to_sync
from dotenv import load_dotenv
from getwowdataasync import *
import django
from calculator.utils import *
from calculator.exceptions import *
from calculator.utils import convert_to_float_or_none, convert_to_int_or_none
load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

from calculator import models

connected_realm_index_file_name = "connected_realms_index.json"
realms_file_name = "relams.json"
spell_name_csv_name = "SpellName.csv"
skill_line_ability_csv_name = "SkillLineAbility.csv"
crafting_data_csv_name = "CraftingData.csv"
spell_effect_csv_name = "SpellEffect.csv"
item_csv_name = "Item.csv"
itemSparse_csv_name = "itemSparse.csv"
spell_reagents_csv_name = "SpellReagents.csv"
modified_crafting_reagent_slot_csv_name = "ModifiedCraftingReagentSlot.csv"
modified_crafting_spells_csv_name = "ModifiedCraftingSpellSlot.csv"
modified_crafting_category_csv_name = "ModifiedCraftingCategory.csv"
MCRSlotXMCRCategory_csv_name = "MCRSlotXMCRCategory.csv"
modified_crafting_reagent_item_csv_name = "ModifiedCraftingReagentItem.csv"
profession_trees = "profession_trees.json"
optional_material_crafting_stats_csv_name = "wowprofitcalculator - OptionalMaterialCraftingStats.csv"
crafting_quality_csv_name = "CraftingQuality.csv"
profession_trees_json_name = "profession_trees.json"
crafting_data_enchant_quality_csv_name = "CraftingDataEnchantQuality.csv"
profession_effect_csv_name = "ProfessionEffect.csv"
profession_effect_type_csv_name = "ProfessionEffectType.csv"
crafting_reagent_effect_csv_name = "CraftingReagentEffect.csv"
crafting_reagent_quality_csv_name = "Craftingreagentquality.csv"
item_types_csv_name = "ItemClass.csv"

crafting_data_item_quality_csv_name = "CraftingDataItemQuality.csv"
crafting_data_ids_by_spell_id_json_name = "crafting_data_ids_by_spell_id.json"
product_item_ids_by_crafting_data_id_json_name = "product_item_ids_by_crafting_data_id.json"
prodict_item_ids_json_name = "product_item_ids_by_crafting_data_id.json"



async def insert_all_data_async():
    wow_api = await WowApi.create('us')

    # await insert_regions()

    await insert_records_from_api(
        connected_realm_index_file_name,
        wow_api.get_connected_realm_index,
        insert_connected_realms_index
    )
    realms = await insert_records_from_api(
        realms_file_name,
        wow_api.get_all_realms,
        insert_all_realms
    )
    await insert_records_from_csv(
        skill_line_ability_csv_name, 
        insert_spells_used_with_recipes
    )
    await insert_records_from_csv(
        modified_crafting_reagent_slot_csv_name,
        insert_modified_crafting_reagent_slot
    )
    await insert_records_from_csv(
        modified_crafting_category_csv_name,
        insert_modified_crafting_categories,
    )
    await insert_records_from_csv(
        MCRSlotXMCRCategory_csv_name,
        insert_CategoryReagentSlotRelationship,
    )
    await insert_records_from_csv(
        modified_crafting_reagent_item_csv_name,
        insert_modified_crafting_reagent_items,
    )
    await insert_records_from_csv(
        crafting_quality_csv_name,
        insert_crafting_qualities
    )
    await insert_records_from_csv(
        item_csv_name,
        insert_all_items_from_csv,
    )
    await insert_all_crafting_data_records()
    # because of that 'df' param insert_from_api doesn't work unless changed
    await insert_records_from_profession_trees(wow_api.get_professions_tree_by_expansion)

    # these 3 functions don't use a csv directly like the above ones. Thats why no insert_records_from_csv call
    await insert_product_records()
    await insert_material_records()
    await insert_optional_material_records()

    await insert_records_from_csv(
        optional_material_crafting_stats_csv_name, 
        insert_optional_material_crafting_stats
    )

def insert_all_data():
    insert_from_csv(profession_effect_type_csv_name, insert_profession_effect_type)
    insert_from_csv(profession_effect_csv_name, insert_profession_effect)
    insert_from_csv(crafting_reagent_effect_csv_name, insert_crafting_reagent_effect)
    insert_from_csv(crafting_reagent_quality_csv_name, insert_crafting_reagent_quality)
    insert_from_csv(item_types_csv_name, insert_item_types)

async def insert_records_from_profession_trees(api_fetch: Callable) -> List[models.ConnectedRealmsIndex]:
    print(f"Inserting data profession trees...")
    json_file_path = create_json_path(profession_trees_json_name)
    json_data = load_data_from_cache(json_file_path)

    if json_data == None:
        json_data = await api_fetch('df')
        save_data_to_cache(json_file_path, json_data)
        print("saved profession trees to json file!")

    inserted_records = await insert_dragonflight_profession_tree(json_data)
    print(f"Finished inserting data with {insert_dragonflight_profession_tree}!")
    return inserted_records


async def insert_regions(): # its async since its being called from an async context and django will raise an error otherwise.
    """Inserts all regions into the db."""
    na = "us"
    eu = "eu"
    kr = "kr"
    regions = [na, eu, kr]
    for region in regions:
        await models.Region.objects.acreate(region=region)

async def insert_connected_realms_index(connected_realm_index: dict) -> List[models.ConnectedRealmsIndex]:
    records = []
    for connected_realm in connected_realm_index["connected_realms"]:
        connected_realm_id = get_id_from_url(connected_realm["href"])
        record = models.ConnectedRealmsIndex(connected_realm_id=connected_realm_id)
        records.append(record)
    return await models.ConnectedRealmsIndex.objects.abulk_create(records, ignore_conflicts=True)

async def insert_all_realms(realms: dict):
    connected_realms_index_records = models.ConnectedRealmsIndex.objects.all()
    regions = models.Region.objects.all()
    realm_records = []

    for connected_realm in realms:  # each entry in results is a connected realm cluster
        connected_realm_object = await connected_realms_index_records.aget(
            connected_realm_id=connected_realm["id"]
        )
        for realm in connected_realm["realms"]:
            region_full_name = realm["region"]["name"]
            if region_full_name == "North America":
                region = await regions.aget(region="us")
            elif region_full_name == "Europe":
                region = await regions.aget(region="eu")
            elif region_full_name == "Korea":
                region = await regions.aget(region="kr")
            else:
                # print(f"What region is this: {region_full_name}")
                pass

            record = models.Realm(
                realm_id=realm["id"],
                connected_realm=connected_realm_object,
                population=connected_realm["population"]["type"],
                name=realm["slug"],
                region=region,
                timezone=realm["timezone"],
                play_style=realm["type"]["type"],
            )
            realm_records.append(record)
    return await models.Realm.objects.abulk_create(realm_records, ignore_conflicts=True)

async def insert_spells_used_with_recipes(skill_line_ability_spells: str) -> List[models.Spell]:
    spell_records = []
    spells_encountered = {}
    for spell in skill_line_ability_spells:
        spell_id = int(spell[5])

        if spell_id in spells_encountered:
            continue
        else:
            spells_encountered[spell_id] = 1

        spell_record = models.Spell(id=spell_id)
        spell_records.append(spell_record)
    return await models.Spell.objects.abulk_create(spell_records, ignore_conflicts=True)

async def insert_dragonflight_profession_tree(profession_trees: List[Dict]) -> List[List]:
    all_spells_by_recipe_id = await get_spell_records_by_recipe_id()
    all_crafting_data_records_ids_by_spell_id = await get_crafting_data_record_by_spell_id()

    categories_to_ignore = [
        "Quest Plans", "Recrafting",
        "Quest Designs", "Quest Techniques",
        "Quest Recipes", "Quest Patterns",
        "Quest Techniques", "Quest Formulas",
        "Quest Schematics", "Recrafting"
    ]
    recipes_to_ignore = ["Rummage Through Scrap"]

    professions = []
    categories = []
    recipes = []
    for profession in profession_trees:
        profession_record, _ = await models.ProfessionIndex.objects.aget_or_create(
                    name=profession["name"],
                    id=profession["id"]
                )
        professions.append(profession_record)

        for category in profession["categories"]:
            if category["name"] in categories_to_ignore:
                continue

            category_record, _ = await models.RecipeCategory.objects.aget_or_create(
                name=category["name"],
                profession=profession_record
            )
            categories.append(category_record)
            # recipe dict is from the api
            for recipe_dict in category["recipes"]:
                recipe_name = recipe_dict["name"]
                recipe_id = recipe_dict["id"]

                if recipe_name in recipes_to_ignore:
                    continue
                # api has incomplete data so these these are from csv
                spell_record = all_spells_by_recipe_id[recipe_id]

                crafting_data_record = all_crafting_data_records_ids_by_spell_id.get(spell_record.id) or None

                recipe_record = models.Recipe(
                    id=recipe_id,
                    name=recipe_name,
                    recipe_category=category_record,
                    spell=spell_record,
                    crafting_data=crafting_data_record
                )
                recipes.append(recipe_record)

# error is probably caused by records being skipped by ignore_conflicts being assigned to new records and since the forign keys are skipped the records don't have that foreign key correctly set so it raises the error
# get_or_create on categories and professions
    # inserted_professions_records = await models.ProfessionIndex.objects.abulk_create(professions, ignore_conflicts=True)
    # inserted_category_records = await models.RecipeCategory.objects.abulk_create(categories, ignore_conflicts=True)
    inserted_recipe_records = await models.Recipe.objects.abulk_create(recipes, ignore_conflicts=True)
    
    return [
        professions,
        categories,
        inserted_recipe_records,
        ]

async def insert_product_records() -> List[models.Product]:
    all_items = models.Item.objects.all()
    recipe_records = models.Recipe.objects.select_related("crafting_data").select_related("spell").all()
    quantities_by_spell_id = get_quantities_by_spell_id()

    crafting_data_by_crafting_data_id = get_crafting_data_by_crafting_data_id()
    product_item_id_by_spell_id = await get_product_item_records_by_spell_id()

    crafting_data_item_quality_by_crafting_data_id = await get_crafting_data_item_quality_by_crafting_data_id(all_items)

    products = []
    async for recipe_record in recipe_records:
        spell_id = recipe_record.spell.id

        quantity = quantities_by_spell_id[spell_id]

        if spell_id in product_item_id_by_spell_id:
            item_record = product_item_id_by_spell_id[spell_id]
            products.append(models.Product(
                item = item_record,
                quantity = quantity,
                recipe = recipe_record
            ))
        elif recipe_record.crafting_data:
            crafting_data_id = recipe_record.crafting_data.id
            
            crafted_item_id = crafting_data_by_crafting_data_id[crafting_data_id]
            if crafted_item_id == 0:
                different_tier_products = crafting_data_item_quality_by_crafting_data_id[crafting_data_id]
                
                for item_record in different_tier_products:
                    products.append(models.Product(
                        item = item_record,
                        quantity = quantity,
                        recipe = recipe_record
                    ))
            else:
                item_record = await all_items.aget(id=crafted_item_id)

                products.append(models.Product(
                    item = item_record,
                    quantity = quantity,
                    recipe = recipe_record
                ))
        else:
            print(f"No crafting data id or product item id for {recipe_record}")
            pass
    return await models.Product.objects.abulk_create(products, ignore_conflicts=True)

async def get_product_item_records_by_spell_id():
    path = create_csv_path(spell_effect_csv_name)

    loaded_spell_effect = load_data_from_cache(path)
    all_items = models.Item.objects.all()

    product_item_records_by_spell_id = {}
    for line in loaded_spell_effect:
        product_item_id = int(line[11])

        if product_item_id == 0: # 0 is for spells that produce no item
            continue
        try:
            item_record = await all_items.aget(id=product_item_id)
        except models.Item.DoesNotExist:
            # print(f"Item record for id={product_item_id} does not exist.")
            pass

        spell_id = int(line[35])
        product_item_records_by_spell_id[spell_id] = item_record
    return product_item_records_by_spell_id

async def insert_material_records() -> List[models.Material]:
    recipe_records = models.Recipe.objects.select_related("crafting_data").select_related("spell").all()

    # this function only gets quantities from spellReagents.csv which doens't contain modified crafting mat quantities
    material_quantities_by_spell_id = get_material_quantities_by_spell_id()
    item_records = models.Item.objects.all()
    
    material_records = []
    async for recipe_record in recipe_records:
        spell_id = recipe_record.spell.id
        if material_quantities_by_spell_id.get(spell_id): # recipe probably doens't use normal mats but optional mats instead
            mat_item_ids_and_quantities = material_quantities_by_spell_id[spell_id]
        else:
            continue
            #TODO figure out why recipes don't seem to have all normal mats
        for index in range(8):
            item_id = mat_item_ids_and_quantities[index]
            if item_id == 0:
                break
            item_record = await item_records.aget(id=item_id)
            quantity = mat_item_ids_and_quantities[index + 8]
            recraft_quantity = mat_item_ids_and_quantities[index + 16]

            material_record = models.Material(
                item=item_record,
                quantity=quantity,
                recraft_quantity=recraft_quantity,
                display_order=index,
                recipe=recipe_record
                )
            material_records.append(material_record)
    return await models.Material.objects.abulk_create(material_records, ignore_conflicts=True)

async def insert_optional_material_records() -> List[models.OptionalMaterial]:
    recipe_records = models.Recipe.objects.select_related("crafting_data").select_related("spell").all()
    optional_material_data_by_spell_id = get_optional_material_data_by_spell_id()
    MCRSlots = models.ModifiedCraftingReagentSlot.objects.all()
    
    optional_material_records = []
    async for recipe_record in recipe_records:
        spell_id = recipe_record.spell.id

        if optional_material_data_by_spell_id.get(spell_id): # recipe probably doens't use normal mats but optional mats instead
            optional_material_mats_by_display_order = optional_material_data_by_spell_id[spell_id]
        else:
            continue

        for optional_material in optional_material_mats_by_display_order:
            quantity = optional_material["quantity"]
            recraft_quantity = optional_material["recraft_quantity"]
            modified_crafting_slot_id = optional_material["modified_crafting_reagent_slot"]
            display_order = optional_material["display_order"]
            optional_material_slot = await MCRSlots.aget(id=modified_crafting_slot_id)

            if "(DNT)" in optional_material_slot.name:
                required = True
            else:
                required = False
            

            optional_material_record = models.OptionalMaterial(
                quantity=quantity,
                recraft_quantity=recraft_quantity,
                display_order=display_order,
                optional_material_slot=optional_material_slot,
                recipe=recipe_record,
                is_required=required
            )
            optional_material_records.append(optional_material_record)
    return await models.OptionalMaterial.objects.abulk_create(optional_material_records, ignore_conflicts=True)


async def get_spell_records_by_recipe_id() -> Dict[int, models.Spell]:
    skill_line_ability_path = create_csv_path(skill_line_ability_csv_name)

    all_spell_records = models.Spell.objects.all()
    if await all_spell_records.acount() == 0:
        await insert_spells_used_with_recipes()
        all_spell_records = models.Spell.objects.all()

    all_spells_by_recipe_id = {}
    skill_line_ability_data = load_data_from_cache(skill_line_ability_path)
    for recipe in skill_line_ability_data:
        temp_recipe_id = int(recipe[3])
        spell_id = int(recipe[5])
        try:
            spell_record = await all_spell_records.aget(id=spell_id)
        except models.Spell.DoesNotExist:
            continue
        all_spells_by_recipe_id[temp_recipe_id] = spell_record
    return all_spells_by_recipe_id

async def get_crafting_data_record_by_spell_id() -> Dict[int, models.CraftingData]:
    all_crafting_data_records = models.CraftingData.objects.all()
    if await all_crafting_data_records.acount() == 0:
        await insert_all_crafting_data_records()
        all_crafting_data_records = models.CraftingData.objects.all()

    return await create_crafting_data_by_spell_id_dict(all_crafting_data_records)

async def create_crafting_data_by_spell_id_dict(crafting_data_records: List) -> Dict[int, models.CraftingData]:
    spell_effect_csv_path = create_csv_path(spell_effect_csv_name)

    spell_effect_data = load_data_from_cache(spell_effect_csv_path)

    crafting_data_records_by_spell_id = {}
    for line in spell_effect_data:
        crafting_data_id = int(line[25])

        try:
            crafting_data_record = await crafting_data_records.aget(id=crafting_data_id)
        except models.CraftingData.DoesNotExist:
            continue
        spell_id = int(line[35])

        crafting_data_records_by_spell_id[spell_id] = crafting_data_record
    return crafting_data_records_by_spell_id

# TODO refactor to work like other insert functions and change functions like get_crafting_data_record_by_spell_id to reflect these changes
async def insert_all_crafting_data_records() -> List[models.CraftingData]:
    crafting_data_csv_path = create_csv_path(crafting_data_csv_name)

    crafting_data = load_data_from_cache(crafting_data_csv_path)

    crafting_data_records = []
    for line in crafting_data:
        crafting_data_id = int(line[0])
        crafting_data_record = models.CraftingData(
            id = crafting_data_id
        )
        crafting_data_records.append(crafting_data_record)
    return await models.CraftingData.objects.abulk_create(crafting_data_records, ignore_conflicts=True)

async def insert_crafting_qualities(data: List[List]) -> List[models.CraftingQuality]:
    crafting_quality_records = []
    for line in data:
        crafting_quality_id = int(line[0])
        crafting_quality_tier = int(line[1])
        crafting_quality_record = models.CraftingQuality(
            id = crafting_quality_id,
            quality_tier = crafting_quality_tier
        )
        crafting_quality_records.append(crafting_quality_record)
    return await models.CraftingQuality.objects.abulk_create(crafting_quality_records, ignore_conflicts=True)

async def insert_all_items_from_csv(item_data: List[List]) -> List[models.Item]:
    item_types = models.ItemType.objects.all()
    all_crafting_qualitites = models.CraftingQuality.objects.all()
    all_MCR_item_records = models.ModifiedCraftingReagentItem.objects.all()

    item_records = {}
    for line in item_data:
        item_id = int(line[0])
        crafting_quality_id = int(line[-1])
        MCR_Item_id = int(line[-2])
        item_type_id = int(line[1].split()[0])
        item_type_record = await item_types.aget(id=item_type_id)

        if crafting_quality_id != 0:
            quality_record = await all_crafting_qualitites.aget(id=crafting_quality_id)
        else:
            quality_record = None

        if MCR_Item_id != 0:
            MCR_item_record = await all_MCR_item_records.aget(id=MCR_Item_id)
        else:
            MCR_item_record = None
            
        item_records[item_id] = models.Item(
            id=line[0],
            quality = quality_record,
            type = item_type_record,
            MCR_item = MCR_item_record
        )
    # get item binding and name since they are not in item.csv
    item_sparse_csv = create_csv_path(itemSparse_csv_name)
    item_sparse_data = load_data_from_cache(item_sparse_csv)
    for line in item_sparse_data:
        item_id = int(line[0])
        if item_id in item_records:
            item_record = item_records[item_id]
            item_record.binding = line[80]
            item_record.name = line[6]
        else:
            continue
    return await models.Item.objects.abulk_create(item_records.values(), ignore_conflicts=True)

async def insert_modified_crafting_reagent_slot(modified_crafting_reagent_slot_data: List[List]) -> List[models.ModifiedCraftingReagentSlot]:
    MCRSlots = []
    for line in modified_crafting_reagent_slot_data:
        record = models.ModifiedCraftingReagentSlot(id=line[1], name=line[0])
        MCRSlots.append(record)
    await models.ModifiedCraftingReagentSlot.objects.abulk_create(MCRSlots, ignore_conflicts=True)

def get_quantities_by_spell_id() -> Dict[int, int]:
    spell_effect_csv_path = create_csv_path(spell_effect_csv_name)
    spell_effect_data = load_data_from_cache(spell_effect_csv_path)

    quantities_by_spell_id = {}
    for spell in spell_effect_data:
        spell_id = int(spell[35])
        quantity = float(spell[23])
        quantities_by_spell_id[spell_id] = quantity
    return quantities_by_spell_id

def get_crafting_data_by_crafting_data_id() -> Dict[int, int]:
    crafting_data_path = create_csv_path(crafting_data_csv_name)
    loaded_crafting_data = load_data_from_cache(crafting_data_path)

    crafting_data = {}
    for line in loaded_crafting_data:
        crafting_data_id = int(line[0])
        product_item_id = int(line[3])
        crafting_data[crafting_data_id] = product_item_id
    return crafting_data

async def get_crafting_data_item_quality_by_crafting_data_id(all_items: List[models.Item]) -> Dict[int, List[models.Item]]:
    item_records_by_crafting_data_id = {}

    item_records_by_crafting_data_id.update(await append_crafting_data_products(all_items))
    item_records_by_crafting_data_id.update(await append_crafting_data_enchant_products(all_items))

    return item_records_by_crafting_data_id

async def append_crafting_data_products(all_items: List[models.Item]):
    crafting_data_item_quality_csv_path = create_csv_path(crafting_data_item_quality_csv_name)
    crafting_data_item_quality_data = load_data_from_cache(crafting_data_item_quality_csv_path)
    item_records_by_crafting_data_id = {}

    for line in crafting_data_item_quality_data:
        crafting_data_id = int(line[2])
        # the items associated with this id don't exist in items table
        if crafting_data_id == 1:
            continue

        item_id = int(line[1])
        item_record = await all_items.aget(id=item_id)

        if crafting_data_id in item_records_by_crafting_data_id:
            item_records_by_crafting_data_id[crafting_data_id].append(item_record)
        else:
            item_records_by_crafting_data_id[crafting_data_id] = [item_record]
    
    return item_records_by_crafting_data_id

async def append_crafting_data_enchant_products(all_items: List[models.Item]):
    crafting_data_enchant_quality_csv_path = create_csv_path(crafting_data_enchant_quality_csv_name)
    crafting_data_enchant_quality_data = load_data_from_cache(crafting_data_enchant_quality_csv_path)
    item_records_by_crafting_data_id = {}

    for line in crafting_data_enchant_quality_data:
        crafting_data_id = int(line[4])
        item_id = int(line[3])
        try:
            item_record = await all_items.aget(id=item_id)
        except models.Item.DoesNotExist:
            # print(f"Item id {item_id} not found. skipping")
            continue

        if crafting_data_id in item_records_by_crafting_data_id:
            item_records_by_crafting_data_id[crafting_data_id].append(item_record)
        else:
            item_records_by_crafting_data_id[crafting_data_id] = [item_record]

    return item_records_by_crafting_data_id

def get_material_quantities_by_spell_id() -> Dict[int, List[int]]:
    spell_reagents_path = create_csv_path(spell_reagents_csv_name)
    spell_reagents_data = load_data_from_cache(spell_reagents_path)

    mat_item_ids_and_quantities = {}
    for spell in spell_reagents_data:
        spell_id = int(spell[1])
        
        mat_item_ids_and_quantities[spell_id] = list(map(int, spell[2:27]))
    return mat_item_ids_and_quantities

# TODO needs to be refactored to be DRY
def get_optional_material_data_by_spell_id() -> Dict[int, Dict[int, Dict[str, int]]]:
    modified_crafting_spells_csv_path = create_csv_path(modified_crafting_spells_csv_name)
    modified_crafting_spells_csv_data = load_data_from_cache(modified_crafting_spells_csv_path)

    materials = {}
    for material in modified_crafting_spells_csv_data:
        recipe_spell_id = int(material[1])

        if recipe_spell_id not in materials:
            materials[recipe_spell_id] = []
            materials[recipe_spell_id].append(
                {
                    "display_order" : int(material[2]),
                    "modified_crafting_reagent_slot" : int(material[3]),
                    "quantity" : int(material[5]),
                    "recraft_quantity" : int(material[6])
                }
            )
        else:
            materials[recipe_spell_id].append(
                {
                    "display_order" : int(material[2]),
                    "modified_crafting_reagent_slot" : int(material[3]),
                    "quantity" : int(material[5]),
                    "recraft_quantity" : int(material[6])
                }
            )
    return materials

async def insert_modified_crafting_categories(MCC_data: List[List]) -> List[models.ModifiedCraftingCategory]:
    categories = []
    for line in MCC_data:
        category_id = int(line[0])
        name = line[1]
        description = line[2]
        category_record = models.ModifiedCraftingCategory(
            id=category_id,
            name=name,
            description=description
        )
        categories.append(category_record)
    return await models.ModifiedCraftingCategory.objects.abulk_create(categories, ignore_conflicts=True)

# Since this doesn't set a primary key and i'm choosing to 
# add new records by going through a list of all records
# when this is run over and over it will add the same records with
# new primary keys
async def insert_CategoryReagentSlotRelationship(MCRSlotXMCRCategory_data: List[List]) -> List[models.CategoryReagentSlotRelationship]:
    categories = models.ModifiedCraftingCategory.objects.all()
    slots = models.ModifiedCraftingReagentSlot.objects.all()

    records = []
    for line in MCRSlotXMCRCategory_data:
        primary_id = int(line[0])
        category_id = int(line[1])
        order = int(line[2])
        slot_id = int(line[3])
        category_record = await categories.aget(id=category_id)
        slot_record = await slots.aget(id=slot_id)

        CategoryReagentSlotRelationship_record = models.CategoryReagentSlotRelationship(
            id = primary_id,
            category=category_record,
            reagent_slot=slot_record,
            order=order
        )
        records.append(CategoryReagentSlotRelationship_record)
    return await models.CategoryReagentSlotRelationship.objects.abulk_create(records, ignore_conflicts=True)

async def insert_modified_crafting_reagent_items(
        modified_crafting_reagent_item_data: List[List]
    ) -> List[models.ModifiedCraftingReagentItem]:
    all_modified_crafting_categories = models.ModifiedCraftingCategory.objects.all()

    MCR_item_records = []
    for line in modified_crafting_reagent_item_data:
        MCR_item_id = int(line[0])
        description = line[1]
        MCR_category_id = int(line[2])

        if MCR_category_id == 0: # a single record in MCRItem has 0 category ID which doesn't exist
            continue

        category_record = await all_modified_crafting_categories.aget(id=MCR_category_id)
        MCR_item_record = models.ModifiedCraftingReagentItem(
            id=MCR_item_id,
            description=description,
            modified_crafting_category=category_record
        )
        MCR_item_records.append(MCR_item_record)
    return await models.ModifiedCraftingReagentItem.objects.abulk_create(MCR_item_records, ignore_conflicts=True)

async def insert_optional_material_crafting_stats(
        optional_material_crafting_stats_data: List[List]
    ) -> List[models.CraftingStats]:
    all_items = models.Item.objects.all()
    crafting_qualities = models.CraftingQuality.objects.all()

    crafting_stats = []
    for single_items_crafting_stats in optional_material_crafting_stats_data:
        name = single_items_crafting_stats[0]
        quality_tier = convert_to_int_or_none(single_items_crafting_stats[1])
        if quality_tier != None:
            quality = await crafting_qualities.aget(id=quality_tier) # id and tier are equal for items with 3 quality tiers (tradegoods)
        else:
            quality = None
        items = all_items.filter(name=name)

        if await sync_to_async(len)(items) > 1: # some items have multiple qualities and need further filtering
            item = await items.aget(quality=quality)
        elif await sync_to_async(len)(items) == 1: # item has only one quality return it
            item = await items.aget() 
        else:
            raise MissingItemRecordError(f"Unable to find item record for {name}\nfrom existing items records: {items}")
        crafting_stat_record = models.CraftingStats(
            item = item,
            inspiration = convert_to_int_or_none(single_items_crafting_stats[2]),
            skill_from_inspiration = convert_to_float_or_none(single_items_crafting_stats[3]),
            multicraft = convert_to_int_or_none(single_items_crafting_stats[4]),
            resourcefulness = convert_to_int_or_none(single_items_crafting_stats[5]),
            increase_material_from_resourcefulness = convert_to_float_or_none(single_items_crafting_stats[6]),
            skill = convert_to_int_or_none(single_items_crafting_stats[7]),
            crafting_speed = convert_to_float_or_none(single_items_crafting_stats[8]),
        )
        crafting_stats.append(crafting_stat_record)
    return await models.CraftingStats.objects.abulk_create(crafting_stats, ignore_conflicts=True)

def insert_profession_effect_type(
        profession_effect_type_data: List[List]
    ) -> List[models.ProfessionEffectType]:

    records = []
    for line in profession_effect_type_data:
        record = models.ProfessionEffectType(
            id=int(line[2]),
            name=line[1]
        )
        records.append(record)
    return models.ProfessionEffectType.objects.bulk_create(records, ignore_conflicts=True)

def insert_profession_effect(
        profession_effect_data: List[List]
    ) -> List[models.ProfessionEffect]:
    profession_effect_types = models.ProfessionEffectType.objects.all()
    modified_crafting_slots = models.ModifiedCraftingReagentSlot.objects.all()
    
    records = []
    for line in profession_effect_data:
        profession_effect_type_id = int(line[1])
        profession_effect_type_record = profession_effect_types.get(id=profession_effect_type_id)
        if int(line[3]) == 0:
            modified_crafting_slot_record = None
        else:
            MCR_slot_id = int(line[3])
            modified_crafting_slot_record = modified_crafting_slots.get(id=MCR_slot_id)

        record = models.ProfessionEffect(
            id=int(line[0]),
            profession_effect_type=profession_effect_type_record,
            amount =float(line[2]),
            MCR_slot=modified_crafting_slot_record
        )
        records.append(record)
    return models.ProfessionEffect.objects.bulk_create(records, ignore_conflicts=True)

def insert_crafting_reagent_effect(
        crafting_reagent_effect_data
    ) -> List[models.CraftingReagentEffect]:
    profession_effects = models.ProfessionEffect.objects.all()
    modified_crafting_categories = models.ModifiedCraftingCategory.objects.all()
    
    records = []
    for line in crafting_reagent_effect_data:
        profession_effect_type_id = int(line[1])
        profession_effect_record = profession_effects.get(id=profession_effect_type_id)
        MCR_slot_id = int(line[3])
        modified_crafting_category_record = modified_crafting_categories.get(id=MCR_slot_id)

        record = models.CraftingReagentEffect(
            id=int(line[0]),
            profession_effect=profession_effect_record,
            order=int(line[2]),
            modified_crafting_category=modified_crafting_category_record
        )
        records.append(record)
    return models.CraftingReagentEffect.objects.bulk_create(records, ignore_conflicts=True)

def insert_crafting_reagent_quality(
        crafting_reagent_quality_data: List[List]
    ) -> List[models.CraftingReagentQuality]:
    modified_crafting_categories = models.ModifiedCraftingCategory.objects.all()
    items = models.Item.objects.all()
    
    records = []
    for line in crafting_reagent_quality_data:
        item_id = int(line[2])
        try:
            item_record = items.get(id=item_id)
        except models.Item.DoesNotExist:
            print(f"item_id: {item_id} not found")
            continue
        MCR_slot_id = int(line[5])
        modified_crafting_category_record = modified_crafting_categories.get(id=MCR_slot_id)

        record = models.CraftingReagentQuality(
            id=int(line[0]),
            order=int(line[1]),
            item=item_record,
            difficulty_adjustment=int(line[3]),
            reagent_effect_percent=int(line[4]),
            modified_crafting_category=modified_crafting_category_record
        )
        records.append(record)
    return models.CraftingReagentQuality.objects.bulk_create(records, ignore_conflicts=True)

def insert_item_types(
    item_class_data: List[List]
    ) -> List[models.ItemType]:

    item_classes = []
    for item_class in item_class_data:
        class_id = item_class[2]
        name = item_class[1]

        item_classes.append(models.ItemType(
            id = class_id,
            name = name
        ))
    models.ItemType.objects.bulk_create(item_classes, ignore_conflicts=True)

# need to update the type column for existing item records probably a new func for this

# current update_items doesn't work like the rest of the tested inserts.
# if new items don't fit into the scheme then they should be printed for me to look at
# maybe update fields on item records that don't match the data in new csv? Is this a possibility?
def update_items(
        item_data: List[List]
    ) -> List[models.Item]:
    """
    Go through csv of a new patches items and add them to the db. 
    Csv needs to be downloaded seperately. Try wago.tools.
    """
    item_types = models.ItemType.objects.all()
    all_crafting_qualitites = models.CraftingQuality.objects.all()
    all_MCR_item_records = models.ModifiedCraftingReagentItem.objects.all()

    item_records = {}
    for line in item_data:
        item_id = int(line[0])
        crafting_quality_id = int(line[-1])
        MCR_Item_id = int(line[-2])
        print(MCR_Item_id)
        item_type_id = int(line[1])
        item_type_record = item_types.get(id=item_type_id)

        if crafting_quality_id != 0:
            quality_record = all_crafting_qualitites.get(id=crafting_quality_id)
        else:
            quality_record = None

        if MCR_Item_id != 0:
            print(MCR_Item_id)
            MCR_item_record = all_MCR_item_records.get(id=MCR_Item_id)
        else:
            MCR_item_record = None
            
        item_records[item_id] = models.Item(
            id=line[0],
            quality = quality_record,
            type = item_type_record,
            MCR_item = MCR_item_record
        )
    # get item binding and name since they are not in item.csv
    item_sparse_csv = create_csv_path(itemSparse_csv_name)
    item_sparse_data = load_data_from_cache(item_sparse_csv)
    for line in item_sparse_data:
        item_id = int(line[0])
        if item_id in item_records:
            item_record = item_records[item_id]
            item_record.binding = line[80]
            item_record.name = line[6]
        else:
            continue
    return models.Item.objects.bulk_create(item_records.values(), ignore_conflicts=True)


def load_data(csv_name):
    csv_path = create_csv_path(csv_name)
    return load_data_from_cache(csv_path)
