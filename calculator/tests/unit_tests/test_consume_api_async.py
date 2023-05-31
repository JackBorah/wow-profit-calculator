from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from unittest import skip, IsolatedAsyncioTestCase
from unittest import TestCase as UnittestTestCase
from textwrap import dedent
import json
import os
import csv


from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase
from getwowdataasync import urls, convert_to_datetime, WowApi
from calculator import models
from calculator.utils import *
from calculator.consume_api_async import *
from calculator.exceptions import MissingItemRecordError
from freezegun import freeze_time

# Will fix when all inserts are done TODO
# class TestInsertAllData(IsolatedAsyncioTestCase):
#     @patch("calculator.consume_api_async.WowApi.create", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_all_connected_realm_index_records", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_regions", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_all_realms", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_modified_crafting_reagent_slot", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_all_dragonflight_items", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_optional_material_crafting_stats", new_callable=AsyncMock)
#     @patch("calculator.consume_api_async.insert_dragonflight_profession_tree", new_callable=AsyncMock)
#     async def test_insert_all_data_calls_insertion_functions(
#             self,
#             mock_insert_dragonflight_profession_tree,
#             mock_insert_optional_material_crafting_stats,
#             mock_insert_all_dragonflight_items,
#             mock_insert_modified_crafting_reagent_slot,
#             mock_insert_all_realms,
#             mock_insert_regions,
#             mock_connected_realm_index_records,
#             mock_wow_api_create
#     ):
#         await insert_all_data()

#         mock_wow_api_create.assert_called_once_with('us')
#         mock_connected_realm_index_records.assert_called_once()
#         mock_insert_regions.assert_called_once()
#         mock_insert_all_realms.assert_called_once()
#         mock_insert_modified_crafting_reagent_slot.assert_called_once()
#         mock_insert_all_dragonflight_items.assert_called_once()
#         mock_insert_optional_material_crafting_stats.assert_called_once()
#         mock_insert_dragonflight_profession_tree.assert_called_once()

class TestInsertRegions(TestCase):
    async def test_insert_regions_success(self):
        await insert_regions()

        regions = ["us", "eu", "kr"]
        for region in regions:
            region_record = await models.Region.objects.aget(region=region)
            self.assertIsNotNone(region_record)


class TestInsertConnectedRealmIndexRecords(TestCase):
    def setUp(self):
        self.test_data = {
            "connected_realms": [
                {"href": "https://some-url/connected-realm/1"},
                {"href": "https://some-url/connected-realm/2"},
            ]
        }

    async def test_insert_all_connected_realm_index_records_success(self):
        inserted_records = await insert_connected_realms_index(self.test_data)
        self.assertEqual(len(inserted_records), 2)

        record1 = await models.ConnectedRealmsIndex.objects.aget(connected_realm_id=1)
        record2 = await models.ConnectedRealmsIndex.objects.aget(connected_realm_id=2)

        self.assertIsNotNone(record1)
        self.assertIsNotNone(record2)


class TestInsertAllRealms(TestCase):
    def setUpTestData():
        models.ConnectedRealmsIndex.objects.create(connected_realm_id=1)
        models.Region.objects.create(region="us")
        models.Region.objects.create(region="eu")
        models.Region.objects.create(region="kr")


    async def test_insert_all_realms_success(self):
        realms_data = [
            {
                "id": 1,
                "population": {"type": "medium"},
                "realms": [
                    {
                        "id": 100,
                        "region": {"name": "North America"},
                        "slug": "realm-1",
                        "timezone": "America/New_York",
                        "type": {"type": "pve"}
                    },
                    {
                        "id": 101,
                        "region": {"name": "Europe"},
                        "slug": "realm-2",
                        "timezone": "America/New_York",
                        "type": {"type": "pve"}
                    },
                    {
                        "id": 102,
                        "region": {"name": "Korea"},
                        "slug": "realm-3",
                        "timezone": "America/New_York",
                        "type": {"type": "pve"}
                    },
                ],
            },
        ]

        await insert_all_realms(realms_data)

        realm_ids = [100, 101, 102]
        for realm_id in realm_ids:
            realm_record = await models.Realm.objects.aget(realm_id=realm_id)
            self.assertIsNotNone(realm_record)


