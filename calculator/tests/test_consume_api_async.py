import datetime
from unittest.mock import MagicMock, AsyncMock

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase, TransactionTestCase
from getwowdataasync import urls, convert_to_datetime, WowApi
from calculator.models import *
from calculator.consume_api_async import Insert
from aioresponses import aioresponses

class Test(TestCase):
    mock_region = "us"
    mock_recipe_id = 1
    mock_connected_realm_id = 1
    mock_profession_id = 1
    mock_skill_tier_id = 1
    mock_item_id = 1
    current_date = datetime.datetime.now()
    with aioresponses() as mocked:
        mocked.post(
            urls["access_token"].format(region=mock_region),
            payload={"access_token": "0000000000000000000000000000000000"},
        )
        test_api = async_to_sync(Insert.create)("us")

    @classmethod
    def setUpTestData(cls):
    
        region = Region.objects.create(region="North America")
        connected_realm = ConnectedRealmsIndex.objects.create(connected_realm_id=1)
        realm = Realm.objects.create(connected_realm=connected_realm, population="Low", realm_id=1, name="Test realm", region=region, timezone='est', play_style='RP')
        ItemBonus.objects.create(id=1)
        item = Item.objects.create(id=1, vendor_buy_price=100, vendor_sell_price=100, vendor_buy_quantity=100, quality='test_quality', name="item_test", binding='boe')
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
        self.test_api.connected_realm_search = AsyncMock(
            return_value={
                "results": [
                    {
                        "data": {
                            "id": 2,
                            "population": {"type": "FULL"},
                        }
                    }
                ]
            }
        )
        self.test_api.insert_connected_realms_index()
        expected_record = {'connected_realm_id':2}
        actual_record = ConnectedRealmsIndex.objects.filter(connected_realm_id=2).values()
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
                                    "region": {"name": {"en_US": "North America"}},
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
            'region_id': "North America",
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


