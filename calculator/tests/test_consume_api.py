"""Tests for the consume_api.py module"""
from unittest.mock import MagicMock
import responses
from django.test import TestCase
from getwowdata import urls
from getwowdata import WowApi
from calculator.models import *
from calculator import consume_api


class TestConsumeApi(TestCase):
    ###consume functions
    # Setup responses dummy urls with json data in the blizzard format
    # call consume_api.py func's and assert they return the expected values

    ###insert functions
    # Mock db
    # Mock consume_func that is yielding the inserted data
    # Assert that expected records are being inserted into the table

    region = "us"
    mock_connected_realm_id = 1
    responses.post(
        urls["access_token"].format(region=region),
        json={"access_token": "0000000000000000000000000000000000"},
    )
    us_region_api = WowApi("us", "test_client_id", "test_client_secret")

    @classmethod
    def setUpTestData(cls):
        """Inserts testing records into a testing db."""
        ConnectedRealmsIndex.objects.create(connected_realm_id=1)
        ItemBonus.objects.create(id=1)
        ItemModifier.objects.create(modifier_type=1, value=1)
        Item.objects.create(id = 1, name = 'item_test')

    def test_consume_realm_yield_success(self):
        """Unit test for consume_realm correctly returning values."""

        self.us_region_api.connected_realm_search = MagicMock(
            return_value={
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

        connected_realm_id = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        consume_output = next(consume_api.consume_realm(self.us_region_api))
        expected_yield = {
            "connected_realm_id": connected_realm_id,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region": "North America",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }

        self.assertDictEqual(expected_yield, consume_output[0])

    def test_insert_realm_success(self):
        """Unit test for insert_realm correctly inserting values into db."""
        connected_realm_id = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        consume_realm_results = [{
            "connected_realm_id": connected_realm_id,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region": "North America",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }]

        consume_api.consume_realm = MagicMock(return_value=consume_realm_results)
        consume_api.insert_realm(self.us_region_api)

        record = Realm.objects.get(realm_id=2)

        self.assertEqual(
            consume_realm_results.get("connected_realm_id").connected_realm_id,
            record.connected_realm_id,
        )
        self.assertEqual(consume_realm_results.get("population"), record.population)
        self.assertEqual(consume_realm_results.get("realm_id"), record.realm_id)
        self.assertEqual(consume_realm_results.get("name"), record.name)
        self.assertEqual(consume_realm_results.get("region"), record.region)
        self.assertEqual(consume_realm_results.get("timezone"), record.timezone)
        self.assertEqual(consume_realm_results.get("play_style"), record.play_style)

    def test_consume_connected_realms_index_success(self):
        """Unit test for connected_realm_index returning correct values"""
        self.us_region_api.connected_realm_search = MagicMock(
            return_value={
                "results": [
                    {
                        "data": {
                            "id": 1,
                            "population": {"type": "FULL"},
                        }
                    }
                ]
            }
        )
        consume_index_output = next(
            consume_api.consume_connected_realms_index(self.us_region_api)
        )
        expected_yield = 1
        self.assertEqual(expected_yield, consume_index_output)

    def test_insert_connected_realms_index_success(self):
        """Unit test for insert_connected_realms_index correctly inserting into db."""
        consume_index_results = 1
        consume_api.consume_connected_realms_index = MagicMock(
            return_value=[consume_index_results]
        )
        consume_api.insert_connected_realms_index(self.us_region_api)
        record = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        self.assertEqual(consume_index_results, record.connected_realm_id)

    def test_consume_auctions_success(self):
        """Unit test for consume_auctions yielding correct values."""
        mock_get_auctions_return = {
                "auctions": {
                    "id": 1,
                    "buyout": 1,
                    "bid": 1,
                    "unit_price": 1,
                    "quantity": 1,
                    "time_left": 'SHORT',
                    'item':{'id':1,
                        'pet_level':1,
                        'bonus_lists':[1,2,3],
                        'modifiers': {'type':1, 'value':1}
                    }
                }
            }
        self.us_region_api.get_auctions = MagicMock(
            return_value=mock_get_auctions_return)
        consume_auctions_output = next(consume_api.consume_auctions(self.mock_connected_realm_id))

        item_obj = Item.objects.get(id=1)
        connected_realm_obj = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        item_bonus_list = [ItemBonus.objects.get()]
        item_modifier_list = [ItemModifier.objects.filter(modifier_type=1).filter(value=1)]

        expected_yield = {'auction_id':1,
            'buyout':1,
            'bid':1,
            'unit_price':1,
            'quantity':1,
            'time_left':'SHORT',
            'connected_realm_id':connected_realm_obj,
            'item':item_obj,
            'pet_level':1,
            'item_bonus_list':item_bonus_list,
            'item_modifier_list':item_modifier_list}
        self.assertEqual(consume_auctions_output, expected_yield)

    def test_insert_auctions_success(self):
        """Unit test for correctly inserting auctions into db."""
        item_obj = Item.objects.get(id=1)
        connected_realm_obj = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        
        mock_auction_input = [{'auction_id':1,
            'buyout':1,
            'bid':1,
            'unit_price':1,
            'quantity':1,
            'time_left':'SHORT',
            'connected_realm_id':connected_realm_obj,
            'item':item_obj,
            'pet_level':1,
            'item_bonus_list':[1,2,3],
            'item_modifier_list':{'type':1, 'value':1},}]
        consume_api.consume_auctions = MagicMock(return_value = mock_auction_input)

        consume_api.insert_auction(self.us_region_api, self.mock_connected_realm_id)
        inserted_record = Auction.objects.get(auction_id = 1)

        for field in mock_auction_input.keys(): 
            self.assertEqual(mock_auction_input.get(field), inserted_record.values().get(field))

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass

    def test_consume_auctions_success(self):
        pass
