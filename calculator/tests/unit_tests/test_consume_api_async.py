from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from unittest import skip, IsolatedAsyncioTestCase
from unittest import TestCase as UnittestTestCase
from textwrap import dedent
import json
import os


from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase
from getwowdataasync import urls, convert_to_datetime, WowApi
from calculator import models
from calculator import create_paths
from calculator import consume_api_async
from calculator.consume_api_async import *
from calculator.exceptions import MissingItemRecordError
from freezegun import freeze_time

# TODO these are acutllay integrated tests. Organize files different?

class Test(IsolatedAsyncioTestCase):
    async def test_insert_all_data(self):
        WowApi.create = AsyncMock(return_value=1)
        insert_all_connected_realm_index_records = consume_api_async.insert_all_connected_realm_index_records = AsyncMock()
        insert_regions = consume_api_async.insert_regions = AsyncMock()
        insert_all_realms = consume_api_async.insert_all_realms = AsyncMock()
        insert_modified_crafting_reagent_slot = consume_api_async.insert_modified_crafting_reagent_slot = AsyncMock()
        insert_all_dragonflight_items = consume_api_async.insert_all_dragonflight_items = AsyncMock()
        insert_optional_material_crafting_stats = consume_api_async.insert_optional_material_crafting_stats = AsyncMock()
        insert_dragonflight_profession_tree = consume_api_async.insert_dragonflight_profession_tree = AsyncMock()

        await insert_all_data()

        insert_all_connected_realm_index_records.assert_awaited()
        insert_regions.assert_awaited()
        insert_all_realms.assert_awaited()
        insert_modified_crafting_reagent_slot.assert_awaited()
        insert_all_dragonflight_items.assert_awaited()
        insert_optional_material_crafting_stats.assert_awaited()
        insert_dragonflight_profession_tree.assert_awaited()

    async def test_insert_all_connected_realm_index_records(self):
        wow_api = WowApi()
        mocked_get_connected_realm_index = wow_api.get_connected_realm_index = AsyncMock()
        create_paths.create_json_path = MagicMock(return_value="/")
        mocked__if_json_file_doesnt_exist_create_one = consume_api_async._if_json_file_doesnt_exist_create_one = AsyncMock()
        mocked__insert_all_connected_realm_index_records = consume_api_async._insert_all_connected_realm_index_records = MagicMock(
            return_value = []
        )

        with patch("os.remove"):
            actual_records = await insert_all_connected_realm_index_records(wow_api)
        expected_records = []

        self.assertEqual(expected_records, actual_records)

    # def test_get_data_from_csv(self):
    #     mock_csv_path = r".\test.csv"
    #     with open(mock_csv_path, "w", encoding='utf-8-sig') as mock_file:
    #         mock_file.write("1")
    #     mock_callable = MagicMock(
    #         return_value="success"
    #     )
        
    #     actual_return = get_data_from_csv(mock_csv_path, mock_callable)
    #     expected_return = "success"

    #     self.assertEqual(expected_return, actual_return)
    #     mock_callable.assert_called_once()

# class TestConnectedRealmsIndexInsertClass(TestCase):
#     def setUp(self) -> None:
#         WowApi._get_access_token = AsyncMock(return_value='DummyAccessToken')
#         self.insert_test = async_to_sync(ConnectedRealmsIndex.create)('testregion')

#     def tearDown(self) -> None:
#         async_to_sync(self.insert_test.wowapi.close)()

#     def test_ConnectedRealmsIndex_create(self):
#         # connected_realms_index_obj = async_to_sync(ConnectedRealmsIndex.create)('testregion')
#         # print(type(connected_realms_index_obj))
#         x = ConnectedRealmsIndex()
#         print(dir(x))
#         print(x.self)

#     def test_insert_connected_realms_index(self):
#         pass

#     def test__insert_connected_realms_index(self):
#         pass


# class TestInsertIntoCleanDB(TestCase):
#     def setUp(self) -> None:
#         WowApi._get_access_token = AsyncMock(return_value='DummyAccessToken')
#         self.insert_test = async_to_sync(Insert.create)('testregion')

#     def tearDown(self) -> None:
#         async_to_sync(self.insert_test.wowapi.close)()

#     def test__insert_connected_realms_index(self):
#         mock_connected_realm_index_json = dedent(
#         """
#             {
#                 "connected_realms": [
#                     {
#                         "href": "https://us.api.blizzard.com/data/wow/connected-realm/121?namespace=dynamic-us"
#                     }
#                 ]
#             }
#         """
#         ).strip()
#         json_data = mock_open(read_data=mock_connected_realm_index_json)
#         with patch('builtins.open', json_data):
#             actual_record = self.insert_test._insert_connected_realms_index()[0]
            
#         expected_record = ConnectedRealmsIndex(connected_realm_id=121)
#         self.assertEqual(expected_record.connected_realm_id, int(actual_record.connected_realm_id))

#     async def test_insert_regions(self):
#         await self.insert_test.insert_regions()

#         expected_regions = ['us', 'eu', 'kr']
#         actual_na = await Region.objects.aget(region='us')
#         actual_eu = await Region.objects.aget(region='eu')
#         actual_kr = await Region.objects.aget(region='kr')

#         await sync_to_async(self.assertEqual)(expected_regions[0], actual_na.region)
#         await sync_to_async(self.assertEqual)(expected_regions[1], actual_eu.region)
#         await sync_to_async(self.assertEqual)(expected_regions[2], actual_kr.region)

#     def test__insert_all_realms(self):
#         mock_connected_realm_index = ConnectedRealmsIndex.objects.create(connected_realm_id=1)
#         mock_region = Region.objects.create(region="testregion")
#         mock_all_realms_json = dedent(
#             """
#             [
#                 {
#                 "id": "1",
#                 "population": {"type": "FULL"},
#                 "realms": [
#                     {
#                         "id": "1",
#                         "region": {"name": "testregion"},
#                         "timezone": "America/New_York",
#                         "type": {"type": "NORMAL"},
#                         "slug": "TestServer 1"
#                     },
#                     {
#                         "id": "2",
#                         "region": {"name": "testregion"},
#                         "timezone": "America/New_York",
#                         "type": {"type": "NORMAL"},
#                         "slug": "TestServer 2" 
#                     }
#                 ]
#                 }
#             ]
#             """
#         ).strip()
#         json_data = mock_open(read_data=mock_all_realms_json)
#         with patch('builtins.open', json_data):
#             actual_records = self.insert_test._insert_all_realms()

