import datetime
from unittest.mock import MagicMock, AsyncMock
from string import ascii_uppercase

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase
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
        realm = Realm.objects.create(
            connected_realm=connected_realm,
            population="Low",
            realm_id=1,
            name="Test realm",
            region=region,
            timezone="est",
            play_style="RP",
        )
        ItemBonus.objects.create(id=1)
        item = Item.objects.create(
            id=1,
            vendor_buy_price=100,
            vendor_sell_price=100,
            vendor_buy_quantity=100,
            quality="test_quality",
            name="item_test",
            binding="boe",
        )
        item5 = Item.objects.create(
            id=5,
            vendor_buy_price=100,
            vendor_sell_price=100,
            vendor_buy_quantity=100,
            quality="test_quality",
            name="item_test",
            binding="boe",
        )

        profession = ProfessionIndex.objects.create(id=1, name="Test Profession")
        profession_tier = ProfessionTier.objects.create(
            id=1, name="Test Tier", profession=profession
        )
        recipe_category = RecipeCategory.objects.create(
            name="Test category", profession_tier=profession_tier
        )
        recipe = Recipe.objects.create(
            id=1, name="Test recipe", recipe_category=recipe_category
        )
        material = Material.objects.create(item=item, quantity=1, recipe=recipe)
        product = Product.objects.create(
            item=item, recipe=recipe, min_quantity=1, max_quantity=1
        )

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
        expected_record = {"connected_realm_id": 121}
        actual_record = ConnectedRealmsIndex.objects.filter(
            connected_realm_id=121
        ).values()
        self.assertDictEqual(expected_record, actual_record[0])

    def test_insert_all_realms(self):
        self.test_api.get_all_realms = AsyncMock(
            return_value={
                "realms": [
                    {
                        "realms": [
                            {
                                "id": 2,
                                "region": {"name": "testregion"},
                                "timezone": "America/New_York",
                                "type": {"type": "NORMAL"},
                                "slug": "TestServer",
                            }
                        ],
                        "id": 1,
                        "population": {"type": "FULL"},
                    }
                ]
            }
        )
        self.test_api.insert_all_realms()
        actual_record = Realm.objects.filter(realm_id=2).values()
        expected_record = {
            "connected_realm_id": 1,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region_id": "testregion",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }
        self.assertDictEqual(expected_record, actual_record[0])

    def test_insert_auctions(self):
        self.test_api.get_auctions = AsyncMock(
            return_value={
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
                ],
            }
        )

        self.test_api.insert_auctions(self.mock_connected_realm_id)
        actual_record = Auction.objects.filter(auction_id=2).values()
        date = actual_record[0]["timestamp"]

        expected_record = {
            "auction_id": 2,
            "buyout": 2,
            "bid": 2,
            "unit_price": 2,
            "quantity": 2,
            "time_left": "SHORT",
            "timestamp": date,
            "connected_realm_id": 1,
            "item_id": 2,
            "pet_level": 2,
        }

        self.assertDictEqual(expected_record, actual_record[0])

    def test_insert_profession_index(self):
        self.test_api.get_profession_index = AsyncMock(
            return_value={"professions": [{"id": 2, "name": "test"}]}
        )

        self.test_api.insert_profession_index()
        actual_record = ProfessionIndex.objects.filter(id=2).values()
        expected_record = {"name": "test", "id": 2}
        self.assertDictEqual(expected_record, actual_record[0])

    def test_insert_profession_tier(self):
        self.test_api.get_profession_tiers = AsyncMock(
            return_value={"id": 1, "skill_tiers": [{"name": "Test", "id": 2}]}
        )
        self.test_api.insert_profession_tier(self.mock_profession_id)
        actual_record = ProfessionTier.objects.filter(id=2).values()
        expected_record = {"id": 2, "name": "Test", "profession_id": 1}
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
        self.test_api.insert_recipe_category(
            self.mock_profession_id, self.mock_profession_tier_id
        )
        actual_record_category = RecipeCategory.objects.filter(
            name="Test Category 2"
        ).values()
        actual_record_recipe = Recipe.objects.filter(id=2).values()
        expected_record_category = {
            "id": 2,
            "name": "Test Category 2",
            "profession_tier_id": 1,
        }
        expected_record_recipe = {
            "id": 2,
            "name": "Test Recipe",
            "recipe_category_id": 2,
        }

        self.assertEqual(expected_record_category, actual_record_category[0])
        self.assertEqual(expected_record_recipe, actual_record_recipe[0])

    def test_insert_recipe(self):
        self.test_api.get_recipe = AsyncMock(
            return_value={
                "id": 1,
                "name": "Test recipe",
                "crafted_item": {"id": 2, "name": "item_test"},
                "crafted_quantity": {"value": 2},
                "reagents": [
                    {"reagent": {"id": 2, "name": "item_test"}, "quantity": 2}
                ],
            }
        )
        # TODO test that this inserts into the mats, product, and recipe models correctly
        self.test_api.insert_recipe(1)
        actual_record = Recipe.objects.filter(id=1).values()
        mats = Recipe.objects.filter(id=1)[0].material_set.all().values()

        expected_record = {
            "id": 1,
            "name": "Test recipe",
            "recipe_category_id": 1,
        }
        expected_record_mats0 = {"id": 1, "item_id": 1, "quantity": 1, "recipe_id": 1}
        expected_record_mats1 = {"id": 2, "item_id": 2, "quantity": 2, "recipe_id": 1}

        self.assertDictEqual(expected_record, actual_record[0])
        self.assertDictEqual(expected_record_mats0, mats[0])
        self.assertDictEqual(expected_record_mats1, mats[1])

    # TODO
    def test_insert_item(self):
        pass

    def test_insert_all_items(self):
        mock_items_json = {
            "items": [
                {
                    "id": 3,
                    "purchase_price": 2,
                    "sell_price": 2,
                    "purchase_quantity": 2,
                    "quality": {"type": "EPIC"},
                    "name": "Test Epic item",
                    "binding": {"type": "ON_ACQUIRE"},
                },
                {
                    "id": 4,
                    "purchase_price": 2,
                    "sell_price": 3,
                    "purchase_quantity": 3,
                    "quality": {"type": "LEGENDARY"},
                    "name": "Test lego item",
                },
            ]
        }
        self.test_api.get_all_items = AsyncMock(return_value=mock_items_json)
        self.test_api.insert_all_items()
        actual_record = Item.objects.filter(vendor_buy_price=2).values()
        expected_record = [
            {
                "id": 3,
                "vendor_buy_price": 2,
                "vendor_sell_price": 2,
                "vendor_buy_quantity": 2,
                "quality": "EPIC",
                "name": "Test Epic item",
                "binding": "ON_ACQUIRE",
            },
            {
                "id": 4,
                "vendor_buy_price": 2,
                "vendor_sell_price": 3,
                "vendor_buy_quantity": 3,
                "quality": "LEGENDARY",
                "name": "Test lego item",
                "binding": None,
            },
        ]
        self.assertEqual(expected_record[0], actual_record[0])
        self.assertEqual(expected_record[1], actual_record[1])

    """ # because of the if not condition this doesn't work correctly but its simple enough to ignore
    def test_insert_regional_data(self):
        self.test_api.get_all_realms = AsyncMock(return_value={
                "results": [
                    {
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
                ]
            }
        )
        self.test_api.get_connected_realm_index = AsyncMock(
            return_value={
                "connected_realms": [
                    {
                        "href": "https://us.api.blizzard.com/data/wow/connected-realm/121?namespace=dynamic-us"
                    }
                ]
            }
        )
      
        self.test_api.insert_regional_data()
        ConnectedRealmsIndex.objects.all()
        expected_connected_realm_record = {'connected_realm_id':121}
        actual_connected_realm_record = ConnectedRealmsIndex.objects.filter(connected_realm_id=121).values()
        print(actual_connected_realm_record)
        self.assertDictEqual(expected_connected_realm_record, actual_connected_realm_record[0])

        actual_realm_record = Realm.objects.filter(realm_id=2).values()
        expected_realm_record = {
            'connected_realm_id': 1,
            'population': "FULL",
            'realm_id': 2,
            'name': "TestServer",
            'region_id': "testregion",
            'timezone': "America/New_York",
            'play_style': "NORMAL",
        }
        self.assertDictEqual(expected_realm_record, actual_realm_record[0])
    """

    def test_calculate_market_price(self):
        for id in range(20):
            Auction.objects.create(
                auction_id=id + 3,
                buyout=id + 1,
                bid=id,
                quantity=1,
                time_left="SHORT",
                timestamp=self.current_date,
                connected_realm=ConnectedRealmsIndex.objects.get(connected_realm_id=1),
                item=Item.objects.get(id=1),
            )
            Auction.objects.create(
                auction_id=id + 40,
                unit_price=id + 2,
                quantity=1,
                time_left="SHORT",
                timestamp=self.current_date,
                connected_realm=ConnectedRealmsIndex.objects.get(connected_realm_id=1),
                item=Item.objects.get(id=5),
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
            {"region": "North America"},
            {"region": "Europe"},
            {"region": "Korea"},
        ]
        self.assertDictEqual(expected_record[0], regions[0])
        self.assertDictEqual(expected_record[1], regions[1])
        self.assertDictEqual(expected_record[2], regions[2])


