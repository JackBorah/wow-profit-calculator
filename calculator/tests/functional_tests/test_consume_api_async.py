from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from textwrap import dedent
import asyncio
import unittest
from pprint import pprint

from asgiref.sync import async_to_sync, sync_to_async
from django.test import TestCase, TransactionTestCase
from calculator.models import *
from calculator.consume_api_async import Insert
from django.db import transaction

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TestInsertIntoCleanDB(unittest.IsolatedAsyncioTestCase):
    # def setUp(self) -> None:
    #     self.insert_test = async_to_sync(Insert.create)('us')

    # this raises event loop is closed error. No clue why.
    # A warning is not raised when httpx client isn't closed. I thought this would happen.
    # def tearDown(self) -> None:
    #     async_to_sync(self.insert_test.wowapi.close)()

    # Problems still live
    # spells have multiple names with different spell ids
    # the last spell id is overwriting previous ones
    # the recipe spell is needed not anyother.

    async def test_insert_all_data():
        pass

    async def test_insert_connected_realms_index(self):
        await sync_to_async(print)(ConnectedRealmsIndex.objects.all())

        insert_test = await Insert.create('us')
        await insert_test.insert_connected_realms_index()

        await sync_to_async(print)(ConnectedRealmsIndex.objects.all())

    async def test_insert_regions(self):
        insert_test = await Insert.create('us')
        await insert_test.insert_regions()
        await sync_to_async(print)(Region.objects.all())

    async def test_insert_all_realms(self):
        insert_test = await Insert.create('us')
        await insert_test.insert_all_realms()
        await sync_to_async(print)(Realm.objects.all())

    async def test_insert_modified_crafting_reagent_slot(self):
        insert_test = await Insert.create('us')
        await insert_test.insert_modified_crafting_reagent_slot()
        await sync_to_async(print)(OptionalMaterialSlot.objects.all())

    async def test_insert_all_dragonflight_items(self):
        insert_test = await Insert.create('us')
        await insert_test.insert_all_dragonflight_items()
        await sync_to_async(print)(Item.objects.all())

    async def test_insert_optional_material_crafting_stats(self):
        insert_test = await Insert.create('us')
        await insert_test.insert_optional_material_crafting_stats()
        await sync_to_async(print)(CraftingStats.objects.all())


    async def test_insert_dragonflight_profession_tree(self):
        insert_test = await Insert.create('us')
        try:
            await insert_test.insert_dragonflight_profession_tree()
        except BaseException as e:
            await ProfessionIndex.objects.all().adelete()
            await RecipeCategory.objects.all().adelete()
            await Recipe.objects.all().adelete()
            await Material.objects.all().adelete()
            raise e
        await sync_to_async(print)(ProfessionIndex.objects.all())
        await sync_to_async(print)(RecipeCategory.objects.all())
        await sync_to_async(print)(Recipe.objects.all())
        await sync_to_async(print)(Material.objects.all())


class TestNoDB(unittest.IsolatedAsyncioTestCase):
    async def test_get_all_spells(self):
        insert_test = await Insert.create('us')
        all_spells = insert_test.get_all_spells()
        print(len(all_spells))
        print(all_spells)

    async def test_get_product_quantity(self):
        insert_test = await Insert.create('us')
        all_product_quantities = insert_test.get_product_quantity()
        count_of_0 = 0
        count_of_other_numbers = 0
        for value in all_product_quantities.values():
            if value == 0.0:
                count_of_0 += 1
            else:
                count_of_other_numbers += 1
        print(count_of_0)
        print(count_of_other_numbers)
        # print(all_product_quantities)

    async def test_get_recipe_spell_id_by_recipe_id(self):
        problem_recipe_id = 47414
        insert_test = await Insert.create('us')

        returned_spell_id = await insert_test.get_recipe_spell_id_by_recipe_id(problem_recipe_id)
        expected_wrong_spell_id = 315132
        expected_correct_spell_id = 382408

        self.assertEqual(expected_correct_spell_id, returned_spell_id)

