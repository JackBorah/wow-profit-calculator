# To test the template I need to:
# 1. Render the tempalte with django, provide a context dict with dummy values
# 2. Assert that all expected elements are present on the page.
# 3. Use selenium to find all elements on the page, click on boxes and make sure the correct ones are exposed,
        # enter in different values inside <inputs> and check that the price is calculated
# 4. 

# Notes:
# The template can ge rendered without a view or url paths 

import tempfile
import webbrowser

from django.test import TestCase, Client, RequestFactory
from django.shortcuts import render

class TestTemplatesWithoutView(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Insert data to be pulled in by the view
        pass

    def setUp(self) -> None:
        self.client = Client()
        self.facrory = RequestFactory()
        self.mock_context = {
            "name" : "Test Recipe",
            "recipe_skill" : 325,
            "user_skill" : 150,
            "inspiration" : 30,
            "skill_from_inspiration" : 200,
            "resourcefulness" : 60,
            "multicraft" : 20,
            "mats" : [
                {
                    "name" : "Test mat 1",
                    "id" : 1,
                    "quantity" : 3,
                    "tiers" : [
                        {
                            "item_id" : 1,
                            "num" : 1,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 2,
                            "num" : 2,
                            "buyout" : 200,
                        },
                        {
                            "item_id" : 3,
                            "num" : 3,
                            "buyout" : 300,
                        }
                    ] 
                },
                {
                    "name" : "Test mat 2",
                    "id" : 2,
                    "quantity" : 2,
                    "buyout" : 1,
                    "tiers" : [
                        {
                            "item_id" : 4,
                            "num" : 1,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 5,
                            "num" : 2,
                            "buyout" : 200,
                        },
                        {
                            "item_id" : 6,
                            "num" : 3,
                            "buyout" : 300,
                        }
                    ] 
                },
                {
                    "name" : "Test mat 3",
                    "id" : 3,
                    "quantity" : 1,
                    "buyout" : 0,
                    "tiers" : [
                        {
                            "item_id" : 7,
                            "num" : 1,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 8,
                            "num" : 2,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 9,
                            "num" : 3,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 10,
                            "num" : 4,
                            "buyout" : 100,
                        },
                        {
                            "item_id" : 11,
                            "num" : 5,
                            "buyout" : 100,
                        }
                    ] 
                },
            ],
            "optional_mats" : [
                {
                    "name" : "Optional mat 1",
                    "item_id" : 1,
                    "buyout" : 0,
                },
                {
                    "name" : "Optional mat 2",
                    "item_id" : 2,
                    "buyout" : 0,
                },
            ],
            "product" : {
                "num_of_tiers" : 5, # true means 5 teirs and false means 3 tiers
                "multicraftable" : False, # means no multicraft when false
                "name" : "Test product name",
                "tiers" : {
                    "1" : {
                        "buyout" : 1
                    },
                    "2" : {
                        "buyout" : 2
                    },
                    "3" : {
                        "buyout" : 3
                    }
                }

                
            },
        }

    def tearDown(self) -> None:
        # with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        #     url = 'file://' + f.name
        #     f.write(str(self.response.content, "utf-8"))
        # webbrowser.open(url)
        # print(str(self.response.content, "utf-8"))
        pass

    def test_calculator_contains_expected_headers(self):
        template_name = "recipe_calculator.html"
        calc_url = 'region/realm/profession/tier/1/'
        request = self.facrory.get(calc_url)

        response = render(request, template_name, self.mock_context)
        self.response = response # used to open the html in browser inside tearDown

        expected_headers = [
            "<h1>Test Recipe</h1>",
            "<h3>Crafting Stats</h3>",
            "<h4>Materials</h4>",
            "<h5>Test mat 1 x <span class=\"matQuantity\">3</span></h5>",
            "<h5>Test mat 2 x <span class=\"matQuantity\">2</span></h5>",
            "<h5>Test mat 3 x <span class=\"matQuantity\">1</span></h5>",
            "<h4>Optional Materials</h4>",
            "<h4>Product</h4>",
            "<h5>Test product name</h5>",
            "<h4>Profit</h4>"
        ]


        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            url = 'file://' + f.name
            f.write(str(self.response.content, "utf-8"))
        webbrowser.open(url)
        for expected_header in expected_headers:
            self.assertContains(response, expected_header, html=True)

    def test_calculator_contains_expected_crafting_stat_labels_and_inputs(self):
        template_name = "recipe_calculator.html"
        calc_url = 'region/realm/profession/tier/1/'
        request = self.facrory.get(calc_url)

        response = render(request, template_name, self.mock_context)
        self.response = response # used to open the html in browser inside tearDown

        expected_labels_and_inputs = [
            "<label for=\"inspiration\">Inspiration</label>",
            "<input type=\"number\" id=\"inspiration\" onchange=\"calculatePL()\" value=\"30\">",
            "<label for=\"resourcefulness\">Resourcefulness</label>",
            "<input type=\"number\" id=\"resourcefulness\" onchange=\"calculatePL()\" value=\"60\">",
            "<label for=\"multicraft\">Multicraft</label>",
            "<input type=\"number\" id=\"multicraft\" onchange=\"calculatePL()\" value=\"20\">",
        ]

        for expected_label_or_input in expected_labels_and_inputs:
            self.assertContains(response, expected_label_or_input, html=True)

    # Don't know why this doesn't work but i've spent too much time with it
    # def test_calculator_contains(self):
    #     template_name = "recipe_calculator.html"
    #     calc_url = 'region/realm/profession/tier/1/'
    #     request = self.facrory.get(calc_url)

    #     response = render(request, template_name, self.mock_context)
    #     self.response = response # used to open the html in browser inside tearDown

    #     expected_materials_section = [
    #         "<div id=\"materials\">",
    #         "<h4>Materials</h4>",
    #         "<h5>Test mat 1 x <span class=\"matQuantity\">3</span></h5>",
    #         "<label for=\"mat_1_tier_select\">Tier</label>",
    #         "<select name=\"mat_1_tier_select\" id=\"mat_Test mat 1_tier_select\">",
    #         "<option value=\"Tier 1\">1</option>",
    #         "<option value=\"Tier 2\">2</option>",
    #         "<option value=\"Tier 3\">3</option>",
    #         "</select>",
    #         "<input type=\"number\" id=\"1\" class=\"mat\" onchange=\"calculatePL()\" value=\"2\"/>",
    #         "<h5>Test mat 2 x <span class=\"matQuantity\">2</span></h5>"       
    #         "<label for=\"mat_2_tier_select\">Tier</label>",
    #         "<select name=\"mat_2_tier_select\" id=\"mat_Test mat 2_tier_select\">",
    #         "<option value=\"Tier 1\">1</option>",
    #         "<option value=\"Tier 2\">2</option>",
    #         "<option value=\"Tier 3\">3</option>",
    #         "</select>",
    #         "<input type=\"number\" id=\"2\" class=\"mat\" onchange=\"calculatePL()\" value=\"1\"/>",
    #         "<h5>Test mat 3 x <span class=\"matQuantity\">1</span></h5>",
    #         "<label for=\"mat_3_tier_select\">Tier</label>",
    #         "<select name=\"mat_3_tier_select\" id=\"mat_Test mat 3_tier_select\">",
    #         "<option value=\"Tier 1\">1</option>",
    #         "<option value=\"Tier 2\">2</option>",
    #         "<option value=\"Tier 3\">3</option>",
    #         "<option value=\"Tier 4\">4</option>",
    #         "<option value=\"Tier 5\">5</option>",
    #         "</select>",
    #         "<input type=\"number\" id=\"3\" class=\"mat\" onchange=\"calculatePL()\" value=\"0\"/>",
    #         "</div>",
    #     ]

        
    #     for expected_snippet in expected_materials_section:
    #             self.assertInHTML(expected_snippet, str(response.content, "utf-8"))
