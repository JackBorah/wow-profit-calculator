from django.http import Http404
from django.views.generic import DetailView, ListView
from calculator.models import ProfessionIndex, ProfessionTier, Recipe, RecipeCategory, Realm

# Create your views here.

class ProfessionIndexView(ListView):
    model = ProfessionIndex
    template_name = 'profession_index.html'

class ProfessionTiersView(ListView):
    model = ProfessionTier
    template_name = 'profession_tiers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chosen_profession = self.kwargs['profession']
        context['filtered_profession_tier_list'] = ProfessionTier.objects.filter(profession__name=chosen_profession)

        if not context['filtered_profession_tier_list']:
            raise Http404
    
        return context

class RecipeCategoriesView(ListView):
    #needs categories and recipes to list recipes under their category
    model = RecipeCategory
    template_name = 'recipe_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chosen_tier = self.kwargs['tier']
        context['filtered_profession_categories_list'] = RecipeCategory.objects.filter(profession_tier__name = chosen_tier)
        context['recipe_list'] = Recipe.objects.filter(recipe_category__profession_tier__name = chosen_tier).order_by('name')
        context['test'] = [1,2,3]

        if not context['filtered_profession_categories_list']:
            raise Http404
        if not context['filtered_profession_categories_list']:
            raise Http404
    
        return context

class RecipeCalculatorView(DetailView):
    template_name = "recipe_calculator.html"

    model = Recipe
        
    def get_context_data(self, **kwargs):
        context = super(RecipeCalculatorView, self).get_context_data(**kwargs)
        
        realm = self.kwargs['realm']
        region = self.kwargs['region']
        connected_realm_id = Realm.objects.get(name=realm, region=region).connected_realm.connected_realm_id

        product_auction_list = []
        mat_auction_list = []

        context['product_set'] = context['recipe'].product_set.all()
        for product in context['product_set']:
            products_and_auctions = []
            products_and_auctions.append(product)
            products_and_auctions.append(product.item.auction_set.filter(connected_realm_id=connected_realm_id).order_by('buyout' ,'bid' ,'unit_price'))
            product_auction_list.append(products_and_auctions)
        context['product_auction_set'] = product_auction_list #[[product, products_auctions], ...]

        context['mats_set'] = context['recipe'].mats.all()
        for mat in context['mats_set']:
            mats_and_auctions = []
            mats_and_auctions.append(mat)
            mats_and_auctions.append(mat.item.auction_set.filter(connected_realm_id=connected_realm_id).order_by('buyout' ,'bid' ,'unit_price'))
            mat_auction_list.append(mats_and_auctions)
        context['mats_auction_set'] = mat_auction_list #[[mat, mat_auctions], ...]

        return context

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