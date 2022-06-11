"""Tests for the consume_api.py module"""
from unittest.mock import MagicMock
from django.test import TestCase
import responses
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


    region = 'us'
    responses.post(
        urls["access_token"].format(region=region),
        json={"access_token": "0000000000000000000000000000000000"},
    )
    us_region_api = WowApi("us", "test_client_id", "test_client_secret")

    @classmethod
    def setUpTestData(cls):
        ConnectedRealmsIndex.objects.create(connected_realm_id=1)

    def test_consume_realm_yield_success(self):
        """Unit test for consume_realm."""

        self.us_region_api.connected_realm_search = MagicMock(return_value={
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
            })

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

        self.assertDictEqual(expected_yield, consume_output)

    def test_insert_realm_success(self):
        connected_realm_id = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        consume_realm_results = {
            "connected_realm_id": connected_realm_id,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region": "North America",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }

        consume_api.consume_realm = MagicMock(return_value = [consume_realm_results])
        consume_api.insert_realm(self.us_region_api)

        record = Realm.objects.get(realm_id=2)

        self.assertEqual(consume_realm_results.get('connected_realm_id').connected_realm_id, record.connected_realm_id)
        self.assertEqual(consume_realm_results.get('population'), record.population)
        self.assertEqual(consume_realm_results.get('realm_id'), record.realm_id)
        self.assertEqual(consume_realm_results.get('name'), record.name)
        self.assertEqual(consume_realm_results.get('region'), record.region)
        self.assertEqual(consume_realm_results.get('timezone'), record.timezone)
        self.assertEqual(consume_realm_results.get('play_style'), record.play_style)
        
    def test_consume_connected_realms_index_success(self):
        pass