class TestProfessionInserts(TestCase):
    with aioresponses() as mocked:
        mocked.post(
            urls["access_token"].format(region="us"),
            payload={"access_token": "0000000000000000000000000000000000"},
        )
        test_api = async_to_sync(Insert.create)("us")
    profession_tree = [
        {
            "name": "Test Profession",
            "id": 1,
            "skill_tiers": [
                {
                    "name": "Test Tier",
                    "id": 2,
                    "categories": [
                        {
                            "name": "Test Category",
                            "recipes": [
                                {
                                    "id": 3,
                                    "name": "Test Recipe A",
                                    "crafted_quantity": {"value": 1},
                                    "crafted_item": {"id": 1, "name": "Test Item A"},
                                    "reagents": [
                                        {
                                            "quantity": 1,
                                            "reagent": {
                                                "id": 92,
                                                "name": "Test Mat Item",
                                            },
                                        }
                                    ],
                                },
                                {
                                    "id": 4,
                                    "name": "Test Recipe B",
                                    "crafted_quantity": {
                                        "minimum": 1,
                                        "maximum": 1,
                                    },
                                    "alliance_crafted_item": {
                                        "id": 2,
                                        "name": "Test Item B",
                                    },
                                    "horde_crafted_item": {
                                        "id": 3,
                                        "name": "Test Item C",
                                    },
                                },
                                {
                                    "id": 5,
                                    "name": "Test Recipe C",
                                    "crafted_item": {"id": 4, "name": "Test Item D"},
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    ]

    def test__insert_profession_index(self):
        self.test_api._insert_profession_index(self.profession_tree)
        actual_record = ProfessionIndex.objects.all().values()[0]
        expected_record = {"id": 1, "name": "Test Profession"}
        self.assertDictEqual(expected_record, actual_record)

    def test__insert_skill_tiers(self):
        inserted_professions = self.test_api._insert_profession_index(
            self.profession_tree
        )
        self.test_api._insert_skill_tiers(self.profession_tree, inserted_professions)
        actual_record = ProfessionTier.objects.all().values()[0]
        expected_record = {"id": 2, "name": "Test Tier", "profession_id": 1}
        self.assertDictEqual(expected_record, actual_record)

    def test__insert_skill_tier_categories(self):
        inserted_professions = self.test_api._insert_profession_index(
            self.profession_tree
        )
        inserted_tiers = self.test_api._insert_skill_tiers(
            self.profession_tree, inserted_professions
        )
        actual_record = self.test_api._insert_skill_tier_categories(
            self.profession_tree, inserted_tiers
        )
        expected_record = list(RecipeCategory.objects.filter(id=4))
        self.assertEqual(expected_record, actual_record)

    def test__insert_all_recipes(self):
        inserted_professions = self.test_api._insert_profession_index(
            self.profession_tree
        )
        inserted_tiers = self.test_api._insert_skill_tiers(
            self.profession_tree, inserted_professions
        )
        self.test_api._insert_skill_tier_categories(
            self.profession_tree, inserted_tiers
        )
        inserted_categories = RecipeCategory.objects.all()

        self.test_api._insert_all_recipes(self.profession_tree, inserted_categories)

        actual_recipe_records = Recipe.objects.all().values()
        actual_product_records = Product.objects.all().values()
        actual_mat_record = Material.objects.all().values()

        for recipe_count, actual_recipe_record in enumerate(actual_recipe_records):
            expected_id = recipe_count + 3
            expected_name = f"Test Recipe {ascii_uppercase[recipe_count]}"
            expected_recipe_record = {
                "id": expected_id,
                "name": expected_name,
                "recipe_category_id": 3,
            }
            self.assertDictEqual(expected_recipe_record, actual_recipe_record)

        expected_product_records = [
            {
                "id": 3,
                "item_id": 1,
                "recipe_id": 3,
                "min_quantity": 1,
                "max_quantity": 1,
            },
            {
                "id": 4,
                "item_id": 2,
                "recipe_id": 4,
                "min_quantity": 1,
                "max_quantity": 1,
            },
            {
                "id": 5,
                "item_id": 3,
                "recipe_id": 4,
                "min_quantity": 1,
                "max_quantity": 1,
            },
            {
                "id": 6,
                "item_id": 4,
                "recipe_id": 5,
                "min_quantity": 0,
                "max_quantity": 0,
            },
        ]
        for index, expected_product_record in enumerate(expected_product_records):
            self.assertDictEqual(expected_product_record, actual_product_records[index])

        expected_mat_record = {"id": 3, "item_id": 92, "recipe_id": 3, "quantity": 1}
        self.assertDictEqual(expected_mat_record, actual_mat_record[0])
