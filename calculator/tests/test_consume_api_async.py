import datetime
from unittest.mock import MagicMock, AsyncMock

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase, TransactionTestCase
from getwowdataasync import urls, convert_to_datetime, WowApi
from calculator.models import *
from calculator.consume_api_async import Insert
from aioresponses import aioresponses

class TestConsumeApiAsync(TestCase):
    @async_to_sync
    async def setUp(self):
        self.mock_region = "us"
        self.mock_recipe_id = 1
        self.mock_connected_realm_id = 1
        self.mock_profession_id = 1
        self.mock_skill_tier_id = 1
        self.current_date = datetime.datetime.now()
        with aioresponses() as mocked:
            mocked.post(
                urls["access_token"].format(region=self.mock_region),
                payload={"access_token": "0000000000000000000000000000000000"},
            )
            self.test_api = await Insert.create("us")

    @classmethod
    def setUpTestData(cls):
        """Inserts testing records into a testing db."""
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

    async def test_insert_all_realms(self):
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
        await self.test_api.insert_all_realms()
        connected_realm_obj = await sync_to_async(ConnectedRealmsIndex.objects.get)(connected_realm_id=1)
        reigon_obj = await sync_to_async(Region.objects.get)(region="North America")
        expected_record = Realm(
            connected_realm= connected_realm_obj,
            population= "FULL",
            realm_id= 2,
            name= "TestServer",
            region= reigon_obj,
            timezone= "America/New_York",
            play_style= "NORMAL",
        )
        actual_record = await sync_to_async(Realm.objects.get)(realm_id=2)
        self.assertEqual(expected_record, actual_record)