class TestInsertAllSpells(TestCase):
    spells = [
        ("spell_1", "name_1", "rank_1", "icon_1", "cost_1", "1"),
        ("spell_2", "name_2", "rank_2", "icon_2", "cost_2", "2"),
    ]
    spells_with_same_ids = [
        ("spell_1", "name_1", "rank_1", "icon_1", "cost_1", "230047"),
        ("spell_2", "name_2", "rank_2", "icon_2", "cost_2", "230047"),
    ]

    async def test_insert_all_spell_records_success(self):
        inserted_spell_records = await insert_spells_used_with_recipes(self.spells)

        spell_ids = [1, 2]
        for spell_id in spell_ids:
            spell_record = await models.Spell.objects.aget(id=spell_id)
            self.assertIsNotNone(spell_record)

        self.assertEqual(spell_ids[0], inserted_spell_records[0].id)
        self.assertEqual(spell_ids[1], inserted_spell_records[1].id)

    async def test_insert_all_spell_records_skips_repeated_spell(self):
        inserted_spell_records = await insert_spells_used_with_recipes(self.spells_with_same_ids)

        spell_id = 230047
        spell_record = await models.Spell.objects.aget(id=spell_id)
        self.assertIsNotNone(spell_record)

        self.assertEqual(spell_id, inserted_spell_records[0].id)
    
    def is_a_spell_used_by_more_than_one_recipe(self):
        spells = {}
        skill_line_ability_path = create_csv_path("SkillLineAbility.csv")
        profession_ids = [202, 393, 164, 333, 182, 186, 197, 773, 185, 356, 165, 171, 755]
        spell_to_skip = 230047
        
        with open(skill_line_ability_path, 'r') as spell_name:
            spell_names_reader = csv.reader(spell_name)
            next(spell_names_reader)
            for row in spell_names_reader:
                for profession in profession_ids: 
                    if profession == int(row[4]) and int(row[5]) != spell_to_skip:
                        if row[5] in spells:
                            self.fail(f"spell: {row[5]} is a repeat!")
                        else:
                            spells[row[5]] = row[3]


class TestGetSpellRecordsByRecipeId(TestCase):
    mock_skill_line_ability_data = [
            [0,0,0,1,0,1],
            [0,0,0,2,0,2]
    ]
    mock_skill_line_ability_data_with_no_created_records = [
            [0,0,0,3,0,3],
            [0,0,0,4,0,4]
    ]

    def setUpTestData():
        models.Spell.objects.create(id=1)
        models.Spell.objects.create(id=2)

    async def test_get_spell_records_by_recipe_id_success(self):
        with patch('calculator.consume_api_async.load_data_from_cache') as patched_load_data:
            patched_load_data.return_value=self.mock_skill_line_ability_data

            all_spells_by_recipe_id = await get_spell_records_by_recipe_id()

            expected_recipe_ids = [1, 2]
            expected_spell_ids = [1, 2]
            for recipe_id, spell_id in zip(expected_recipe_ids, expected_spell_ids):
                self.assertIn(recipe_id, all_spells_by_recipe_id)
                self.assertEqual(spell_id, all_spells_by_recipe_id[recipe_id].id)

    async def test_get_spell_records_by_recipe_id_when_spell_id_not_in_records(self):
        with patch('calculator.consume_api_async.load_data_from_cache') as patched_load_data:
            patched_load_data.return_value=self.mock_skill_line_ability_data_with_no_created_records

            all_spells_by_recipe_id = await get_spell_records_by_recipe_id()

            self.assertEqual({}, all_spells_by_recipe_id)


class TestGetCraftingDataRecordBySpellId(TestCase):
    mock_crafting_data = [
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ]
    mock_spell_effect_data = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,2],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2]
    ]

    def setUpTestData():
        models.CraftingData.objects.create(id=3)
        models.CraftingData.objects.create(id=4)

    async def test_insert_all_crafting_data_records_success(self):
        with patch('calculator.consume_api_async.load_data_from_cache') as patched_load_data:
            patched_load_data.return_value = self.mock_crafting_data
            inserted_records = await insert_all_crafting_data_records()

        expected_record_1 = await models.CraftingData.objects.aget(id=1)
        expected_record_2 = await models.CraftingData.objects.aget(id=2)

        self.assertEqual(expected_record_1, inserted_records[0])
        self.assertEqual(expected_record_2, inserted_records[1])

    async def test_create_crafting_data_by_spell_id_dict_success(self):
        all_records = models.CraftingData.objects.all()

        with patch('calculator.consume_api_async.load_data_from_cache') as patched_load_data:
            patched_load_data.return_value=self.mock_spell_effect_data
            actual_crafting_data_records_by_spell_id = await create_crafting_data_by_spell_id_dict(all_records)

        expected_record_3 = await models.CraftingData.objects.aget(id=3)
        expected_record_4 = await models.CraftingData.objects.aget(id=4)

        expected_records = [expected_record_3, expected_record_4]
        expected_spell_ids = [1, 2]
        for expected_record, expected_spell_id in zip(expected_records, expected_spell_ids):
            self.assertEqual(expected_record, actual_crafting_data_records_by_spell_id[expected_spell_id])