#         expected_records = [
#             Realm(
#                 realm_id = 1,
#                 connected_realm = mock_connected_realm_index,
#                 population = "FULL",
#                 name = "TestServer 1",
#                 region = mock_region,
#                 timezone = "America/New_York",
#                 play_style = "NORMAL",
#             ),
#             Realm(
#                 realm_id = 2,
#                 connected_realm = mock_connected_realm_index,
#                 population = "FULL",
#                 name = "TestServer 2",
#                 region = mock_region,
#                 timezone = "America/New_York",
#                 play_style = "NORMAL",
#             )
#         ]

#         for index in range(len(actual_records)):
#             expected_record = expected_records[index]
#             actual_record = actual_records[index]
#             self.assertEqual(expected_record.realm_id, int(actual_record.realm_id))
#             self.assertEqual(expected_record.connected_realm, actual_record.connected_realm)
#             self.assertEqual(expected_record.population, actual_record.population)
#             self.assertEqual(expected_record.name, actual_record.name)
#             self.assertEqual(expected_record.region, actual_record.region)
#             self.assertEqual(expected_record.timezone, actual_record.timezone)
#             self.assertEqual(expected_record.play_style, actual_record.play_style)

#     async def test_insert_modified_crafting_reagent_slot(self):
#         self.insert_test.wowapi.get_modified_crafting_reagent_slot_type_index = AsyncMock(return_value=
#             {
#                 "slot_types": [
#                     {
#                         "name": "test_name_1",
#                         "id": 1
#                     },
#                     {
#                         "id": 2
#                     }
#                 ]
#             }
#         )
#         actual_records = await self.insert_test.insert_modified_crafting_reagent_slot()
#         expected_records = [
#             OptionalMaterialSlot(
#                 name="test_name_1", id=1
#             ),
#             OptionalMaterialSlot(
#                 id=2
#             )
#         ]
#         self.assertEqual(expected_records, actual_records)

#     @skip
#     @freeze_time("2023-1-1 2:32:00", as_kwarg="frozen_time", tz_offset=-5)
#     def test_insert_auctions(self, frozen_time):
#         connected_realm_id = 1
#         connected_realm = ConnectedRealmsIndex.objects.create(connected_realm_id=connected_realm_id)
#         item = Item.objects.create(id=1)
#         item = Item.objects.create(id=2)
#         region = Region.objects.create(region=self.insert_test.wowapi.region)

#         self.insert_test.wowapi.get_auctions = AsyncMock(
#             return_value={
#                 "auctions": [
#                     { # all potential fields
#                         "id": 1,
#                         "buyout": 1,
#                         "bid": 1,
#                         "quantity": 1,
#                         "time_left": "SHORT",
#                         "item": {
#                             "id": 1,
#                             "pet_level": 1,
#                             "bonus_lists": [1, 2],
#                             "modifiers" : [{"type": 1, "value" : 2}]
#                         },
#                     },
#                     { # no bid, bonus, modifiers, pet level
#                         "id": 2,
#                         "buyout": 2,
#                         "quantity": 2,
#                         "time_left": "SHORT",
#                         "item": {
#                             "id": 2,
#                         },
#                     }
#                 ],
#             }
#         )

#         self.insert_test.insert_auctions(connected_realm_id)
#         actual_record = list(Auction.objects.all().values())
#         timestamp = frozen_time.time_to_freeze.today()

#         expected_record = [
#             {
#                 "auction_id": 1,
#                 "buyout": 1,
#                 "quantity": 1,
#                 "time_left": "SHORT",
#                 "timestamp": timestamp,
#                 "connected_realm_id": 1,
#                 "item_id": 1,
#                 "bonus_list_id" : 1,
#                 "modifier_list_id" : 1,
#                 "pet_level": 1,
#                 "region_id": self.insert_test.wowapi.region
#             },
#             {
#                 "auction_id": 2,
#                 "buyout": 2,
#                 "quantity": 2,
#                 "time_left": "SHORT",
#                 "timestamp": timestamp,
#                 "connected_realm_id": 1,
#                 "bonus_list_id": None,
#                 "modifier_list_id": None,
#                 "pet_level": None,
#                 "item_id": 2,
#                 "region_id": self.insert_test.wowapi.region
#             }
#         ]
#         self.assertEqual(expected_record, actual_record)

#     @skip
#     @freeze_time("2023-1-1 2:32:00", as_kwarg="frozen_time", tz_offset=-5)
#     def test_insert_commodities(self, frozen_time):
#         item1 = Item.objects.create(id=1)
#         item2 = Item.objects.create(id=2)
#         region = Region.objects.create(region=self.insert_test.wowapi.region)
#         timestamp = frozen_time.time_to_freeze.today()

#         self.insert_test.wowapi.get_commodities = AsyncMock(return_value = {
#                 "auctions" : [
#                     {
#                         "id" : 1,
#                         "item" : {"id" : 1},
#                         "quantity" : 1,
#                         "unit_price" : 1,
#                         "time_left" : "SHORT"
#                     },
#                     {
#                         "id" : 2,
#                         "item" : {"id" : 2},
#                         "quantity" : 2,
#                         "unit_price" : 2,
#                         "time_left" : "SHORT" 
#                     }
#                 ]
#             }
#         )
#         self.insert_test.insert_commodities()
#         actual_record = list(Auction.objects.all().values())
#         expected_record = [
#             {
#                 "auction_id": 1,
#                 "buyout": 1,
#                 "quantity": 1,
#                 "time_left": "SHORT",
#                 "timestamp": timestamp,
#                 "connected_realm_id": None,
#                 "bonus_list_id": None,
#                 "modifier_list_id": None,
#                 "pet_level": None,
#                 "item_id": 1,
#                 "region_id": self.insert_test.wowapi.region
#             },
#             {
#                 "auction_id": 2,
#                 "buyout": 2,
#                 "quantity": 2,
#                 "time_left": "SHORT",
#                 "timestamp": timestamp,
#                 "connected_realm_id": None,
#                 "bonus_list_id": None,
#                 "modifier_list_id": None,
#                 "pet_level": None,
#                 "item_id": 2,
#                 "region_id": self.insert_test.wowapi.region
#             }
#         ]
#         self.assertEqual(expected_record, actual_record)

