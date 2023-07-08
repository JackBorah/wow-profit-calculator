from typing import Any, Dict

from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView
from calculator.models import *

# Create your views here.

class ProfessionIndexView(ListView):
    model = ProfessionIndex
    template_name = 'select_profession.html'

# # TODO From old design and probably useless since other expansions won't be included
# class ProfessionTiersIndexView(ListView):
#     # model = ProfessionTier
#     template_name = 'select_profession_tier.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         chosen_profession = self.kwargs['profession']
#         # context['filtered_profession_tier_list'] = ProfessionTier.objects.filter(profession__name=chosen_profession)

#         if not context['filtered_profession_tier_list']:
#             raise Http404
    
#         return context

class ProfessionCategoriesView(ListView):
    #needs categories and recipes to list recipes under their category
    model = RecipeCategory
    template_name = 'select_recipe_category.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profession_name=self.kwargs['profession']
        context['profession_categories_list'] = RecipeCategory.objects.filter(profession__name=profession_name).order_by('name')
        context['recipe_list'] = Recipe.objects.filter(recipe_category__profession__name=profession_name)
    
        return context

class RecipeCalculatorView(TemplateView):
    template_name = "recipe_calculator.html"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        super_context = super().get_context_data(**kwargs)

        recipe = Recipe.objects.get(id=self.kwargs["pk"])
        materials_list = recipe.material_set.all()
        optional_materials_list = recipe.optionalmaterial_set.all()
        formatted_materials = []
        # normal mats don't have different qualities except required optional mats
        for optional_material in optional_materials_list:
            if not optional_material.is_required:
                continue

            if optional_material.quantity == 0:
                continue

            if "(DNT)" in optional_material.optional_material_slot.name:
                item_name = optional_material.optional_material_slot.name[:-5]
            else:
                item_name = optional_material.optional_material_slot.name

            single_material = {
                "name" : item_name,
                "id" : optional_material.id, # not sure which id this key refers too
                "quantity" : optional_material.quantity,
                "tiers" : []
            }
            formatted_materials.append(single_material)
            relationship = optional_material.optional_material_slot.categoryreagentslotrelationship_set.get()
            modified_crafting_reagent_item_set = relationship.category.modifiedcraftingreagentitem_set.all()

            if len(modified_crafting_reagent_item_set) > 1:
                for MCR_item in modified_crafting_reagent_item_set:
                    if MCR_item.id == 93:
                        continue
                    item = MCR_item.item_set.get()
                    tier = {
                        "name" : item.name,
                        "num" : item.quality.quality_tier,
                        "buyout" : 0,
                    }
                    single_material["tiers"].append(tier)

            else:
                item_set = optional_material.optional_material_slot.categoryreagentslotrelationship_set.get().category.modifiedcraftingreagentitem_set.get().item_set.all()
                
                for item in item_set:
                    tier = {
                        "name" : item.name,
                        "num" : item.quality.quality_tier,
                        "buyout" : 0,
                    }
                    single_material["tiers"].append(tier)

        for material_record in materials_list:
            if material_record.quantity == 0:
                continue
            single_material = {
                "name" : material_record.item.name,
                "id" : material_record.id, # not sure which id this key refers too
                "quantity" : material_record.quantity,
                "tiers" : [
                    {
                        "item_id" : material_record.item.id,
                        "num" : material_record.item.quality, # should always be none since normal mats have no qualities
                        "buyout" : 0
                    }
                ]
            }
            formatted_materials.append(single_material)

        formatted_optional_mat_slots = []
        for optional_material in optional_materials_list:

            if optional_material.is_required:
                continue

            category_slot_relationships = optional_material.optional_material_slot.categoryreagentslotrelationship_set.all()
            optional_material_slot = {
                "name" : optional_material.optional_material_slot.name,
                "quantity" : optional_material.quantity,
                "categories" : []
            }
            formatted_optional_mat_slots.append(optional_material_slot)
            
            for relation in category_slot_relationships:
                category_record = relation.category
                category = {
                    "name" : category_record.name,
                    "items" : []
                }

                optional_material_slot["categories"].append(category)

                reagent_effects = category_record.craftingreagenteffect_set.all()
                reagent_quality_stat_adjustments = category_record.craftingreagentquality_set.all()
                MCR_items_from_category = relation.category.modifiedcraftingreagentitem_set.all()
                for MCR_items in MCR_items_from_category:
                    item_records = MCR_items.item_set.all()

                    for item in item_records:
                        if item.quality:
                            quality = item.quality.quality_tier
                        else:
                            quality = 1
                        item_json = {
                            "item_id" : item.id,
                            "name" : item.name,
                            "quality" : quality,
                            "buyout" : 0
                        }
                        category["items"].append(item_json)

                        if not reagent_quality_stat_adjustments or item.id in (191535, 191536, 191537, 191253):
                            continue
                        item_stat_adjustment = reagent_quality_stat_adjustments.get(item__id=item.id) 
                        reagent_effect_pct = item_stat_adjustment.reagent_effect_percent
                        for effect in reagent_effects:
                            amount = effect.profession_effect.amount
                            amount_x_reagent_effect_pct = reagent_effect_pct * (amount / 100)
                            effect_name = effect.profession_effect.profession_effect_type.name
                            item_json[effect_name] = amount_x_reagent_effect_pct

        product_set = recipe.product_set.all()
        product_tiers = []
        for product in product_set:
            
            if product.quantity > 1:
                multicraftable = True
            else:
                multicraftable = False

            print(f"product {product.item.type.id}")
            if product.item.type.id in [0, 2, 4, 7, 8]:
                inspirable = True
            else:
                inspirable = False

            item = product.item
            if product.item.quality:
                quality = item.quality.quality_tier
            else:
                quality = None
            tier = {
                "buyout": 0,
                "item_id": item.id,
                "num": quality
            }
            product_tiers.append(tier)

        # Small
        # TODO remove (DNT) from names
        # order tiers as 1, 2, 3 
        # select widgets with optgroups in optional material
            # needs names in empower with training matrix instead of numbers
            # empower also needs a better optgroup name
            # empower also isn't a great label since the items that fit in that slot are not all called training matrixes
            # lesser illusterious insight needs no select as their is no qualities to choose
            # everything number wise needs to be displayed as 1, 2, 3
        # products tier when inspired is useless right now
        # all stats in the html is useless
        # products like weapons and armor have one item id and are distinguished by bonus and modifier ids
            # wowhead seems to have the bonus ids in the querystring and a good way to select them now
            # how should this be displayed? Something to think about when adding live auction prices

        context = {
            "name" : recipe.name,
            "recipe_skill" : 0,
            "user_skill" : 0,
            "inspiration" : 0,
            "skill_from_inspiration" : 0,
            "resourcefulness" : 0,
            "multicraft" : 0,
            "mats" : formatted_materials,
            "optional_mat_slots" : formatted_optional_mat_slots,
            "product" : {
                "quantity" : product.quantity,
                "multicraftable": multicraftable, 
                "inspirable": inspirable,
                "name": product_set[0].item.name, # kinda reduntant with recipe name
                "tiers": product_tiers
            },
        }
        super_context.update(context)
        return super_context
    