class InsertAllItemsFromCsvTest(TestCase):
    def setUp(self):
        self.item_data = [
            [1] + ["5 (word)"] * 9 + [1, 2],
            [2] + ["6 (words)"] * 9 + [2, 3],
        ]

        self.item_sparse_data = [
            [1] + [0] * 5 + ['Item 1 Name'] + [0] * 73 + ['Binding 1'],
            [2] + [0] * 5 + ['Item 2 Name'] + [0] * 73 + ['Binding 2'],
        ]

    def setUpTestData():
        models.CraftingQuality.objects.create(id=2, quality_tier=1)
        models.CraftingQuality.objects.create(id=3, quality_tier=2)

        models.ModifiedCraftingReagentItem.objects.create(id=1)
        models.ModifiedCraftingReagentItem.objects.create(id=2)

        models.ItemType.objects.create(id=5)
        models.ItemType.objects.create(id=6)

    @patch('calculator.consume_api_async.create_csv_path', return_value="path")
    @patch('calculator.consume_api_async.load_data_from_cache')
    async def test_insert_all_items_from_csv(self, load_data_from_cache_mock, create_csv_path_mock):
        load_data_from_cache_mock.return_value = self.item_sparse_data
        items = await insert_all_items_from_csv(self.item_data)

        crafting_quality_record_1 = await models.CraftingQuality.objects.aget(id=2)
        crafting_quality_record_2 = await models.CraftingQuality.objects.aget(id=3)
        MCR_record_1 = await models.ModifiedCraftingReagentItem.objects.aget(id=1)
        MCR_record_2 = await models.ModifiedCraftingReagentItem.objects.aget(id=2)
        itemType_1 = await models.ItemType.objects.aget(id=5)
        itemType_2 = await models.ItemType.objects.aget(id=6)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 1)
        self.assertEqual(items[0].quality, crafting_quality_record_1)
        self.assertEqual(items[0].MCR_item, MCR_record_1)
        self.assertEqual(items[0].type, itemType_1)
        self.assertEqual(items[0].name, 'Item 1 Name')
        self.assertEqual(items[0].binding, 'Binding 1')

        self.assertEqual(items[1].id, 2)
        self.assertEqual(items[1].quality, crafting_quality_record_2)
        self.assertEqual(items[1].MCR_item, MCR_record_2)
        self.assertEqual(items[1].type, itemType_2)
        self.assertEqual(items[1].name, 'Item 2 Name')
        self.assertEqual(items[1].binding, 'Binding 2')

        create_csv_path_mock.assert_called_once_with('itemSparse.csv')
        load_data_from_cache_mock.assert_called_once()

