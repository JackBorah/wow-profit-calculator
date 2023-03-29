from typing import Any, Dict

from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView
from calculator.models import *

# Create your views here.

class ProfessionIndexView(ListView):
    model = ProfessionIndex
    template_name = 'select_profession.html'

# TODO From old design and probably useless since other expansions won't be included
class ProfessionTiersIndexView(ListView):
    # model = ProfessionTier
    template_name = 'select_profession_tier.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chosen_profession = self.kwargs['profession']
        # context['filtered_profession_tier_list'] = ProfessionTier.objects.filter(profession__name=chosen_profession)

        if not context['filtered_profession_tier_list']:
            raise Http404
    
        return context

class ProfessionTierCategoriesIndexView(ListView):
    #needs categories and recipes to list recipes under their category
    model = RecipeCategory
    template_name = 'select_recipe_category.html'
    # template_name = 'test.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chosen_tier = self.kwargs['tier']
        context['filtered_profession_categories_list'] = RecipeCategory.objects.filter(profession_tier__name = chosen_tier)
        context['recipe_list'] = Recipe.objects.filter(recipe_category__profession_tier__name = chosen_tier).order_by('name')
        context['test'] = [1,2,3]

        # if not context['filtered_profession_categories_list']:
        #     raise Http404
    
        return context

class RecipeCalculatorView(TemplateView):
    template_name = "recipe_calculator.html"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        super_context = super().get_context_data(**kwargs)
        # What needs to be here?
        Recipe.objects.get()

        context = {
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
                            "buyout" : 310,
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
                            "buyout" : 200,
                        },
                        {
                            "item_id" : 9,
                            "num" : 3,
                            "buyout" : 300,
                        },
                        {
                            "item_id" : 10,
                            "num" : 4,
                            "buyout" : 400,
                        },
                        {
                            "item_id" : 11,
                            "num" : 5,
                            "buyout" : 500,
                        }
                    ] 
                },
            ],
            "optional_mats" : [
                {
                    "name" : "Optional mat 1",
                    "tiers" : [
                        {
                            "item_id" : 4,
                            "num" : 1,
                            "buyout" : 100,
                            "inspiration" : 10,
                        },
                        {
                            "item_id" : 5,
                            "num" : 2,
                            "buyout" : 200,
                            "inspiration" : 20,
                        },
                        {
                            "item_id" : 6,
                            "num" : 3,
                            "buyout" : 310,
                            "inspiration" : 30,
                        }
                    ]
                },
                {
                    "name" : "Optional mat 2",
                    "item_id" : 2,
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
                            "buyout" : 310,
                        }
                    ]
                },
            ],
            "product" : {
                "num_of_tiers": 5,
                "multicraftable": "FALSE",
                "name": "Test product name",
                "tiers": [
                    {
                        "buyout": 1,
                        "item_id": 10,
                        "num": 1
                    },
                    {
                        "buyout": 2,
                        "item_id": 20,
                        "num": 2
                    },
                    {
                        "buyout": 3,
                        "item_id": 30,
                        "num": 3
                    },
                    {
                        "buyout": 4,
                        "item_id": 40,
                        "num": 4
                    },
                    {
                        "buyout": 5,
                        "item_id": 50,
                        "num": 5
                    }
                ]
            },
        }
        super_context.update(context)
        return super_context
    
    # Needs to get data and build a context object:
    # Data Needed: 
        # Recipe
        # input and product items + all tiers of the items
        # auctions filtered by item
        # talent tree from session
        # base skill from session
        # optional materials stat buffs
        # Needs skill for each recipe
        # needs the prices of all tiers of item for inspiration purposes
        # just found out that items don't have different ids per item level
            # Means i need to figure out the bonus lists for each possible tier of item
            # For tradeable items just check the auctions bonus list and compare to the ilevel
            # I believe the item livel increases are constant between items
            # meaning that a purple sword or shield of tier 1 would have the same skill requirements
            # and their ilvl's would increase the exact same way when increasing the tier
    # TODO 
    # 1. context should have a buyout variable only change unit_price to buyout
    # 2. This view should look at the recipe type and determine the crafting stats
         # and send this to the html. Since different items will have different stats based on the skill tree choices
    # 3. I think the session object makes html ugly. So take the useful session variables out in
         # inside the view and assign them a good name like Inspiration instead of using request.session.inspiration

    # model = Recipe
       
    # def get_context_data(self, **kwargs):
    #     context = super(RecipeCalculatorView, self).get_context_data(**kwargs)
        
    #     realm = self.kwargs['realm']
    #     #region = self.kwargs['region']
    #     connected_realm_id = Realm.objects.get(name=realm, region=region).connected_realm.connected_realm_id

    #     product_auction_list = []
    #     mat_auction_list = []

    #     context['product_set'] = context['recipe'].product_set.all()
    #     for product in context['product_set']:
    #         products_and_auctions = []
    #         products_and_auctions.append(product)
    #         products_and_auctions.append(product.item.auction_set.filter(connected_realm_id=connected_realm_id).order_by('buyout' ,'bid' ,'unit_price'))
    #         product_auction_list.append(products_and_auctions)
    #     context['product_auction_set'] = product_auction_list #[[product, products_auctions], ...]

    #     context['mats_set'] = context['recipe'].mats.all()
    #     for mat in context['mats_set']:
    #         mats_and_auctions = []
    #         mats_and_auctions.append(mat)
    #         mats_and_auctions.append(mat.item.auction_set.filter(connected_realm_id=connected_realm_id).order_by('buyout' ,'bid' ,'unit_price'))
    #         mat_auction_list.append(mats_and_auctions)
    #     context['mats_auction_set'] = mat_auction_list #[[mat, mat_auctions], ...]

    #     return context

#getting the profit/loss from milling/prospecting is easy. 
#price*rate + ... for each pigment/gem from an herb/ore
#Now how would the cost of herbs be found for a recipe?
#I'm making a cost model. I can assume that the unused pigment is sold or unused.
#So calculate the amount of herbs needed to make the recipe 
#then decide to count unused as sold or not.
#A problem is that pigments/inks may be sold very slowly so extras would be much lower than normal sale price to account for the high volume
#A better solution (price wise) could be to make something else like tomes with extra inks. 
#But i'm seeing that this is all modeling. The most useful system would say how to use leftovers
#acutally links to recipes that use the leftovers would be best. 

#TODO Needs milling and prospecting, prices of legos, prices for untradable mats, intermediate prices like showing milling, ink, pigment, profits for making decks so you can choose the best, better prices like average minbuyout or 1st quartile of all servers in the region, showing all available auctions somewhere, a link to the change realm and server page, a searchbar, home button, nice looking header and footer, prettier design, displaying information on index pages like what the profit is on the recipes index page next to the detail recipe link, reorder profession tiers so latest expansion is at the top, add wow tooltips from wowhead, add ilvl and faction (if applicaple) to the recipe index view, link to undermine journal page for historical data, link to wowhead for the items (through the tooltip), add support for recieps with multiple products, add support for procs, add vendor purchase and sell prices to items, make calculator use min of vendor buy and auction prices,