#TODO Needs milling and prospecting, prices of legos, prices for untradable mats, 
# intermediate prices like showing milling, ink, pigment, 
# profits for making decks so you can choose the best, 
# better prices like average minbuyout or 1st quartile of all servers in the region, 
# showing all available auctions somewhere, a link to the change realm and server page, 
# a searchbar, home button, nice looking header and footer, prettier design, 
# displaying information on index pages like what the profit is on the recipes 
# index page next to the detail recipe link, reorder profession tiers so latest 
# expansion is at the top, add wow tooltips from wowhead, add ilvl and faction 
# (if applicaple) to the recipe index view, link to undermine journal page for 
# historical data, link to wowhead for the items (through the tooltip), 
# add support for recieps with multiple products, add support for procs, 
# add vendor purchase and sell prices to items, make calculator use min of 
# vendor buy and auction prices,

class TalentTreeView(TemplateView):
    # TODO move tree creation to a TraitTree model method, jot down somewhere to do the same with the rest of the views
    context = {
        "potion_mastery" : {
            "trait_path" : {
                "children_nodes" : [
                    {
                        "name" : "test name 1",
                        "children_nodes" : [], # has no children
                        "perk_nodes" : [
                            {
                                "name" : "test_perk_name_1",
                                "max_ranks" : 1,
                                "effect" : {
                                    "type" : "test_stat",
                                    "amount" : 30
                                    }
                            }
                        ]
                    },
                    {
                        "name" : "test name 2",
                        "children_nodes" : [
                            {
                                "name" : "test name 3",
                                "children_nodes" : [] # bottom most part of tree
                            }
                        ]
                    }
                ],
                "perk_nodes" : [
                    {},
                    {}
                ]
            }
        }
    }