#     def test_get_all_spells(self):
#         expected_spell_name_csv = dedent("""
#             Id,Name_lang
#             1,Word of Recall (OLD)
#             365731,Primal Molten Spellblade
#             """).strip()
#         csv_data = mock_open(read_data=expected_spell_name_csv)
#         with patch('builtins.open', csv_data):
#             acutal_records = self.insert_test.get_all_spells()

#         expected_records = {
#             "Word of Recall (OLD)" : 1,
#             "Primal Molten Spellblade" : 365731
#             }
#         self.assertEqual(expected_records, acutal_records)

#     def test_get_all_spells_with_same_spell_name(self):
#         expected_spell_name_csv = dedent("""
#             Id,Name_lang
#             1,Word of Recall (OLD)
#             365731,Primal Molten Spellblade
#             365732,Primal Molten Spellblade
#             """).strip()
#         csv_data = mock_open(read_data=expected_spell_name_csv)
#         with patch('builtins.open', csv_data):
#             acutal_records = self.insert_test.get_all_spells()

#         expected_records = {
#             "Word of Recall (OLD)": 1,
#             "Primal Molten Spellblade" : [365731, 365732]
#             }
#         self.assertEqual(expected_records, acutal_records)

#     def test_get_all_spells_with_many_of_same_spell_name(self):
#         expected_spell_name_csv = dedent("""
#             Id,Name_lang
#             1,Word of Recall (OLD)
#             365731,Primal Molten Spellblade
#             365732,Primal Molten Spellblade
#             365733,Primal Molten Spellblade

#             """).strip()
#         csv_data = mock_open(read_data=expected_spell_name_csv)
#         with patch('builtins.open', csv_data):
#             acutal_records = self.insert_test.get_all_spells()

#         expected_records = {
#             "Word of Recall (OLD)": 1,
#             "Primal Molten Spellblade" : [365731, 365732, 365733]
#             }
#         self.assertEqual(expected_records, acutal_records)

#     async def test_insert_optional_material_crafting_stats_with_more_than_1_item(self):
#         expected_crafting_stats_csv = dedent(
#             """
#             item,quality,inspiration,skill from inspiration,multicraft,resourcefulness,increase materials saved from resourcefulness,skill,crafting speed
#             Vibrant Polishing Cloth,1,30,0.07,,,,,
#             Lesser Illusterious Insight,,,,,,,30,
#             Agitating Potion Augmentation,2,40,,36,,,,
#             Brood Salt,1,30,,,,,,0.12
#             Shimmering Embroidery Thread,3,,,,,0.25,,
#             """
#         ).strip()
#         expected_items = await Item.objects.abulk_create(
#             [
#                 Item(id=1, name="Vibrant Polishing Cloth", quality=1),
#                 Item(id=2, name="Lesser Illusterious Insight"),
#                 Item(id=3, name="Agitating Potion Augmentation", quality=2),
#                 Item(id=4, name="Brood Salt", quality=3),
#                 Item(id=5, name="Shimmering Embroidery Thread", quality=1)
#             ]
#         )
#         csv_data = mock_open(read_data=expected_crafting_stats_csv)
#         with patch('builtins.open', csv_data):
#             actual_records = await self.insert_test.insert_optional_material_crafting_stats()

#         expected_records = [
#             CraftingStats(id=1, item=expected_items[0], inspiration=30, skill_from_inspiration= 0.07, multicraft=None, resourcefulness=None, increase_material_from_resourcefulness=None, skill= None, crafting_speed=None),
#             CraftingStats(id=2, item=expected_items[1], inspiration=None, skill_from_inspiration=None, multicraft=None, resourcefulness=None ,increase_material_from_resourcefulness=None, skill=30, crafting_speed=None),
#             CraftingStats(id=3, item=expected_items[2], inspiration=40, skill_from_inspiration=None, multicraft=36, resourcefulness=None , increase_material_from_resourcefulness=None, skill=None, crafting_speed=None),
#             CraftingStats(id=4, item=expected_items[3], inspiration= 30, skill_from_inspiration= None, multicraft= None, resourcefulness=None ,increase_material_from_resourcefulness=None, skill=None, crafting_speed=0.12),
#             CraftingStats(id=5, item=expected_items[4], inspiration= None, skill_from_inspiration= None, multicraft= None, resourcefulness=None, increase_material_from_resourcefulness=0.25, skill=None, crafting_speed=None)
#             ]
#         for index in range(len(expected_records)):
#             self.assertEqual(expected_records[index].item, actual_records[index].item)
#             self.assertEqual(expected_records[index].inspiration, actual_records[index].inspiration)
#             self.assertEqual(expected_records[index].skill_from_inspiration, actual_records[index].skill_from_inspiration)
#             self.assertEqual(expected_records[index].multicraft, actual_records[index].multicraft)
#             self.assertEqual(expected_records[index].resourcefulness, actual_records[index].resourcefulness)
#             self.assertEqual(expected_records[index].increase_material_from_resourcefulness, actual_records[index].increase_material_from_resourcefulness)
#             self.assertEqual(expected_records[index].skill, actual_records[index].skill)
#             self.assertEqual(expected_records[index].crafting_speed, actual_records[index].crafting_speed)

#     async def test_insert_optional_material_crafting_stats_with_1_item(self):
#         expected_crafting_stats_csv = dedent(
#             """
#             item,quality,inspiration,skill from inspiration,multicraft,resourcefulness,increase materials saved from resourcefulness,skill,crafting speed
#             Lesser Illusterious Insight,,,,,,,30,
#             """
#         ).strip()
#         expected_items = await Item.objects.abulk_create(
#             [
#                 Item(id=2, name="Lesser Illusterious Insight"),
#             ]
#         )
#         csv_data = mock_open(read_data=expected_crafting_stats_csv)
#         with patch('builtins.open', csv_data):
#             actual_records = await self.insert_test.insert_optional_material_crafting_stats()

#         expected_records = [
#             CraftingStats(id=2, item=expected_items[0], inspiration=None, skill_from_inspiration=None, multicraft=None, resourcefulness=None ,increase_material_from_resourcefulness=None, skill=30, crafting_speed=None),
#             ]

