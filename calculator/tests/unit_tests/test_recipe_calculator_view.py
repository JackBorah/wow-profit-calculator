from datetime import datetime
from pprint import pprint
import unittest
from django.test import TestCase, Client
from calculator.models import *
import bs4

class TestRecipeCalculator(TestCase):
    # A url is requested with the recipes id
    # Recipe calculator takes grabs the requested recipe from the db.
    # A loop renders an <input> for each reagent. 
    # Default value (in the else statement) is 0 otherwise <inputs> have most recent auction price
    # A talent tree page exists with the full tree with all discriptions
        # This page will also be where tools and accessories + enchants are set
        # and the users base skill 
        # I think a lightweight version of trees and tool should exist somewhere on the recipe page but thats for later
    # The talent tree calculates the stats for all different item types
        # Like trade goods, mail armor, leather armor, and others will have different values
        # That will be calculated when the tree is updated
        # Pros: 
            # calculate once and just read variables after.
        # Cons:
            # dozens of variables for each different item type and their stats
            # like mail_armor has its own inspiration and resourcefulness
            # trade goods has their own  inspiration, resourcefulness, and multicraft
    # The users talent tree is saved to their session
    # The recipe type (trade good, mail armor, ...) is checked and those stats are retrieved
    # checkboxes for each optional item
        # when checked their stats are added to the calculation and their price is added to the cost
        # How should bop optional reagents be calculated?
            # Their cost will be 0 by default and their stats added when checked
    # How should bop reagents be handled?
        # Indicate they are bop through a wowhead tooltip, maybe literally labeling it with 'bind on pickup'
        # cost is set to 0 by default but would be factored in like any other stat if user gives it a value
    # How should bop products be handled?
        # output the cost if the product is bop
    # profit is calculated with inspiration, multicraft, and resourcefulness factored in
    # the profit_calculator script is set to each inputs onchange=
    # the p/l is output to a box
    # Now whenever each input is modified a profit is calculated with that recipes specific stats
    # Apply this generally and boom a calculator for all recipes
    # 
    # After call this calculator func to calculate the profit for the whole profession
    # At a glance the user would see the p/l of all recipes in their profession

    pass


# class RealRecipeCalculatorViewTestCase(unittest.TestCase):        

#     def test_price_input_fields_not_empty(self):
#         """Check all inputs for all recipes for empty value attributes.
        
#             Empty values need to be replaced with sane default values.
#         """
#         professions = ProfessionIndex.objects.all()
#         profession_tiers = ProfessionTier.objects.all() 
#         recipe_categories = RecipeCategory.objects.all() 
#         recipes = Recipe.objects.all()      

#         c = Client()
#         for profession in professions:
#             for profession_tier in profession_tiers.filter(profession=profession):
#                 for recipe_category in recipe_categories.filter(profession_tier=profession_tier):
#                     for recipe in recipes.filter(recipe_category=recipe_category):
#                         url = f'/North%20America/Illidan/{profession.name}/{profession_tier.name}/{recipe.id}/'
#                         res = c.get(url, follow=True)
#                         soup = bs4.BeautifulSoup(res.content, 'xml')
#                         inputs = soup.find_all(lambda m: m.name == 'input' and m.attrs.get('value') == '')
#                         for input in inputs:
#                             print(url)
#                             print(input)
#                             self.assertNotEqual(input['value'], '')

# class RecipeCalculatorViewTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         conn_realm_id = ConnectedRealmsIndex.objects.create(connected_realm_id=1)
#         Realm.objects.create(connected_realm=conn_realm_id, population="Low", realm_id=1, name="Test Realm", region="Test Region", timezone="GMT", play_style="Normal")
#         bonus = ItemBonus.objects.create(id=1)
#         item = Item.objects.create(id=1, name="Test Item")
#         profession = ProfessionIndex.objects.create(id=1, name="Test Profession")
#         profession_tier = ProfessionTier.objects.create(
#             id=1, name="Test Tier", profession=profession
#         )
#         recipe_category = RecipeCategory.objects.create(
#             name="Test category", profession_tier=profession_tier
#         )
#         material = Material.objects.create(item=item, quantity=1)
#         recipe = Recipe.objects.create(
#             id=1, name="Test recipe", recipe_category=recipe_category
#         )
#         recipe.mats.add(material)
#         auction = Auction.objects.create(
#                 auction_id = 1,
#                 buyout = 100,
#                 bid = 99,
#                 quantity = 1,
#                 time_left = "Short",
#                 timestamp = datetime(1999, 10, 10, 1),
#                 connected_realm = conn_realm_id,
#                 item = item,
#         )
#         auction.bonuses.add(bonus)

#     def test_price_input_fields_not_empty(self):
#         c = Client()
#         res = c.get('/Test%20Region/Test%20Realm/Test%20Profession/Test%20Tier/1/', follow=True)
#         pprint(res.rendered_content)
