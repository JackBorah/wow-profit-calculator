from datetime import datetime
from pprint import pprint
import unittest
from django.test import TestCase, Client
from calculator.models import *
import bs4

class RealRecipeCalculatorViewTestCase(unittest.TestCase):        

    def test_price_input_fields_not_empty(self):
        """Check all inputs for all recipes for empty value attributes.
        
            Empty values need to be replaced with sane default values.
        """
        professions = ProfessionIndex.objects.all()
        profession_tiers = ProfessionTier.objects.all() 
        recipe_categories = RecipeCategory.objects.all() 
        recipes = Recipe.objects.all()      

        c = Client()
        for profession in professions:
            for profession_tier in profession_tiers.filter(profession=profession):
                for recipe_category in recipe_categories.filter(profession_tier=profession_tier):
                    for recipe in recipes.filter(recipe_category=recipe_category):
                        url = f'/North%20America/Illidan/{profession.name}/{profession_tier.name}/{recipe.id}/'
                        res = c.get(url, follow=True)
                        soup = bs4.BeautifulSoup(res.content, 'xml')
                        inputs = soup.find_all(lambda m: m.name == 'input' and m.attrs.get('value') == '')
                        for input in inputs:
                            print(url)
                            print(input)
                            self.assertNotEqual(input['value'], '')

class RecipeCalculatorViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        conn_realm_id = ConnectedRealmsIndex.objects.create(connected_realm_id=1)
        Realm.objects.create(connected_realm=conn_realm_id, population="Low", realm_id=1, name="Test Realm", region="Test Region", timezone="GMT", play_style="Normal")
        bonus = ItemBonus.objects.create(id=1)
        item = Item.objects.create(id=1, name="Test Item")
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
        auction = Auction.objects.create(
                auction_id = 1,
                buyout = 100,
                bid = 99,
                quantity = 1,
                time_left = "Short",
                timestamp = datetime(1999, 10, 10, 1),
                connected_realm = conn_realm_id,
                item = item,
        )
        auction.bonuses.add(bonus)

    def test_price_input_fields_not_empty(self):
        c = Client()
        res = c.get('/Test%20Region/Test%20Realm/Test%20Profession/Test%20Tier/1/', follow=True)
        pprint(res.rendered_content)