#         self.assertEqual(expected_records[0].item, actual_records[0].item)
#         self.assertEqual(expected_records[0].inspiration, actual_records[0].inspiration)
#         self.assertEqual(expected_records[0].skill_from_inspiration, actual_records[0].skill_from_inspiration)
#         self.assertEqual(expected_records[0].multicraft, actual_records[0].multicraft)
#         self.assertEqual(expected_records[0].resourcefulness, actual_records[0].resourcefulness)
#         self.assertEqual(expected_records[0].increase_material_from_resourcefulness, actual_records[0].increase_material_from_resourcefulness)
#         self.assertEqual(expected_records[0].skill, actual_records[0].skill)
#         self.assertEqual(expected_records[0].crafting_speed, actual_records[0].crafting_speed)

#     async def test_insert_optional_material_crafting_stats_with_no_items(self):
#         expected_crafting_stats_csv = dedent(
#             """
#             item,quality,inspiration,skill from inspiration,multicraft,resourcefulness,increase materials saved from resourcefulness,skill,crafting speed
#             Vibrant Polishing Cloth,1,30,0.07,,,,,
#             Lesser Illusterious Insight,,,,,,,30,
#             Agitating Potion Augmentation,2,40,,36,,,,
#             Brood Salt,1,30,,,,,,0.12
#             Shimmering Embroidery Thread,3,,,,,0.25,,
#             """
#         ).strip()
#         csv_data = mock_open(read_data=expected_crafting_stats_csv)
#         with self.assertRaises(MissingItemRecordError):
#             with patch('builtins.open', csv_data):
#                 await self.insert_test.insert_optional_material_crafting_stats()

#     def test_convert_to_int_or_none_returns_a_int(self):
#         actual_return = self.insert_test.convert_to_int_or_none("1")
#         expected_return = 1

#         self.assertEqual(expected_return, actual_return)
    
#     def test_convert_to_int_or_none_returns_none(self):
#         actual_return = self.insert_test.convert_to_int_or_none("a")
#         expected_return = None

#         self.assertEqual(expected_return, actual_return)

#     def test_convert_to_float_or_none_returns_a_float(self):
#         actual_return = self.insert_test.convert_to_float_or_none("1.1")
#         expected_return = 1.1

#         self.assertEqual(expected_return, actual_return)

#     def test_convert_to_float_or_none_returns_none(self):
#         actual_return = self.insert_test.convert_to_float_or_none("a")
#         expected_return = None

#         self.assertEqual(expected_return, actual_return)

#     def test__insert_all_dragonflight_items(self):
#         mock_dragonflight_items = dedent(
#             """
#             [
#                 {
#                     "id":1,
#                     "name": "test name 1",
#                     "purchase_price": 1,
#                     "sell_price":1,
#                     "preview_item" :
#                         {
#                             "binding":{"name": "Bind on pickup"}
#                         },
#                     "purchase_quantity":1,
#                     "modified_crafting" :
#                         {
#                            "id": 1 
#                         }
#                 },
#                 {
#                     "id":2,
#                     "name": "test name 2",
#                     "purchase_price": 2,
#                     "sell_price":2,
#                     "purchase_quantity":2 
#                 },
#                 {
#                     "id":3,
#                     "name": "test name 3",
#                     "purchase_price": 3,
#                     "sell_price":3,
#                     "purchase_quantity":3, 
#                     "preview_item" :
#                         {}
#                 }
#             ]
#         """).strip()
#         self.insert_test.get_all_item_crafting_qualities = MagicMock(return_value=
#             {
#                 1:1
#             }
#         )
#         csv_data = mock_open(read_data=mock_dragonflight_items)
#         with patch('builtins.open', csv_data):
#             actual_records = self.insert_test._insert_all_dragonflight_items()

#             mock_optional_material = OptionalMaterialSlot(id=1, name="Test slot")

#             expected_records = [
#                 Item(
#                     id=1,
#                     name="test name 1",
#                     vendor_buy_price=1,
#                     vendor_sell_price=1,
#                     vendor_buy_quantity=1,
#                     quality=1,
#                     binding="Bind on pickup",
#                     optional_material_slot=mock_optional_material
#                 ),
#                 Item(
#                     id=2,
#                     name="test name 2",
#                     vendor_buy_price=2,
#                     vendor_sell_price=2,
#                     vendor_buy_quantity=2,
#                     quality=None,
#                     binding=None,
#                     optional_material_slot_id=None
#                 ),
#                 Item(
#                     id=3,
#                     name="test name 3",
#                     vendor_buy_price=3,
#                     vendor_sell_price=3,
#                     vendor_buy_quantity=3,
#                     quality=None,
#                     binding=None,
#                     optional_material_slot_id=None
#                 )
#             ]

#             for index in range(len(actual_records)):
#                 expected_record = expected_records[index]
#                 actual_record = actual_records[index]
#                 self.assertEqual(expected_record.id, actual_record.id)
#                 self.assertEqual(expected_record.vendor_buy_price, actual_record.vendor_buy_price)
#                 self.assertEqual(expected_record.vendor_sell_price, actual_record.vendor_sell_price)
#                 self.assertEqual(expected_record.vendor_buy_quantity, actual_record.vendor_buy_quantity)
#                 self.assertEqual(expected_record.quality, actual_record.quality)
#                 self.assertEqual(expected_record.name, actual_record.name)
#                 self.assertEqual(expected_record.binding, actual_record.binding)
#                 self.assertEqual(expected_record.optional_material_slot, actual_record.optional_material_slot)

#     def test_get_all_item_crafting_qualities(self):
#         expected_modified_crafting_items_csv = dedent(
#         """
#         ItemID, ItemQualityLevel,
#         2, 0, 2
#         4, 0, 1
#         """
#         ).strip()
#         csv_data = mock_open(read_data=expected_modified_crafting_items_csv)
#         with patch('builtins.open', csv_data):
#             acutal_returns = self.insert_test.get_all_item_crafting_qualities()

#         expected_returns = {
#             2: 2,
#             4: 1
#         }
#         self.assertEqual(expected_returns, acutal_returns)

#     async def test__insert_dragonflight_profession_tree(self):
#         self.insert_test._create_modified_crafting_material_info = MagicMock(return_value={
#             365731: {
#                 1:{
#                     "display_order" : 0,
#                     "quantity" : 1,
#                     "recraft_quantity" : 1
#                 },
#                 2:{
#                     "display_order" : 1,
#                     "quantity" : 2,
#                     "recraft_quantity" : 2