class TestGetQuantitiesBySpellId(TestCase):

    def setUp(self):
        self.spell_effect_data = [['x'] * 50, ['x'] * 50]

        self.spell_effect_data[0][35] = 1
        self.spell_effect_data[0][23] = 5
        self.spell_effect_data[1][35] = 2
        self.spell_effect_data[1][23] = 3


    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_get_quantities_by_spell_id(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_csv_path'
        mock_load_data_from_cache.return_value = self.spell_effect_data

        quantities_by_spell_id = get_quantities_by_spell_id()

        expected_quantities_by_spell_id = {
            1: 5,
            2: 3,
        }
        self.assertEqual(quantities_by_spell_id, expected_quantities_by_spell_id)

        # Check if the mocked functions were called
        mock_create_csv_path.assert_called_once_with('SpellEffect.csv')
        mock_load_data_from_cache.assert_called_once_with('mock_csv_path')

class TestGetCraftingDataByCraftingDataId(TestCase):

    def setUp(self):
        self.loaded_crafting_data = [
            [1, 'x', 'x', 100],
            [2, 'x', 'x', 200],
            [3, 'x', 'x', 300],
        ]

    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_get_crafting_data_by_crafting_data_id(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_csv_path'
        mock_load_data_from_cache.return_value = self.loaded_crafting_data

        crafting_data = get_crafting_data_by_crafting_data_id()

        # Check the results
        expected_crafting_data = {
            1: 100,
            2: 200,
            3: 300,
        }
        self.assertEqual(crafting_data, expected_crafting_data)

        # Check if the mocked functions were called
        mock_create_csv_path.assert_called_once_with('CraftingData.csv')
        mock_load_data_from_cache.assert_called_once_with('mock_csv_path')

class TestGetProductItemIdBySpellId(TestCase):
    test_data=[
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
        ]
        
    def setUpTestData():
        models.Item.objects.create(id=1)

    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    async def test_get_product_item_id_by_spell_id(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_csv_path'
        mock_load_data_from_cache.return_value = self.test_data
        actual_product_item_records_by_spell_id = await get_product_item_records_by_spell_id()
        
        expected_item_record = await models.Item.objects.aget(id=1)
        actual_item_record = actual_product_item_records_by_spell_id[1]

        self.assertEqual(1, len(actual_product_item_records_by_spell_id))
        self.assertEqual(expected_item_record, actual_item_record)

class TestGetCraftingDataItemQualityByCraftingDataId(TestCase):
    def setUp(self):
        self.loaded_crafting_data_item_quality_data = [
            # [id, ItemId, CraftingDataId]
            [0, 1, 3],
            [1, 2, 3],
            [2, 3, 2],
            [6, 6, 1],
        ]
        self.loaded_crafting_data_enchant_quality_data = [
            # [id, rank, spellEnhanceId, ItemId, CraftingData,ID]
            [3, 0, 0, 4, 4],
            [4, 0, 0, 5, 4],
            [5, 0, 0, 6, 5],
        ]

    def setUpTestData():
        models.Item.objects.create(id=1)
        models.Item.objects.create(id=2)
        models.Item.objects.create(id=3)
        models.Item.objects.create(id=4)
        models.Item.objects.create(id=5)
        models.Item.objects.create(id=6)

    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    async def test_append_crafting_data_products(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_csv_path'
        mock_load_data_from_cache.return_value = self.loaded_crafting_data_item_quality_data
        all_items = models.Item.objects.all()
        item_records_by_crafting_data_id = await append_crafting_data_products(all_items)

        item_record_1 = await all_items.aget(id=1)
        item_record_2 = await all_items.aget(id=2)
        item_record_3 = await all_items.aget(id=3)

        expected_item_records_by_crafting_data_id = {
            3: [item_record_1, item_record_2],
            2: [item_record_3],
        }
        self.assertEqual(item_records_by_crafting_data_id, expected_item_records_by_crafting_data_id)

        mock_create_csv_path.assert_called_once_with('CraftingDataItemQuality.csv')
        mock_load_data_from_cache.assert_called_once_with('mock_csv_path')

    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    async def test_append_crafting_data_enchant_products(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_csv_path'
        mock_load_data_from_cache.return_value = self.loaded_crafting_data_enchant_quality_data
        all_items = models.Item.objects.all()
        item_records_by_crafting_data_id = await append_crafting_data_enchant_products(all_items)

        item_record_4 = await all_items.aget(id=4)
        item_record_5 = await all_items.aget(id=5)
        item_record_6 = await all_items.aget(id=6)

        expected_item_records_by_crafting_data_id = {
            4: [item_record_4, item_record_5],
            5: [item_record_6]
        }
        self.assertEqual(item_records_by_crafting_data_id, expected_item_records_by_crafting_data_id)

        mock_create_csv_path.assert_called_once_with('CraftingDataEnchantQuality.csv')
        mock_load_data_from_cache.assert_called_once_with('mock_csv_path')


class TestCreateProductRecords(TestCase):
    def setUpTestData():
        crafting_data_1 = models.CraftingData.objects.create(id=1)
        crafting_data_2 = models.CraftingData.objects.create(id=2)
        spell_1 = models.Spell.objects.create(id=1)
        spell_2 = models.Spell.objects.create(id=2)
        spell_3 = models.Spell.objects.create(id=3)
        models.Recipe.objects.create(id=1, crafting_data=crafting_data_1, spell=spell_1)
        models.Recipe.objects.create(id=2, crafting_data=crafting_data_2, spell=spell_2)
        models.Recipe.objects.create(id=3, spell=spell_3)
        models.Item.objects.create(id=1)
        models.Item.objects.create(id=2)
        models.Item.objects.create(id=3)
        models.Item.objects.create(id=4)


    @patch('calculator.consume_api_async.get_quantities_by_spell_id')
    @patch('calculator.consume_api_async.get_crafting_data_by_crafting_data_id')
    @patch('calculator.consume_api_async.get_crafting_data_item_quality_by_crafting_data_id')
    @patch('calculator.consume_api_async.get_product_item_records_by_spell_id')
    async def test_insert_product_records(
        self, 
        mock_get_product_item_records_by_spell_id,
        mock_get_crafting_data_item_quality_by_crafting_data_id, 
        mock_get_crafting_data_by_crafting_data_id,
        mock_get_quantities_by_spell_id,
        ):
        item_1 = await models.Item.objects.aget(id=1)
        item_2 = await models.Item.objects.aget(id=2)
        item_3 = await models.Item.objects.aget(id=3)
        item_4 = await models.Item.objects.aget(id=4)

        mock_get_quantities_by_spell_id.return_value = {1: 1, 2: 2, 3: 3}
        mock_get_crafting_data_by_crafting_data_id.return_value = {1: 1, 2: 0}
        mock_get_crafting_data_item_quality_by_crafting_data_id.return_value = {
            1: [],
            2: [item_2, item_3]
        }
        mock_get_product_item_records_by_spell_id.return_value = {
            3: item_4
        }
        recipe_1 = await models.Recipe.objects.aget(id=1)
        recipe_2 = await models.Recipe.objects.aget(id=2)
        recipe_3 = await models.Recipe.objects.aget(id=3)


        products = await insert_product_records()

        expected_products = [
            models.Product(item=item_1, quantity=1, recipe=recipe_1),
            models.Product(item=item_2, quantity=2, recipe=recipe_2),
            models.Product(item=item_3, quantity=2, recipe=recipe_2),
            models.Product(item=item_4, quantity=3, recipe=recipe_3)
        ]
        self.assertEqual(len(products), len(expected_products))
        for product, expected_product in zip(products, expected_products):
            self.assertEqual(product.item, expected_product.item)
            self.assertEqual(product.quantity, expected_product.quantity)
            self.assertEqual(product.recipe, expected_product.recipe)


class TestGetMaterialQuantitiesBySpellId(TestCase):
    @patch('calculator.consume_api_async.create_csv_path')
    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_get_material_quantities_by_spell_id(self, mock_load_data_from_cache, mock_create_csv_path):
        mock_create_csv_path.return_value = 'mock_spell_reagents_csv_path'
        mock_load_data_from_cache.return_value = [
            [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
            [2, 2, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
        ]
        mat_item_ids = get_material_quantities_by_spell_id()

        expected_mat_item_ids = {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
            2: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
        }
        self.assertEqual(mat_item_ids, expected_mat_item_ids)

        mock_create_csv_path.assert_called_once_with('SpellReagents.csv')
        mock_load_data_from_cache.assert_called_once_with('mock_spell_reagents_csv_path')


class TestCreateMaterialRecords(TestCase):
    @patch('calculator.consume_api_async.get_material_quantities_by_spell_id')
    def test_insert_material_records(self, mock_get_material_quantities_by_spell_id):
        mock_get_material_quantities_by_spell_id.return_value = {
            1: [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0],
        }

        item = models.Item.objects.create(id=1, name="Item 1")
        spell = models.Spell.objects.create(id=1, name="Spell 1")
        crafting_data = models.CraftingData.objects.create(id=1)
        recipe = models.Recipe.objects.create(id= 1, spell=spell, crafting_data=crafting_data)

        material_records = async_to_sync(insert_material_records)()

        self.assertEqual(len(material_records), 1)
        material_record = material_records[0]
        self.assertEqual(material_record.item, item)
        self.assertEqual(material_record.quantity, 2)
        self.assertEqual(material_record.recraft_quantity, 3)
        self.assertEqual(material_record.display_order, 0)
        self.assertEqual(material_record.recipe, recipe)

        mock_get_material_quantities_by_spell_id.assert_called_once()


class TestCreateOptionalMaterialRecords(TestCase):
    @patch('calculator.consume_api_async.get_optional_material_data_by_spell_id')
    def test_create_optional_material_records(self, mock_get_optional_material_data_by_spell_id):
        # Set up mocks
        mock_get_optional_material_data_by_spell_id.return_value = {
            1 :  [
                {
                    "quantity": 2,
                    "modified_crafting_reagent_slot": 1,
                    "recraft_quantity": 3,
                    "display_order": 0
                }
            ],
        }

        # Create test data
        spell = models.Spell.objects.create(id=1, name="Spell 1")
        crafting_data = models.CraftingData.objects.create(id=1)
        recipe = models.Recipe.objects.create(id=1, spell=spell, crafting_data=crafting_data)
        optional_material_slot = models.ModifiedCraftingReagentSlot.objects.create(id=1, name="test (DNT)")

        # Call the function
        optional_material_records = async_to_sync(insert_optional_material_records)()

        # Check the results
        self.assertEqual(len(optional_material_records), 1)
        optional_material_record = optional_material_records[0]
        self.assertEqual(optional_material_record.quantity, 2)
        self.assertEqual(optional_material_record.recraft_quantity, 3)
        self.assertEqual(optional_material_record.display_order, 0)
        self.assertEqual(optional_material_record.optional_material_slot, optional_material_slot)
        self.assertEqual(optional_material_record.recipe, recipe)
        self.assertEqual(optional_material_record.is_required, True)

        # Verify that the mocks were called
        mock_get_optional_material_data_by_spell_id.assert_called_once()

class TestGetOptionalMaterialDataBySpellId(TestCase):
    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_get_optional_material_data_by_spell_id(self, mock_load_data_from_cache):
        # Set up mocks
        mock_load_data_from_cache.return_value = [
            ["", "1", "0", "0", "1", "10", "1", "1"],
            ["", "1", "1", "1", "2", "50", "2", "2"],
        ]

        # Call the function
        materials = get_optional_material_data_by_spell_id()
        self.maxDiff = None
        # Check the results
        expected_materials = {
            1:  [
                    {
                        "display_order": 0,
                        "modified_crafting_reagent_slot" : 0,
                        "quantity": 10,
                        "recraft_quantity": 1,
                    },
                    {
                        "display_order": 1,
                        "modified_crafting_reagent_slot" : 1,
                        "quantity": 50,
                        "recraft_quantity": 2,
                    },
            ]
        }
        self.assertEqual(materials, expected_materials)

        # Verify that the mocks were called
        mock_load_data_from_cache.assert_called_once()

class TestInsertModifiedCraftingCategories(TestCase):
    def test_insert_modified_crafting_categories(self):
        # Set up input data
        MCC_data = [
            [1, "Category 1", "Category 1 description"],
            [2, "Category 2", "Category 2 description"],
        ]

        # Call the function
        categories =  async_to_sync(insert_modified_crafting_categories)(MCC_data)

        # Check the results
        self.assertEqual(len(categories), len(MCC_data))

        for index, category in enumerate(categories):
            self.assertEqual(category.id, MCC_data[index][0])
            self.assertEqual(category.name, MCC_data[index][1])
            self.assertEqual(category.description, MCC_data[index][2])

class TestInsertCategoryReagentSlotRelationship(TestCase):
    def setUpTestData():
            models.ModifiedCraftingCategory.objects.create(id=1, name="Category 1", description="Category 1 description")
            models.ModifiedCraftingCategory.objects.create(id=2, name="Category 2", description="Category 2 description")
            models.ModifiedCraftingReagentSlot.objects.create(id=1, name="Slot 1")
            models.ModifiedCraftingReagentSlot.objects.create(id=2, name="Slot 2")

    def test_insert_CategoryReagentSlotRelationship(self):
        # Set up input data
        MCRSlotXMCRCategory_data = [
            [1, 1, 1, 1],
            [2, 1, 2, 2],
            [3, 2, 1, 2],
        ]

        # Call the function

        relationships = async_to_sync(insert_CategoryReagentSlotRelationship)(MCRSlotXMCRCategory_data)

        # Check the results
        self.assertEqual(len(relationships), len(MCRSlotXMCRCategory_data))

        for index, record in enumerate(relationships):
            self.assertEqual(record.category.id, MCRSlotXMCRCategory_data[index][1])
            self.assertEqual(record.order, MCRSlotXMCRCategory_data[index][2])
            self.assertEqual(record.reagent_slot.id, MCRSlotXMCRCategory_data[index][3])

        # Verify that the records were inserted into the database
        self.assertEqual(models.CategoryReagentSlotRelationship.objects.count(), 3)

class TestInsertModifiedCraftingReagentItems(TestCase):
    def setUpTestData():
        models.ModifiedCraftingCategory.objects.create(id=1, name="Category 1", description="Category 1 description"),
        models.ModifiedCraftingCategory.objects.create(id=2, name="Category 2", description="Category 2 description"),

    def test_insert_modified_crafting_reagent_items(self):
        # Set up input data
        modified_crafting_reagent_item_data = [
            [1, "Item 1 description", 1],
            [2, "Item 2 description", 1],
            [3, "Item 3 description", 2],
            [4, "item 4 description", 0]
        ]

        # Call the function
        items = async_to_sync(insert_modified_crafting_reagent_items)(modified_crafting_reagent_item_data)

        # Check the results
        expected_number_of_records = 3
        self.assertEqual(len(items), expected_number_of_records)

        for index, item in enumerate(items):
            self.assertEqual(item.id, modified_crafting_reagent_item_data[index][0])
            self.assertEqual(item.description, modified_crafting_reagent_item_data[index][1])
            self.assertEqual(item.modified_crafting_category.id, modified_crafting_reagent_item_data[index][2])

        # Verify that the records were inserted into the database
        for item in items:
            db_item = models.ModifiedCraftingReagentItem.objects.get(id=item.id)
            self.assertEqual(db_item, item)

class TestInsertDragonflightProfessionTree(TestCase):
    profession_trees_data = [
        {
            "name": "Test Profession",
            "id": 1,
            "categories": [
                {
                    "name": "Test Category",
                    "recipes": [
                        {
                            "name": "Test Recipe",
                            "id": 1
                        }
                    ]
                }
            ]
        }
    ]

    def setUpTestData():
        models.Spell.objects.create(id=2)
        models.CraftingData.objects.create(id=3)

    @patch("calculator.consume_api_async.get_spell_records_by_recipe_id")
    @patch("calculator.consume_api_async.get_crafting_data_record_by_spell_id")
    def test_insert_dragonflight_profession_tree(
        self,
        patched_get_crafting_data_record_by_spell_id,
        patched_get_spell_records_by_recipe_id,
        ):
        spell = models.Spell.objects.get(id=2)
        patched_get_spell_records_by_recipe_id.return_value = {1: spell}
        crafting_data = models.CraftingData.objects.get(id=3)
        patched_get_crafting_data_record_by_spell_id.return_value = {2: crafting_data}

        inserted_records = async_to_sync(insert_dragonflight_profession_tree)(self.profession_trees_data)

        self.assertEqual(len(inserted_records[0]), 1)  # Test ProfessionIndex records
        self.assertEqual(len(inserted_records[1]), 1)  # Test RecipeCategory records
        self.assertEqual(len(inserted_records[2]), 1)  # Test Recipe records

        profession_record = inserted_records[0][0]
        category_record = inserted_records[1][0]
        recipe_record = inserted_records[2][0]

        self.assertEqual(profession_record.name, "Test Profession")
        self.assertEqual(category_record.name, "Test Category")
        self.assertEqual(recipe_record.name, "Test Recipe")

        # Check the relationships
        self.assertEqual(category_record.profession, profession_record)
        self.assertEqual(recipe_record.recipe_category, category_record)

class TestInsertCraftingQualities(TestCase):
    csv_data = [
        [0, 1],
        [2, 3]
    ]

    def test_insert_crafting_qualitites(self):
        inserted_records = async_to_sync(insert_crafting_qualities)(self.csv_data)

        expected_records = [
            models.CraftingQuality(id=0, quality_tier=1),
            models.CraftingQuality(id=2, quality_tier=3)
            ]
        # Django doens't have ordering by default
        actual_records = [
            models.CraftingQuality.objects.get(id=0),
            models.CraftingQuality.objects.get(id=2)
        ]
        for expected_record, actual_record, inserted_record in zip(expected_records, actual_records, inserted_records):
            self.assertEqual(expected_record.id, actual_record.id)
            self.assertEqual(expected_record.quality_tier, actual_record.quality_tier)

            self.assertEqual(expected_record.id, inserted_record.id)
            self.assertEqual(expected_record.quality_tier, inserted_record.quality_tier)

class TestInsertOptionalMaterialCraftingstats(TestCase):
    csv_data = [
        ["Vibrant Polishing Cloth",1,30,0.07,'','','','',''],
        ["Chromatic Embroidery Thread",2,'',0.1,'','','','',0.16],
        ["Chromatic Embroidery Thread",3,'',0.1,'','','','',0.16],
        ["Salad on the Side",'','','',90,'','','','']
    ]

    def setUpTestData():
        quality1 = models.CraftingQuality.objects.create(id=1, quality_tier=1)
        quality2 = models.CraftingQuality.objects.create(id=2, quality_tier=2)
        quality3 = models.CraftingQuality.objects.create(id=3, quality_tier=3)

        models.Item.objects.create(id=1, name="Vibrant Polishing Cloth", quality=quality1)
        models.Item.objects.create(id=2, name="Chromatic Embroidery Thread", quality=quality2)
        models.Item.objects.create(id=3, name="Chromatic Embroidery Thread", quality=quality3)
        models.Item.objects.create(id=4, name="Salad on the Side", quality=None)

    @patch('calculator.consume_api_async.load_data_from_cache')
    async def test_insert_optional_material_crafting_stats(self, patched_load_data_from_cache):
        patched_load_data_from_cache.return_value = self.csv_data

        returned_records = await insert_optional_material_crafting_stats(patched_load_data_from_cache)

        item_1 = await models.Item.objects.aget(id=1)
        item_2 = await models.Item.objects.aget(id=2)
        item_3 = await models.Item.objects.aget(id=3)
        item_4 = await models.Item.objects.aget(id=4)

        expected_crafting_stats_1 = models.CraftingStats(
            item = item_1,
            inspiration = 30,
            skill_from_inspiration = 0.07,
            multicraft = None,
            resourcefulness = None,
            increase_material_from_resourcefulness = None,
            skill = None,
            crafting_speed = None
        )
        expected_crafting_stats_2 = models.CraftingStats(
            item = item_2,
            inspiration = None,
            skill_from_inspiration = 0.1,
            multicraft = None,
            resourcefulness = None,
            increase_material_from_resourcefulness = None,
            skill = None,
            crafting_speed = 0.16
        )
        expected_crafting_stats_3 = models.CraftingStats(
            item = item_3,
            inspiration = None,
            skill_from_inspiration = 0.1,
            multicraft = None,
            resourcefulness = None,
            increase_material_from_resourcefulness = None,
            skill = None,
            crafting_speed = 0.16
        )
        expected_crafting_stats_4 = models.CraftingStats(
            item = item_4,
            inspiration = None,
            skill_from_inspiration = None,
            multicraft = 90,
            resourcefulness = None,
            increase_material_from_resourcefulness = None,
            skill = None,
            crafting_speed = None
        )

        expected_records = [
            expected_crafting_stats_1,
            expected_crafting_stats_2,
            expected_crafting_stats_3,
            expected_crafting_stats_4
        ]

        for expected_record, returned_record in zip(expected_records, returned_records):
            self.assertEqual(expected_record.item, returned_record.item)
            self.assertEqual(expected_record.inspiration, returned_record.inspiration)
            self.assertEqual(expected_record.skill_from_inspiration, returned_record.skill_from_inspiration)
            self.assertEqual(expected_record.multicraft, returned_record.multicraft)
            self.assertEqual(expected_record.resourcefulness, returned_record.resourcefulness)
            self.assertEqual(expected_record.increase_material_from_resourcefulness, returned_record.increase_material_from_resourcefulness)
            self.assertEqual(expected_record.skill, returned_record.skill)
            self.assertEqual(expected_record.crafting_speed, returned_record.crafting_speed)

class TestInsertProfessionEffectType(TestCase):
    test_data = [
        [1, "Skill", 0],
        [2, "Test", 1]
    ]

    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_insert_profession_effect_type(self, mocked_load_data):
        mocked_load_data.return_value = self.test_data
        
        returned_records = insert_profession_effect_type(mocked_load_data)

        expected_profession_effect_type_1 = models.ProfessionEffectType(
            id=0, name="Skill"
        )
        expected_profession_effect_type_2 = models.ProfessionEffectType(
            id=1, name="Test"
        ) 

        expected_records = [
            expected_profession_effect_type_1,
            expected_profession_effect_type_2
        ]

        for expected, actual in zip(expected_records, returned_records):
            self.assertEqual(expected.id, actual.id)
            self.assertEqual(expected.name, actual.name)

class TestInsertProfessionEffect(TestCase):
    test_data = [
        [1, 2, 0, 3],
        [4, 5, 90, 6],
        [7, 8, 13, 0]
    ]

    def setUpTestData():
        models.ProfessionEffectType.objects.create(id=2, name="Test1")
        models.ProfessionEffectType.objects.create(id=5, name="Test2")
        models.ProfessionEffectType.objects.create(id=8, name="Test3")

        models.ModifiedCraftingReagentSlot.objects.create(id=3)
        models.ModifiedCraftingReagentSlot.objects.create(id=6)

    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_insert_profession_effect(self, mocked_load_data):
        mocked_load_data.return_value = self.test_data
        
        returned_records = insert_profession_effect(mocked_load_data)

        profession_effect_types = models.ProfessionEffectType.objects.all()
        modified_crafting_reagent_slots = models.ModifiedCraftingReagentSlot.objects.all()

        expected_profession_effect_1 = models.ProfessionEffect(
            id=1, profession_effect_type=profession_effect_types[0], 
            amount=0, MCR_slot=modified_crafting_reagent_slots[0]
        )
        expected_profession_effect_2 = models.ProfessionEffect(
            id=4, profession_effect_type=profession_effect_types[1], 
            amount=90, MCR_slot=modified_crafting_reagent_slots[1]
        ) 
        expected_profession_effect_3 = models.ProfessionEffect(
            id=7, profession_effect_type=profession_effect_types[2], 
            amount=13, MCR_slot=None
        ) 

        expected_records = [
            expected_profession_effect_1,
            expected_profession_effect_2,
            expected_profession_effect_3
        ]

        for expected, actual in zip(expected_records, returned_records):
            self.assertEqual(expected.id, actual.id)
            self.assertEqual(expected.profession_effect_type, actual.profession_effect_type)
            self.assertEqual(expected.amount, actual.amount)
            self.assertEqual(expected.MCR_slot, actual.MCR_slot)

class TestInsertCraftingReagentEffect(TestCase):
    test_data = [
        [1, 2, 0, 3],
        [4, 5, 1, 6]
    ]

    def setUpTestData():
        models.ProfessionEffect.objects.create(id=2)
        models.ProfessionEffect.objects.create(id=5)

        models.ModifiedCraftingCategory.objects.create(id=3)
        models.ModifiedCraftingCategory.objects.create(id=6)

    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_insert_crafting_reagent_effect(self, mocked_load_data):
        mocked_load_data.return_value = self.test_data
        
        returned_records = insert_crafting_reagent_effect(mocked_load_data)

        profession_effect = models.ProfessionEffect.objects.all()
        modified_crafting_category = models.ModifiedCraftingCategory.objects.all()

        expected_profession_effect_1 = models.CraftingReagentEffect(
            id=1, profession_effect=profession_effect[0], 
            order=0, modified_crafting_category=modified_crafting_category[0]
        )
        expected_profession_effect_2 = models.CraftingReagentEffect(
            id=4, profession_effect=profession_effect[1], 
            order=1, modified_crafting_category=modified_crafting_category[1]
        ) 

        expected_records = [
            expected_profession_effect_1,
            expected_profession_effect_2
        ]

        for expected, actual in zip(expected_records, returned_records):
            self.assertEqual(expected.id, actual.id)
            self.assertEqual(expected.profession_effect, actual.profession_effect)
            self.assertEqual(expected.order, actual.order)
            self.assertEqual(expected.modified_crafting_category, actual.modified_crafting_category)

class TestInsertCraftingReagentQuality(TestCase):
    test_data = [
        #ID	OrderIndex	ItemID 	MaxDifficultyAdjustment	ReagentEffectPct	ModifiedCraftingCategoryID  
        [1, 0, 111, 2, 3, 4],
        [5, 1, 222, 3, 4, 4],
        [6, 0, 333, 7, 8, 5]
    ]

    def setUpTestData():
        models.Item.objects.create(id=111)
        models.Item.objects.create(id=222)
        models.Item.objects.create(id=333)

        models.ModifiedCraftingCategory.objects.create(id=4)
        models.ModifiedCraftingCategory.objects.create(id=5)

    @patch('calculator.consume_api_async.load_data_from_cache')
    def test_insert_crafting_reagent_quality(self, mocked_load_data):
        mocked_load_data.return_value = self.test_data
        
        returned_records = insert_crafting_reagent_quality(mocked_load_data)

        items = models.Item.objects.all()
        modified_crafting_categories = models.ModifiedCraftingCategory.objects.all()

        expected_crafting_reagent_quality_1 = models.CraftingReagentQuality(
            id=1, item=items[0], order=0, 
            difficulty_adjustment=2, 
            reagent_effect_percent=3,
            modified_crafting_category=modified_crafting_categories[0]
        )
        expected_crafting_reagent_quality_2 = models.CraftingReagentQuality(
            id=5, item=items[1], order=1, 
            difficulty_adjustment=3, 
            reagent_effect_percent=4,
            modified_crafting_category=modified_crafting_categories[0]
        ) 
        expected_crafting_reagent_quality_3 = models.CraftingReagentQuality(
            id=6, item=items[2], order=0, 
            difficulty_adjustment=7, 
            reagent_effect_percent=8,
            modified_crafting_category=modified_crafting_categories[1]
        ) 

        expected_records = [
            expected_crafting_reagent_quality_1,
            expected_crafting_reagent_quality_2,
            expected_crafting_reagent_quality_3
        ]

        for expected, actual in zip(expected_records, returned_records):
            self.assertEqual(expected.id, actual.id)
            self.assertEqual(expected.order, actual.order)
            self.assertEqual(expected.item, actual.item)
            self.assertEqual(expected.difficulty_adjustment, actual.difficulty_adjustment)
            self.assertEqual(expected.reagent_effect_percent, actual.reagent_effect_percent)
            self.assertEqual(expected.modified_crafting_category, actual.modified_crafting_category)
