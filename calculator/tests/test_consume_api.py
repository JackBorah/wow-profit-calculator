"""Tests for the consume_api.py module """

# A common bug was str has no get attribute. This is caused by
# looping through a dict (its keys) instead of a generator obj.
# To solve this mock data intended to be a generator obj is wrapped
# in a list.

import datetime
from unittest.mock import MagicMock
from psycopg2 import connect
import responses
from django.test import TestCase
from getwowdata import urls
from getwowdata import WowApi
from calculator.models import *
from calculator import consume_api


class TestConsumeApi(TestCase):
    region = "us"
    mock_recipe_id = 1
    mock_connected_realm_id = 1
    mock_profession_id = 1
    mock_skill_tier_id = 1
    current_date = datetime.datetime.now()
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
        item = Item.objects.create(id=1, name="item_test")
        profession = ProfessionIndex.objects.create(id=1, name="Test Profession")
        profession_tier = ProfessionTier.objects.create(
            id=1, name="Test Tier", profession=profession
        )
        recipe_category = RecipeCategory.objects.create(
            name="Test category", profession_tier=profession_tier
        )
        material = Material.objects.create(item=item, quantity=1)
        recipe = Recipe.objects.create(
            id=1, name="Test recipe", product=item,product_quantity = 1, recipe_category=recipe_category
        )
        recipe.mats.add(material)

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

        self.assertDictEqual(expected_yield, consume_output)

    def test_insert_realm_success(self):
        """Unit test for insert_realm correctly inserting values into db."""
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

        # The return value is wrapped in a list to simulate a generator object
        consume_api.consume_realm = MagicMock(return_value=[consume_realm_results])
        consume_api.insert_realm(self.us_region_api)

        record = Realm.objects.filter(realm_id=2)
        record_fields = record.values().get()

        expected_record = {
            "connected_realm_id": 1,
            "population": "FULL",
            "realm_id": 2,
            "name": "TestServer",
            "region": "North America",
            "timezone": "America/New_York",
            "play_style": "NORMAL",
        }

        for field in record_fields:
            self.assertEqual(expected_record.get(field), record_fields.get(field))

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
        self.maxDiff = None
        mock_get_auctions_return = {
            "auctions": [
                {
                    "id": 1,
                    "buyout": 1,
                    "bid": 1,
                    "unit_price": 1,
                    "quantity": 1,
                    "time_left": "SHORT",
                    "item": {
                        "id": 1,
                        "pet_level": 1,
                        "bonus_lists": [1, 2],
                        "modifiers": [{"type": 1, "value": 1}],
                    },
                }
            ]
        }
        self.us_region_api.get_auctions = MagicMock(
            return_value=mock_get_auctions_return
        )
        actual_yield = next(
            consume_api.consume_auctions(
                self.us_region_api, self.mock_connected_realm_id
            )
        )

        item_obj = Item.objects.get(id=1)
        connected_realm_obj = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        item_bonus_list = [ItemBonus.objects.get(id=1), ItemBonus.objects.get(id=2)]
        item_modifier_list = [
            ItemModifier.objects.filter(modifier_type=1).filter(value=1).get()
        ]

        expected_yield = {
            "auction_id": 1,
            "buyout": 1,
            "bid": 1,
            "unit_price": 1,
            "quantity": 1,
            "time_left": "SHORT",
            "connected_realm_id": connected_realm_obj,
            "item": item_obj,
            "pet_level": 1,
            "item_bonus_list": item_bonus_list,
            "item_modifier_list": item_modifier_list,
        }
        self.assertDictEqual(expected_yield, actual_yield)

    def test_insert_auctions_success(self):
        """Unit test for correctly inserting auctions into db."""
        item_obj = Item.objects.get(id=1)
        connected_realm_obj = ConnectedRealmsIndex.objects.get(connected_realm_id=1)
        item_bonus_list = [ItemBonus.objects.get()]
        item_modifier_list = [
            ItemModifier.objects.filter(modifier_type=1).filter(value=1).get()
        ]

        mock_auction_input = {
            "auction_id": 1,
            "buyout": 1,
            "bid": 1,
            "unit_price": 1,
            "quantity": 1,
            "time_left": "SHORT",
            "connected_realm_id": connected_realm_obj,
            "item": item_obj,
            "pet_level": 1,
            "item_bonus_list": item_bonus_list,
            "item_modifier_list": item_modifier_list,
            "timestamp": self.current_date,
        }

        # Mocked input is wrapped in a list to mock a generator object
        consume_api.consume_auctions = MagicMock(return_value=[mock_auction_input])

        consume_api.insert_auction(self.us_region_api, self.mock_connected_realm_id)
        record = Auction.objects.filter(auction_id=1)
        record_fields = record.values().get()

        record_bonus_set = record.get().itembonus_set.all().first()
        record_modifier_set = record.get().itemmodifier_set.all().first()
        expected_record = {
            "auction_id": 1,
            "buyout": 1,
            "bid": 1,
            "unit_price": 1,
            "quantity": 1,
            "time_left": "SHORT",
            "connected_realm_id": 1,
            "item_id": 1,
            "pet_level": 1,
            "item_bonus_list": item_bonus_list,
            "item_modifier_list": item_modifier_list,
            "timestamp": record_fields.get("timestamp"),
        }

        self.assertEqual(
            expected_record.get("auction_id"), record_fields.get("auction_id")
        )
        self.assertEqual(expected_record.get("buyout"), record_fields.get("buyout"))
        self.assertEqual(expected_record.get("bid"), record_fields.get("bid"))
        self.assertEqual(
            expected_record.get("unit_price"), record_fields.get("unit_price")
        )
        self.assertEqual(expected_record.get("quantity"), record_fields.get("quantity"))
        self.assertEqual(
            expected_record.get("time_left"), record_fields.get("time_left")
        )
        self.assertEqual(
            expected_record.get("timestamp"), record_fields.get("timestamp")
        )
        self.assertEqual(
            expected_record.get("connected_realm_id"),
            record_fields.get("connected_realm_id"),
        )
        self.assertEqual(expected_record.get("item_id"), record_fields.get("item_id"))
        self.assertEqual(
            expected_record.get("pet_level"), record_fields.get("pet_level")
        )
        self.assertEqual(expected_record.get("item_bonus_list")[0], record_bonus_set)
        self.assertEqual(
            expected_record.get("item_modifier_list")[0], record_modifier_set
        )

    def test_consume_item_bonus_success(self):
        self.us_region_api.get_auctions = MagicMock(
            return_value={
                "auctions": [
                    {
                        "item": {
                            "id": 1,
                            "bonus_lists": [3],
                        }
                    }
                ]
            }
        )
        actual_yield = next(
            consume_api.consume_item_bonus(
                self.us_region_api, self.mock_connected_realm_id
            )
        )
        expected_yield = 3
        self.assertEqual(expected_yield, actual_yield)

    def test_insert_item_bonus_success(self):
        consume_api.consume_item_bonus = MagicMock(return_value=[3])
        consume_api.insert_item_bonus(self.us_region_api, self.mock_connected_realm_id)
        actual_record = ItemBonus.objects.get(id=3)
        expected_record = ItemBonus(id=3)
        self.assertEqual(expected_record, actual_record)

    def test_consume_item_modifiers_success(self):
        self.us_region_api.get_auctions = MagicMock(
            return_value={
                "auctions": [
                    {
                        "item": {
                            "modifiers": [{"type": 3, "value": 3}],
                        }
                    }
                ]
            }
        )
        actual_yield = next(
            consume_api.consume_item_modifiers(
                self.us_region_api, self.mock_connected_realm_id
            )
        )
        expected_yield = (3, 3)
        self.assertEqual(expected_yield, actual_yield)

    def test_insert_item_modifiers_success(self):
        consume_api.consume_item_modifiers = MagicMock(return_value=[(3, 3)])
        consume_api.insert_item_modifiers(
            self.us_region_api, self.mock_connected_realm_id
        )
        actual_record = ItemModifier.objects.get(modifier_type=3)
        expected_record = ItemModifier(id=2, modifier_type=3, value=3)
        self.assertEqual(expected_record, actual_record)

    def test_consume_profession_index_success(self):
        self.us_region_api.get_profession_index = MagicMock(
            return_value={"professions": [{"id": 1, "name": "test"}]}
        )
        actual_yield = next(consume_api.consume_profession_index(self.us_region_api))
        expected_yield = {"name": "test", "id": 1}
        self.assertEqual(expected_yield, actual_yield)

    def test_insert_profession_index_success(self):
        consume_api.consume_profession_index = MagicMock(
            return_value=[{"name": "test", "id": 1}]
        )
        consume_api.insert_profession_index(self.us_region_api)
        actual_record = ProfessionIndex.objects.get(name="test")
        expected_record = ProfessionIndex(name="test", id=1)
        self.assertEqual(expected_record, actual_record)

    def test_consume_profession_tier_success(self):
        self.us_region_api.get_profession_tiers = MagicMock(
            return_value={"id": 1, "skill_tiers": [{"name": "Test", "id": 1}]}
        )
        profession_index_obj = ProfessionIndex.objects.get(id=1)
        actual_yield = next(
            consume_api.consume_profession_tier(
                self.us_region_api, self.mock_profession_id
            )
        )
        expected_yield = {"profession": profession_index_obj, "name": "Test", "id": 1}
        self.assertDictEqual(expected_yield, actual_yield)

    def test_insert_profession_tier_success(self):
        consume_api.consume_profession_tier = MagicMock(
            return_value=[{"profession_id": 1, "name": "Test", "id": 1}]
        )
        consume_api.insert_profession_tier(self.us_region_api, self.mock_profession_id)
        profession_index_obj = ProfessionIndex.objects.get(id=1)
        actual_record = ProfessionTier.objects.get(id=1)
        expected_record = ProfessionTier(
            id=1, name="Test", profession=profession_index_obj
        )
        self.assertEqual(expected_record, actual_record)

    def test_consume_recipe_category_success(self):
        self.us_region_api.get_profession_tier_categories = MagicMock(
            return_value={
                "categories": [
                    {
                        "name": "Test Category",
                        "recipes": [{"name": "Test Recipe", "id": 1}],
                    }
                ]
            }
        )
        profession_tier_obj = ProfessionTier.objects.get(id=1)
        category_gen = consume_api.consume_recipe_category(
            self.us_region_api, self.mock_profession_id, self.mock_skill_tier_id
        )
        actual_yield_category_name_and_tier_obj = next(category_gen)
        actual_yield_recipe_name_and_recipe_id = next(category_gen)
        expected_yield_category_name_and_tier_obj = {
            "category_name": "Test Category",
            "profession_tier_obj": profession_tier_obj,
        }
        expected_yield_recipe_name_and_recipe_id = {
            "recipe_name": "Test Recipe",
            "recipe_id": 1,
        }
        self.assertDictEqual(
            expected_yield_category_name_and_tier_obj,
            actual_yield_category_name_and_tier_obj,
        )
        self.assertDictEqual(
            expected_yield_recipe_name_and_recipe_id,
            actual_yield_recipe_name_and_recipe_id,
        )

    def test_insert_recipe_category_success(self):
        profession_tier_obj = ProfessionTier.objects.get(id=1)
        mock_recipe_category_input = {
            "recipe_name": "Test Recipe record",
            "recipe_id": 2,
            "category_name": "Test Category record",
            "profession_tier_obj": profession_tier_obj,
        }
        consume_api.consume_recipe_category = MagicMock(
            return_value=[mock_recipe_category_input]
        )
        consume_api.insert_recipe_category(
            self.us_region_api, self.mock_profession_id, self.mock_skill_tier_id
        )
        actual_record_category = RecipeCategory.objects.get(name="Test Category record")
        actual_record_recipe = Recipe.objects.get(id=2)
        expected_record_category = RecipeCategory(
            id=2,
            name=mock_recipe_category_input.get("category_name"),
            profession_tier=mock_recipe_category_input.get("profession_tier_obj"),
        )
        expected_record_recipe = Recipe(
            id=mock_recipe_category_input.get("recipe_id"),
            name=mock_recipe_category_input.get("recipe_name"),
            recipe_category=expected_record_category,
        )

        self.assertEqual(expected_record_category, actual_record_category)
        self.assertEqual(expected_record_recipe, actual_record_recipe)

    def test_consume_recipe_success(self):
        mock_json = {
            'id':1,
            'name':'Test recipe',
            'crafted_item': {'id':1},
            'crafted_quantity': {'value':1},
            'reagents': [{'reagent': {'id':1}, 'quantity':1}]
        }
        self.us_region_api.get_recipe = MagicMock(return_value = mock_json)
        product_obj = Item.objects.get(id=1)
        material_obj = Material.objects.get(pk=1)
        actual_yield = consume_api.consume_recipe(self.us_region_api, self.mock_recipe_id)
        expected_yield = {
            'recipe_name': mock_json.get('name'),
            'product_obj': product_obj,
            'product_quantity': mock_json.get('crafted_quantity').get('value'),
            'materials_list': [material_obj]
        }
        self.assertDictEqual(expected_yield, actual_yield)

    def test_insert_recipe_success(self):
        product_obj = Item.objects.get(id=1)
        material_obj = Material.objects.get(pk=1)
        recipe_category_obj = RecipeCategory.objects.get(id=1)
        recipe_input = {
            'recipe_name': 'Test recipe',
            'product_obj': product_obj,
            'product_quantity': 1,
            'materials_list': [material_obj]
        }
        consume_api.consume_recipe = MagicMock(return_value=recipe_input)
        consume_api.insert_recipe(self.us_region_api, self.mock_recipe_id)
        actual_record = Recipe.objects.get(id=1)
        expected_record = Recipe(id=self.mock_recipe_id, name = 'Test recipe', product=product_obj,product_quantity = recipe_input.get('product_quantity'), recipe_category=RecipeCategory.objects.get(id=1))
        expected_record.mats.add(material_obj)
        self.assertEqual(expected_record, actual_record)

    def test_consume_all_item_success(self):
        mock_items_json = {
            'results':[
                {
                    'data':{'id':1, 'name':{'en_US':'Test item 1'}}
                },
                {
                    'data':{'id':2, 'name':{'en_US':'Test item 2'}}
                },
                {
                    'data':{'id':3, 'name':{'en_US':'Test item 3'}}
                }
            ]
        }

        self.us_region_api.item_search = MagicMock(return_value = mock_items_json)
        generator_obj_items = consume_api.consume_all_item(self.us_region_api)
        actual_yield_1 = next(generator_obj_items)
        actual_yield_2 = next(generator_obj_items)
        actual_yield_3 = next(generator_obj_items)
        expected_yield_1 = {'item_id':1, 'name':'Test item 1'}
        expected_yield_2 = {'item_id':2, 'name':'Test item 2'}
        expected_yield_3 = {'item_id':3, 'name':'Test item 3'}
        self.assertDictEqual(expected_yield_1,actual_yield_1)
        self.assertDictEqual(expected_yield_2,actual_yield_2)
        self.assertDictEqual(expected_yield_3,actual_yield_3)

    def test_insert_all_item_success(self):
        mock_consume_item_yield = {'item_id':2, 'name':'Test item 1'}
        consume_api.consume_all_item = MagicMock(return_value = [mock_consume_item_yield])
        consume_api.insert_all_item(self.us_region_api)
        actual_record = Item.objects.get(id=2)
        expected_record = Item(id=mock_consume_item_yield.get('item_id'), name=mock_consume_item_yield.get('name'))
        self.assertEqual(expected_record, actual_record)