#                 }
#             }
#         })
#         mock_slot_1 = await OptionalMaterialSlot.objects.acreate(id=1, name="test slot 1")
#         mock_slot_2 = await OptionalMaterialSlot.objects.acreate(id=2, name="test slot 2")
#         mock_item = await Item.objects.acreate(id=1, name="Product Name")
#         self.insert_test.get_product_quantity = MagicMock(return_value={
#                 365731: 1
#             }
#         )
#         mock_profession_tree = dedent(
#         """
#         [
#             {
#                 "name" : "Test Profession 1",
#                 "id" : 1,
#                 "categories" : [
#                     {
#                         "name" : "Test Category Name",
#                         "recipes" : [
#                             {
#                                 "id" : 1,
#                                 "name" : "Product Name",
#                                 "reagents" : [
#                                     {
#                                         "reagent": {
#                                             "name": "Test mettle",
#                                             "id" : 2
#                                         },
#                                         "quantity" : 0
#                                     },
#                                     {
#                                         "reagent": {
#                                             "name": "Test spark",
#                                             "id" : 3
#                                         },
#                                         "quantity" : 1
#                                     }
#                                 ],
#                                 "modified_crafting_slots" : [
#                                     {
#                                         "slot_type" : {
#                                             "name" : "mat 1 (DNT)",
#                                             "id" : 1
#                                         },
#                                         "display_order" : 0
#                                     },
#                                     {
#                                         "slot_type" : {
#                                             "name" : "mat 2 (DNT)",
#                                             "id" : 2
#                                         },
#                                         "display_order" : 1
#                                     }
#                                 ]
#                             }
#                         ]
#                     },
#                     {
#                         "name": "Quest Plans",
#                         "recipes": ["bad recipe"]
#                     },
#                     {
#                         "name": "Quest Designs",
#                         "recipes": ["bad recipe"]
#                     }
#                 ]
#             }
#         ]
#         """
#         ).strip()
#         mock_profession = ProfessionIndex(
#                 name="Test Profession 1",
#                 id=1
#             )
#         self.insert_test._create_profession_index_record = MagicMock(
#             return_value = mock_profession
#             )
#         mock_profession_category = RecipeCategory(
#             name = "Test Category Name",
#             profession = mock_profession
#         )
#         self.insert_test._create_profession_category_record = MagicMock(
#             return_value = mock_profession_category
#             )
#         self.insert_test.get_recipe_spell_id_by_recipe_id = AsyncMock(
#             return_value=1
#         )  
#         mock_recipe = Recipe(
#                 id=1,
#                 name="Product Name",
#                 recipe_category=mock_profession_category,
#             )
#         self.insert_test._create_recipe_record = AsyncMock(
#             return_value = mock_recipe
#         )
#         mock_products = [
#             Product(
#                 item=mock_item,
#                 quantity=1,
#                 recipe=mock_recipe
#             )
#         ]
#         self.insert_test._create_product_record = AsyncMock(
#             return_value=mock_products
#         )
#         mock_materials = [
#                 Material(name="Test mettle", quantity=0, recraft_quantity=None, display_order=None, optional_material_slot=None, recipe=mock_recipe),
#                 Material(name="Test spark", quantity=1, recraft_quantity=None, display_order=None, optional_material_slot=None, recipe=mock_recipe),
#                 Material(name="mat 1 (DNT)", quantity=1, recraft_quantity=1, display_order=0, optional_material_slot=mock_slot_1, recipe=mock_recipe),
#                 Material(name="mat 2 (DNT)", quantity=2, recraft_quantity=2, display_order=1, optional_material_slot=mock_slot_2, recipe=mock_recipe)
#             ]
#         self.insert_test._create_crafting_material_records = AsyncMock(return_value = mock_materials)

#         csv_data = mock_open(read_data=mock_profession_tree)
#         with patch('builtins.open', csv_data):
#             actual_inserted_records = await self.insert_test._insert_dragonflight_profession_tree()

#         expected_professions = [
#             ProfessionIndex(id=1, name="Test Profession 1")
#         ]
#         expected_recipe_categories = [
#             RecipeCategory(name="Test Category Name", profession=expected_professions[0])
#         ]
#         expected_recipe = [
#             Recipe(id=1, name="Product Name", recipe_category=expected_recipe_categories[0])
#         ]
#         expected_products = mock_products
#         expected_materials = mock_materials

#         actual_inserted_profession_records = actual_inserted_records[0]
#         actual_inserted_category_records = actual_inserted_records[1]
#         actual_inserted_recipe_records = actual_inserted_records[2]
#         actual_inserted_product_records = actual_inserted_records[3]
#         actual_inserted_material_records = actual_inserted_records[4]

#         self.assertEqual(expected_professions, actual_inserted_profession_records)
#         self.assertEqual(expected_recipe_categories[0].name, actual_inserted_category_records[0].name)
#         self.assertEqual(expected_recipe, actual_inserted_recipe_records)
#         self.assertEqual(expected_products, actual_inserted_product_records)
#         for index in range(len(actual_inserted_material_records)):
#             actual_material_record = actual_inserted_material_records[index]
#             expected_material_record = expected_materials[index]
#             self.assertEqual(expected_material_record.name, actual_material_record.name)
#             self.assertEqual(expected_material_record.quantity, actual_material_record.quantity)
#             self.assertEqual(expected_material_record.recraft_quantity, actual_material_record.recraft_quantity)
#             self.assertEqual(expected_material_record.display_order, actual_material_record.display_order)
#             self.assertEqual(expected_material_record.optional_material_slot, actual_material_record.optional_material_slot)
#             self.assertEqual(expected_material_record.recipe, actual_material_record.recipe)

