import asyncio
import unittest
from pprint import pprint
from django.test import TestCase

from asgiref.sync import async_to_sync, sync_to_async
from calculator.models import *
from ...consume_api_async import *

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TestInsertIntoCleanDB(TestCase):
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


    async def test_insert_all_data(self):
        try:
            await insert_all_data()
            # print(await Region.objects.afirst())
            # print(await ConnectedRealmsIndex.objects.afirst())
            # print(await Spell.objects.afirst())
            # print(await Product.objects.afirst())
            # print(await Material.objects.afirst())
            # print(await OptionalMaterial.objects.afirst())
            # print(await ModifiedCraftingReagentSlot.objects.afirst())
            # print(await CategoryReagentSlotRelationship.objects.afirst())
            # print(await ModifiedCraftingCategory.objects.afirst())
            # print(await ModifiedCraftingReagentItem.objects.afirst())
            # print(await Item.objects.afirst())
            # print(await CraftingQuality.objects.afirst())
            # print(await CraftingData.objects.afirst())
            # print(await ProfessionIndex.objects.afirst())
            # print(await RecipeCategory.objects.afirst())
            # print(await Recipe.objects.afirst())
            
        except BaseException as e:
            await Region.objects.all().adelete()
            await ConnectedRealmsIndex.objects.all().adelete()
            await Realm.objects.all().adelete()
            await Spell.objects.all().adelete()
            await Product.objects.all().adelete()
            await Material.objects.all().adelete()
            await OptionalMaterial.objects.all().adelete()
            await ModifiedCraftingReagentSlot.objects.all().adelete()
            await CategoryReagentSlotRelationship.objects.all().adelete()
            await ModifiedCraftingCategory.objects.all().adelete()
            await ModifiedCraftingReagentItem.objects.all().adelete()
            await Item.objects.all().adelete()
            await CraftingQuality.objects.all().adelete()
            await CraftingData.objects.all().adelete()
            await ProfessionIndex.objects.all().adelete()
            await RecipeCategory.objects.all().adelete()
            await Recipe.objects.all().adelete()
            await Material.objects.all().adelete()
            raise e

