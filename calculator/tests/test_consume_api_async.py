import datetime
from unittest.mock import MagicMock, AsyncMock

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase, TransactionTestCase
from django.db.models import Avg, Sum
from getwowdataasync import urls, convert_to_datetime, WowApi
from calculator.models import *
from calculator.consume_api_async import Insert
from aioresponses import aioresponses

class Test(TestCase):
    mock_region = "testregion"
    mock_recipe_id = 1
    mock_connected_realm_id = 1
    mock_profession_id = 1
    mock_profession_tier_id = 1
    mock_item_id = 1
    current_date = datetime.datetime.now()
    with aioresponses() as mocked:
        mocked.post(
            urls["access_token"].format(region=mock_region),
            payload={"access_token": "0000000000000000000000000000000000"},
        )
        test_api = async_to_sync(Insert.create)("testregion")

    @classmethod
    def setUpTestData(cls):
    
        region = Region.objects.create(region="testregion")
        connected_realm = ConnectedRealmsIndex.objects.create(connected_realm_id=1)
        realm = Realm.objects.create(connected_realm=connected_realm, population="Low", realm_id=1, name="Test realm", region=region, timezone='est', play_style='RP')
        ItemBonus.objects.create(id=1)
        item = Item.objects.create(id=1, vendor_buy_price=100, vendor_sell_price=100, vendor_buy_quantity=100, quality='test_quality', name="item_test", binding='boe')
        item5 = Item.objects.create(id=5, vendor_buy_price=100, vendor_sell_price=100, vendor_buy_quantity=100, quality='test_quality', name="item_test", binding='boe')

        profession = ProfessionIndex.objects.create(id=1, name="Test Profession")
        profession_tier = ProfessionTier.objects.create(
            id=1, name="Test Tier", profession=profession
        )
        recipe_category = RecipeCategory.objects.create(
            name="Test category", profession_tier=profession_tier
        )
        material = Material.objects.create(item=item, quantity=1)
        recipe = Recipe.objects.create(
            id=1, name="Test recipe", recipe_category=recipe_category
        )
        recipe.mats.add(material)
        product = Product.objects.create(item=item, recipe=recipe, min_quantity=1, max_quantity=1)


    def test_insert_connected_realms_index(self):
        self.test_api.get_connected_realm_index = AsyncMock(
            return_value={
                "connected_realms": [
                    {
                        "href": "https://us.api.blizzard.com/data/wow/connected-realm/121?namespace=dynamic-us"
                    }
                ]
            }
        )
        self.test_api.insert_connected_realms_index()
        expected_record = {'connected_realm_id':121}
        actual_record = ConnectedRealmsIndex.objects.filter(connected_realm_id=121).values()
        self.assertDictEqual(expected_record, actual_record[0])

    def test_insert_all_realms(self):
        self.test_api.connected_realm_search = AsyncMock(return_value={
                "results": [
                    {
                        "data": {
                            "realms": [
                                {
                                    "id": 2,
                                    "name": {"en_US": "TestServer"},
                                    "region": {"name": {"en_US": "testregion"}},
                                    "timezone": "America/New_York",
                                    "type": {"type": "NORMAL"},
                                }
                            ],
                            "id": 1,
                            "population": {"type": "FULL"},
                        }
                    }
                ]
            }
        )
        self.test_api.insert_all_realms()
        actual_record = Realm.objects.filter(realm_id=2).values()
        expected_record = {
            'connected_realm_id': 1,
            'population': "FULL",
            'realm_id': 2,
            'name': "TestServer",
            'region_id': "testregion",
            'timezone': "America/New_York",
            'play_style': "NORMAL",
        }
        self.assertDictEqual(expected_record, actual_record[0])


    def test_insert_auctions(self):
        self.test_api.get_auctions = AsyncMock(return_value=
        {
            "Date": "Tue, 12 Jul 2022 15:03:30 GMT",
            "auctions": [
                {
                    "id": 2,
                    "buyout": 2,
                    "bid": 2,
                    "unit_price": 2,
                    "quantity": 2,
                    "time_left": "SHORT",
                    "item": {
                        "id": 2,
                        "pet_level": 2,
                        "bonus_lists": [1, 2],
                    },
                }
            ]
        })

        self.test_api.insert_auctions(self.mock_connected_realm_id)
        actual_record = Auction.objects.filter(auction_id=2).values()
        date = actual_record[0]['timestamp']

        expected_record = {
            'auction_id' : 2,
            'buyout':2,
            'bid':2,
            'unit_price':2,
            'quantity':2,
            'time_left':"SHORT",
            'timestamp':date,
            'connected_realm_id': 1,
            'item_id': 2,
            'pet_level':2
        }

        self.assertDictEqual(
            expected_record, actual_record[0]
        )

    def test_insert_profession_index(self):
        self.test_api.get_profession_index = AsyncMock(
            return_value={"professions": [{"id": 2, "name": "test"}]}
        )

        self.test_api.insert_profession_index()
        actual_record = ProfessionIndex.objects.filter(id=2).values()
        expected_record = {'name':"test", 'id':2}
        self.assertDictEqual(expected_record, actual_record[0])


    def test_insert_profession_tier(self):
        self.test_api.get_profession_tiers = AsyncMock(
            return_value={"id": 1, "skill_tiers": [{"name": "Test", "id": 2}]}
        )
        self.test_api.insert_profession_tier(self.mock_profession_id)
        actual_record = ProfessionTier.objects.filter(id=2).values()
        expected_record = {'id':2, 'name':"Test", 'profession_id':1}
        self.assertEqual(expected_record, actual_record[0])

    def test_insert_recipe_category(self):
        self.test_api.get_profession_tier_categories = AsyncMock(
            return_value={
                "categories": [
                    {
                        "name": "Test Category 2",
                        "recipes": [{"name": "Test Recipe", "id": 2}],
                    }
                ]
            }
        )
        self.test_api.insert_recipe_category(self.mock_profession_id, self.mock_profession_tier_id)
        actual_record_category = RecipeCategory.objects.filter(name="Test Category 2").values()
        actual_record_recipe = Recipe.objects.filter(id=2).values()
        expected_record_category = {
            'id':2,
            'name':'Test Category 2',
            'profession_tier_id': 1,
        }
        expected_record_recipe = {
            'id':2,
            'name':'Test Recipe',
            'recipe_category_id': 2,
        }

        self.assertEqual(expected_record_category, actual_record_category[0])
        self.assertEqual(expected_record_recipe, actual_record_recipe[0])


    def test_insert_recipe(self):
        self.test_api.get_recipe = AsyncMock(return_value = {
            'id':1,
            'name':'Test recipe',
            'crafted_item': {'id':2, 'name':'item_test'},
            'crafted_quantity': {'value':2},
            'reagents': [{'reagent': {'id':2, 'name':'item_test'}, 'quantity':2}]
        })
        #TODO test that this inserts into the mats, product, and recipe models correctly
        self.test_api.insert_recipe(self.mock_recipe_id)
        actual_record = Recipe.objects.filter(id=1).values()
        mats = Recipe.objects.filter(id=1)[0].mats.all().values()

        expected_record = {
            'id':1,
            'name':'Test recipe',
            'recipe_category_id':1,
        }
        expected_record_mats0 = {
            'id':1,
            'item_id':1,
            'quantity':1
        }
        expected_record_mats1 = {
            'id':2,
            'item_id':2,
            'quantity':2
        }

        self.assertDictEqual(expected_record, actual_record[0])
        self.assertDictEqual(expected_record_mats0, mats[0])
        self.assertDictEqual(expected_record_mats1, mats[1])

    #TODO
    def test_insert_item(self):
        pass

    def test_insert_all_item(self):
        mock_items_json = {
            'items':[
                {
                    'id':3,
                    'purchase_price':2,
                    'sell_price':2,
                    'purchase_quantity':2,
                    'quality': {'type':'EPIC'},
                    'name': 'Test Epic item',
                    'binding': {'type':'ON_ACQUIRE'}
                },
                {
                    'id':4,
                    'purchase_price':2,
                    'sell_price':3,
                    'purchase_quantity':3,
                    'quality': {'type':'LEGENDARY'},
                    'name': 'Test lego item',
                },
            ]
        }
        self.test_api.item_search = AsyncMock(return_value = mock_items_json)
        self.test_api.insert_all_item()
        actual_record = Item.objects.filter(vendor_buy_price=2).values()
        expected_record = [
            {'id': 3, 'vendor_buy_price': 2, 'vendor_sell_price': 2, 'vendor_buy_quantity': 2, 'quality': 'EPIC', 'name': 'Test Epic item', 'binding': 'ON_ACQUIRE'},
            {'id': 4, 'vendor_buy_price': 2, 'vendor_sell_price': 3, 'vendor_buy_quantity': 3, 'quality': 'LEGENDARY', 'name': 'Test lego item', 'binding': None}
        ]
        self.assertEqual(expected_record[0], actual_record[0])
        self.assertEqual(expected_record[1], actual_record[1])

    """
    def test_insert_all_data(self):
        self.test_api.connected_realm_search = AsyncMock(return_value={
                "results": [
                    {
                        "data": {
                            "realms": [
                                {
                                    "id": 2,
                                    "name": {"en_US": "TestServer"},
                                    "region": {"name": {"en_US": "testregion"}},
                                    "timezone": "America/New_York",
                                    "type": {"type": "NORMAL"},
                                }
                            ],
                            "id": 1,
                            "population": {"type": "FULL"},
                        }
                    }
                ]
            }
        )
        self.test_api.insert_all_data()
        actual_record = Item.objects.filter(vendor_buy_price=2).values()
        expected_record = [
            {'id': 3, 'vendor_buy_price': 2, 'vendor_sell_price': 2, 'vendor_buy_quantity': 2, 'quality': 'EPIC', 'name': 'Test Epic item', 'binding': 'ON_ACQUIRE'},
            {'id': 4, 'vendor_buy_price': 2, 'vendor_sell_price': 3, 'vendor_buy_quantity': 3, 'quality': 'LEGENDARY', 'name': 'Test lego item', 'binding': None}
        ]
        self.assertEqual(expected_record[0], actual_record[0])
        self.assertEqual(expected_record[1], actual_record[1])
    """

    def test_calculate_market_price(self):
        for id in range(20):
            Auction.objects.create(
                auction_id=id+3,
                buyout=id+1,
                bid=id,
                quantity=1,
                time_left='SHORT',
                timestamp = self.current_date,
                connected_realm = ConnectedRealmsIndex.objects.get(connected_realm_id=1),
                item = Item.objects.get(id=1)
            )
            Auction.objects.create(
                auction_id=id+40,
                unit_price=id+2,
                quantity=1,
                time_left='SHORT',
                timestamp = self.current_date,
                connected_realm = ConnectedRealmsIndex.objects.get(connected_realm_id=1),
                item = Item.objects.get(id=5)
            )


    def test_insert_region_price_data(self):
        pass

    def test_insert_recipe_profit(self):
        pass

class TestWithEmptyDB(TestCase):
    mock_region = "us"
    mock_recipe_id = 1
    mock_connected_realm_id = 1
    mock_profession_id = 1
    mock_profession_tier_id = 1
    mock_item_id = 1
    current_date = datetime.datetime.now()
    with aioresponses() as mocked:
        mocked.post(
            urls["access_token"].format(region=mock_region),
            payload={"access_token": "0000000000000000000000000000000000"},
        )
        test_api = async_to_sync(Insert.create)("us")

    def test_insert_regions(self):
        self.test_api.insert_regions()
        regions = Region.objects.all().values()
        expected_record = [
            {'region':'North America'}, {'region':'Europe'}, {'region':'Korea'}
        ]
        self.assertDictEqual(expected_record[0], regions[0])
        self.assertDictEqual(expected_record[1], regions[1])
        self.assertDictEqual(expected_record[2], regions[2])

    def test_insert_all_data(self):
        pass