#     async def test__create_crafting_material_records(self):
#         mock_recipe_dict = {
#             "id" : 1,
#             "name" : "Product Name",
#             "reagents" : [
#                 {
#                     "reagent": {
#                         "name": "Test mettle",
#                         "id" : 2
#                     },
#                     "quantity" : 0
#                 },
#                 {
#                     "reagent": {
#                         "name": "Test spark",
#                         "id" : 3
#                     },
#                     "quantity" : 1
#                 }
#             ],
#             "modified_crafting_slots" : [
#                 {
#                     "slot_type" : {
#                         "name" : "mat 1 (DNT)",
#                         "id" : 1
#                     },
#                     "display_order" : 0
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 2 (DNT)",
#                         "id" : 2
#                     },
#                     "display_order" : 1
#                 }
#             ]
#         }
#         mock_all_modified_crafting_mats = {
#             365731: {
#                 1:{
#                     "display_order" : 0,
#                     "quantity" : 1,
#                     "recraft_quantity" : 1
#                 },
#                 2:{
#                     "display_order" : 1,
#                     "quantity" : 2,
#                     "recraft_quantity" : 2
#                 }
#             }
#         }
#         mock_slot_1 = await OptionalMaterialSlot.objects.acreate(id=1, name="test slot 1")
#         mock_slot_2 = await OptionalMaterialSlot.objects.acreate(id=2, name="test slot 2")
#         mock_all_crafting_slots = OptionalMaterialSlot.objects.all()
#         mock_profession = ProfessionIndex(
#                 name="Test Profession 1",
#                 id=1
#             )
#         mock_profession_category = RecipeCategory(
#             name = "Test Category Name",
#             profession = mock_profession
#         )
#         mock_item = await Item.objects.acreate(id=1, name="Product Name")
#         mock_recipe_record = Recipe(
#                 id=1,
#                 name="Product Name",
#                 recipe_category=mock_profession_category,
#             )
#         self.insert_test.get_recipe_spell_id_by_recipe_id = AsyncMock(return_value=1)
#         self.insert_test._get_list_of_recipe_materials = MagicMock(
#             return_value = [
#                 {
#                     "reagent": {
#                         "name": "Test mettle",
#                         "id" : 2
#                     },
#                     "quantity" : 0
#                 },
#                 {
#                     "reagent": {
#                         "name": "Test spark",
#                         "id" : 3
#                     },
#                     "quantity" : 1
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 1 (DNT)",
#                         "id" : 1
#                     },
#                     "display_order" : 0
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 2 (DNT)",
#                         "id" : 2
#                     },
#                     "display_order" : 1
#                 }
#             ]
#         )
#         self.insert_test._get_material_quantities = MagicMock(return_value = [1,2,3,4])
#         self.insert_test._create_modified_crafting_material_record = MagicMock(
#             return_value = Material()
#         )
#         self.insert_test._create_material_record = MagicMock(
#             return_value = Material()
#         )

#         actual_records = await self.insert_test._create_crafting_material_records(
#             mock_recipe_dict, mock_all_modified_crafting_mats, 
#             mock_all_crafting_slots, mock_recipe_record
#         )

#         expected_records = [
#             Material(), Material(),
#             Material(), Material()
#         ]
#         for index in range(len(actual_records)):
#             self.assertEqual(type(expected_records[index]), type(actual_records[index]))

#     def test__get_list_of_recipe_materials_with_both_reagents_and_modified_crafting_reagents(self):
#         mock_recipe = {
#             "id" : 1,
#             "name" : "Product Name",
#             "reagents" : [
#                 {
#                     "reagent": {
#                         "name": "Test mettle",
#                         "id" : 2
#                     },
#                     "quantity" : 0
#                 },
#                 {
#                     "reagent": {
#                         "name": "Test spark",
#                         "id" : 3
#                     },
#                     "quantity" : 1
#                 }
#             ],
#             "modified_crafting_slots" : [
#                 {
#                     "slot_type" : {
#                         "name" : "mat 1 (DNT)",
#                         "id" : 1
#                     },
#                     "display_order" : 0
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 2 (DNT)",
#                         "id" : 2
#                     },
#                     "display_order" : 1
#                 }
#             ]
#         }

#         actual_materials_list = self.insert_test._get_list_of_recipe_materials(mock_recipe)
#         expected_materials_list = [
#                 {
#                     "reagent": {
#                         "name": "Test mettle",
#                         "id" : 2
#                     },
#                     "quantity" : 0
#                 },
#                 {
#                     "reagent": {
#                         "name": "Test spark",
#                         "id" : 3
#                     },
#                     "quantity" : 1
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 1 (DNT)",
#                         "id" : 1
#                     },
#                     "display_order" : 0
#                 },
#                 {
#                     "slot_type" : {
#                         "name" : "mat 2 (DNT)",
#                         "id" : 2
#                     },
#                     "display_order" : 1
#                 }
#         ]

#         self.assertEqual(expected_materials_list, actual_materials_list)

#     def test__get_material_quantities(self):
#         mock_spell_id = 1
#         mock_crafting_slot_1 = 1
#         mock_crafting_slot_2 = 123
#         mock_all_modified_crafting_mats = {
#             mock_spell_id : {
#                 mock_crafting_slot_1: {"quantity":3},
#                 mock_crafting_slot_2: {"quantity":4}
#             }
#         }
#         mock_recipe_material_list = [
#             {"quantity": 1},
#             {"quantity": 2},
#             {"slot_type": {"id":1}},
#             {"slot_type": {"id":123}}
#         ]

#         actual_quantities = self.insert_test._get_material_quantities(
#             mock_spell_id, mock_recipe_material_list, 
#             mock_all_modified_crafting_mats)
        
#         expected_quantities = [1, 2, 3, 4]

#         self.assertEqual(expected_quantities, actual_quantities)

#     def test__create_modified_crafting_material_info(self):
#         expected_modified_crafting_quantities_csv = dedent(
#         """
#         ID,SpellID,Slot,ModifiedCraftingReagentSlotID,Field_9_0_1_35679_003,ReagentCount,ReagentReCraftCount
#         19,309181,0,77,45,1,0
#         19,309181,1,73,45,1,0
#         30,309180,0,46,45,1,0
#         """
#         ).strip()
#         csv_data = mock_open(read_data=expected_modified_crafting_quantities_csv)
#         with patch('builtins.open', csv_data):
#             actual_quantities = self.insert_test._create_modified_crafting_material_info()
 
#         expected_quantities = {
#             309181: {
#                 77:{
#                     "display_order" : 0,
#                     "quantity" : 1,
#                     "recraft_quantity" : 0
#                 },
#                 73:{
#                     "display_order" : 1,
#                     "quantity" : 1,
#                     "recraft_quantity" : 0
#                 }
#             },
#             309180: {46:{
#                 "display_order" : 0,
#                 "quantity" : 1,
#                 "recraft_quantity" : 0
#             }}
#         }
#         self.assertEqual(expected_quantities, actual_quantities)

