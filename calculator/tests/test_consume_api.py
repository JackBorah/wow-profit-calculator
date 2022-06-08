"""Tests for the consume_api.py module"""
from django.test import TestCase
import responses
from getwowdata import urls
from getwowdata import WowApi
from calculator.models import *
from calculator.consume_api import *



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

    @responses.activate
    def test_consume_realm_yield_correct(self):
        """Unit test for consume_realm."""
        responses.get(
            urls["search_realm"].format(region="us"),
            json={
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
            },
        )
        connected_realm_id = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        search_results = next(consume_realm(us_region_api))
        expected_yield = {
            "connected_realm_id": connected_realm_id,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region": "North America",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }

        self.assertDictEqual(expected_yield, search_results)