#     def test_get_product_quantity(self):
#         # EffectBasePointsF is the product quantity index 11
#         expected_spell_effect_csv = dedent(
#         """
#         ID, EffectAura, DifficultyID, EffectIndex
#         272,0,0,0,56,0,0,0,0,1.0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,417,0,0,0,0,0,0,0,32,0,365731
#         """
#         ).strip()
#         csv_data = mock_open(read_data=expected_spell_effect_csv)
#         with patch('builtins.open', csv_data):
#             acutal_records = self.insert_test.get_product_quantity()

#         expected_records = {
#             365731: 1
#         }
#         self.assertEqual(expected_records, acutal_records)

#     async def test_get_recipe_spell_id_by_recipe_id(self):
#         expected_skill_line_ability_csv = dedent(
#         """
#         RaceMask,AbilityVerb_lang,AbilityAllVerb_lang,ID,SkillLine,Spell,MinSkillLineRank,ClassMask,SupercedesSpell,AcquireMethod,TrivialSkillLineRankHigh,TrivialSkillLineRankLow,Flags,NumSkillUps,UniqueBit,TradeSkillCategoryID,SkillupSkillLineID
#         0,,,254,54,198,1,5755,0,2,0,0,0,1,0,0,0
#         """
#         ).strip()
#         mock_recipe_id = 254
#         csv_data = mock_open(read_data=expected_skill_line_ability_csv)
#         with patch('builtins.open', csv_data):
#             actual_spell_id = await self.insert_test.get_recipe_spell_id_by_recipe_id(mock_recipe_id)

#         expected_spell_id = 198
        
#         self.assertEqual(expected_spell_id, actual_spell_id)
 
#     def test__create_modified_crafting_material_record(self):
#         mock_material_name = "Test material name"
#         mock_material_display_order = 0
#         mock_material_quantity = 1
#         mock_recraft_quantity = 0
#         mock_material = {
#             "display_order" : mock_material_display_order,
#             "slot_type":{"name": mock_material_name}
#         }
#         mock_recipe = Recipe()
#         mock_quantities = {mock_material_display_order : mock_material_quantity}
#         mock_slot = OptionalMaterialSlot()

#         actual_record = self.insert_test._create_modified_crafting_material_record(mock_material, mock_recipe, mock_quantities, mock_slot)
#         expected_record = Material(
#             name=mock_material_name,
#             quantity=mock_material_quantity,
#             recraft_quantity=mock_recraft_quantity,
#             optional_material_slot = mock_slot,
#             recipe = mock_recipe,
#             display_order=mock_material_display_order
#             )

#         self.assertEqual(expected_record.name, actual_record.name)
#         self.assertEqual(expected_record.quantity, actual_record.quantity)
#         self.assertEqual(expected_record.recraft_quantity, actual_record.recraft_quantity)
#         self.assertEqual(expected_record.optional_material_slot, actual_record.optional_material_slot)
#         self.assertEqual(expected_record.recipe, actual_record.recipe)
#         self.assertEqual(expected_record.display_order, actual_record.display_order)


#     def test_create_material_record(self):
#         mock_regular_material_param = {
#             "reagent":{
#                 "name": "test regular material",
#                 "id": 1 # item id
#                 },
#             "quantity": 1
#         }
#         mock_profession = ProfessionIndex.objects.create(id=1, name="test profession")
#         mock_profession_category = RecipeCategory.objects.create(name="test category", profession=mock_profession)
#         mock_recipe_param = Recipe.objects.create(
#             id=1, name="test recipe", 
#             recipe_category=mock_profession_category,
#             )

#         actual_response = self.insert_test._create_material_record(mock_regular_material_param, mock_recipe_param)
#         expected_name ="test regular material"
#         expected_quanaity=1
#         expected_recraft_quantity=None
#         expected_display_order=None
#         expected_optional_material_slot=None
#         expected_recipe=mock_recipe_param

#         self.assertEqual(expected_name, actual_response.name)
#         self.assertEqual(expected_quanaity, actual_response.quantity)
#         self.assertEqual(expected_recraft_quantity, actual_response.recraft_quantity)
#         self.assertEqual(expected_display_order, actual_response.display_order)
#         self.assertEqual(expected_optional_material_slot, actual_response.optional_material_slot)
#         self.assertEqual(expected_recipe, actual_response.recipe)


# class TestDumps(IsolatedAsyncioTestCase):
#     test_directory_path = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\tests\unit_tests\test_directory"

#     async def asyncSetUp(self) -> None:
#         WowApi._get_access_token = AsyncMock(return_value='DummyAccessToken')
#         self.insert_test = await Insert.create('testregion')
#         os.mkdir(self.test_directory_path)

#     def tearDown(self) -> None:
#         for file in os.listdir(self.test_directory_path):
#             file_path = os.path.join(self.test_directory_path, file)
#             os.remove(file_path)
#         os.rmdir(self.test_directory_path)

#     async def test__if_json_file_doesnt_exist_create_one_when_path_exists(self):
#         mock_callback_func = AsyncMock(return_value={"dummy":"json"})
#         self.insert_test._write_json_to_file = AsyncMock()
#         mock_path = os.path.join(self.test_directory_path, "mock_connected_realms_index.json")
#         with open(mock_path, "w") as file:
#             pass

#         await self.insert_test._if_json_file_doesnt_exist_create_one(mock_path, mock_callback_func)

#         mock_callback_func.assert_not_awaited()
#         self.insert_test._write_json_to_file.assert_not_awaited()

#     async def test__if_json_file_doesnt_exist_create_one_when_path_does_not_exists(self):
#         mock_callback_func = AsyncMock(return_value={"dummy":"json"})
#         self.insert_test._write_json_to_file = AsyncMock()
#         mock_path = os.path.join(self.test_directory_path, "mock_connected_realms_index.json")

#         await self.insert_test._if_json_file_doesnt_exist_create_one(mock_path, mock_callback_func)

#         mock_callback_func.assert_awaited_once()
#         self.insert_test._write_json_to_file.assert_awaited()

#     async def test__write_json_to_file(self):
#         test_json = {
#                 "dummy json" : 1,
#                 "more dummy" : ":)"
#         }
#         mock_file_name = "test_file"
#         mock_json_path = os.path.join(self.test_directory_path, mock_file_name)
#         await self.insert_test._write_json_to_file(mock_json_path, test_json)

#         expected_json = {
#             "dummy json" : 1,
#             "more dummy" : ":)"
#         }

#         with open(mock_json_path, "r") as dummy_data:
#             actual_json = json.load(dummy_data)

#         self.assertEqual(expected_json, actual_json)

#     async def test_insert_connected_realms_index(self):
#         self.insert_test.wowapi.get_connected_realm_index = AsyncMock()
#         self.insert_test._if_json_file_doesnt_exist_create_one = AsyncMock()
#         self.insert_test._insert_connected_realms_index = MagicMock()
#         os.remove = MagicMock()

#         await self.insert_test.insert_connected_realms_index()

#         self.insert_test._if_json_file_doesnt_exist_create_one.assert_awaited()
#         self.insert_test._insert_connected_realms_index.assert_called_once()
#         os.remove.assert_called_once()

#     async def test_insert_all_realms(self):
#         self.insert_test.wowapi.get_all_realms = AsyncMock()
#         self.insert_test._if_json_file_doesnt_exist_create_one = AsyncMock()
#         self.insert_test._insert_all_realms = MagicMock()
#         os.remove = MagicMock()

#         await self.insert_test.insert_all_realms()

#         self.insert_test.wowapi.get_all_realms.assert_awaited()
#         self.insert_test._if_json_file_doesnt_exist_create_one.assert_awaited()
#         self.insert_test._insert_all_realms.assert_called_once()
#         os.remove.assert_called_once()

#     async def test_insert_all_dragonflight_items(self):
#         self.insert_test.wowapi.get_items_by_expansion = AsyncMock()
#         self.insert_test._if_json_file_doesnt_exist_create_one = AsyncMock()
#         self.insert_test._insert_all_dragonflight_items = MagicMock()
#         os.remove = MagicMock()

#         await self.insert_test.insert_all_dragonflight_items()

#         self.insert_test.wowapi.get_items_by_expansion.assert_awaited()
#         self.insert_test._if_json_file_doesnt_exist_create_one.assert_awaited()
#         self.insert_test._insert_all_dragonflight_items.assert_called_once()
#         os.remove.assert_called_once()        

#     async def test_insert_dragonflight_profession_tree(self):
#         self.insert_test.wowapi.get_professions_tree_by_expansion = AsyncMock()
#         self.insert_test._if_json_file_doesnt_exist_create_one = AsyncMock()
#         self.insert_test._insert_dragonflight_profession_tree = AsyncMock()
#         os.remove = MagicMock()

#         await self.insert_test.insert_dragonflight_profession_tree()

#         self.insert_test._if_json_file_doesnt_exist_create_one.assert_awaited()
#         self.insert_test._insert_dragonflight_profession_tree.assert_awaited()
#         os.remove.assert_called_once()

#     async def test__get_product_item_id_by_spell_id(self):
#         self.insert_test.get_all_crafting_data_ids_by_spell_id = MagicMock()
#         self.insert_test.get_all_product_ids_by_crafting_data_id = MagicMock()
#         self.insert_test._if_json_file_doesnt_exist_create_one = AsyncMock()

#         mock_spell_id = 1

#         self.insert_test.find_value_in_json_file = MagicMock(side_effect=(
#             2,
#             3
#         ))

#         actual_product_id = await self.insert_test._get_product_item_id_by_spell_id(mock_spell_id)
#         expected_product_id = 3

#         self.assertEqual(expected_product_id, actual_product_id)
#         self.insert_test._if_json_file_doesnt_exist_create_one.assert_awaited()
#         self.insert_test.find_value_in_json_file.assert_called()

#     def test_find_value_in_json_file(self):
#         mock_json_file_path = "path"
#         mock_key = "a"
#         mock_file_at_mock_path = dedent(
#             """{"a": 1}"""
#         ).strip()
#         json_data = mock_open(read_data=mock_file_at_mock_path)

#         with patch('builtins.open', json_data):
#             actual_value = self.insert_test.find_value_in_json_file(mock_json_file_path, mock_key)
        
#         expected_value = 1

#         self.assertEqual(expected_value, actual_value)

#     async def test_get_all_crafting_data_ids_by_spell_id(self):
#         expected_spell_effect_csv = dedent(
#         """
#         ID,EffectAura,DifficultyID,EffectIndex,Effect,EffectAmplitude,EffectAttributes,EffectAuraPeriod,EffectBonusCoefficient,EffectChainAmplitude,EffectChainTargets,EffectItemType,EffectMechanic,EffectPointsPerResource,EffectPos_facing,EffectRealPointsPerLevel,EffectTriggerSpell,BonusCoefficientFromAP,PvpMultiplier,Coefficient,Variance,ResourceCoefficient,GroupSizeBasePointsCoefficient,EffectBasePointsF,ScalingClass,EffectMiscValue_0,EffectMiscValue_1,EffectRadiusIndex_0,EffectRadiusIndex_1,EffectSpellClassMask_0,EffectSpellClassMask_1,EffectSpellClassMask_2,EffectSpellClassMask_3,ImplicitTarget_0,ImplicitTarget_1,SpellID
#         357181,0,0,2,28,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,118955,719,13,0,0,0,0,0,142,0,236265
#         """
#         ).strip()
#         csv_data = mock_open(read_data=expected_spell_effect_csv)
#         with patch('builtins.open', csv_data):
#             acutal_record = await self.insert_test.get_all_crafting_data_ids_by_spell_id()
        
#         expected_record = {
#             236265 : 118955
#         }
#         self.assertEqual(expected_record, acutal_record)

#     async def test_get_all_product_ids_by_crafting_data_id(self):
#         expected_crafting_data_csv = dedent(
#         """
#         ID,ItemID,CraftingDataID
#         1,190645,1
#         1,111,1
#         1,222,2
#         """
#         ).strip()
#         csv_data = mock_open(read_data=expected_crafting_data_csv)
#         with patch('builtins.open', csv_data):
#             acutal_record = await self.insert_test.get_all_product_ids_by_crafting_data_id()
        
#         expected_record = {
#             1 : [190645, 111],
#             2 : [222]
#         }
#         self.assertEqual(expected_record, acutal_record)