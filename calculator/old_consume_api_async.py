

    # TODO Model was deleted. Probably useless?
    # def insert_crafting_qualities(self):
    #     qualities = []
    #     with open(r"calculator\wow_csv_data\CraftingQuality.csv", encoding='utf-8-sig') as file:
    #         quality_csv = csv.reader(file)
    #         next(quality_csv)
    #         for crafting_quality in quality_csv:
    #             quality_id = int(crafting_quality[0])
    #             quality = int(crafting_quality[1])
    #             qualities.append(models.CraftingQuality(id=quality_id, quality=quality))
    #     models.CraftingQuality.objects.bulk_create(qualities)


    # TODO This is a single time insert and probably useless. Delete after making hourly update version?
    # def insert_auctions(self, connected_realm_id: int):
    #     """Inserts all auctions from a connected realm into the db."""
    #     json = async_to_sync(self.wowapi.get_auctions)(connected_realm_id)
    #     all_items = models.Item.objects.all()
    #     all_bonuses = models.ItemBonus.objects.all()
    #     all_bonus_lists = models.BonusList.objects.all()
    #     all_modifier_keys = models.ModifierKey.objects.all()
    #     all_modifier_values = models.ModifierValue.objects.all()
    #     all_modifier_pairs = models.ModifierPair.objects.all()
    #     region = models.Region.objects.get(region=self.wowapi.region)
    #     connected_realm_obj = models.ConnectedRealmsIndex.objects.get(
    #         connected_realm_id=connected_realm_id
    #     )
    #     auctions = []  

    #     for auction in json["auctions"]:
    #         item = all_items.get(id = auction["item"]["id"])

    #         if auction["item"].get("bonus_lists"):
    #             json_bonus_list = auction["item"]["bonus_lists"]
    #             bonus_objects = []

    #             for index in range(10):
    #                 try:
    #                     bonus = json_bonus_list[index]
    #                     bonus_object, _ = all_bonuses.get_or_create(id=bonus)
    #                 except IndexError as e:
    #                     bonus_object = None
    #                 bonus_objects.append(bonus_object)
    
    #             bonus_list_object, _ = all_bonus_lists.get_or_create(
    #                 bonus_1=bonus_objects[0],
    #                 bonus_2=bonus_objects[1],
    #                 bonus_3=bonus_objects[2],
    #                 bonus_4=bonus_objects[3],
    #                 bonus_5=bonus_objects[4],
    #                 bonus_6=bonus_objects[5],
    #                 bonus_7=bonus_objects[6],
    #                 bonus_8=bonus_objects[7],
    #                 bonus_9=bonus_objects[8],
    #                 bonus_10=bonus_objects[9],
    #             )
    #         else:
    #             bonus_list_object = None
    #         if auction["item"].get("modifiers"):
    #             json_modifier_list = auction["item"].get("modifiers")
                
    #             pairs = []
    #             for index in range(10):
    #                 try:
    #                     modifier = json_modifier_list[index]
    #                     key_id = modifier["type"]
    #                     value_id = modifier["value"]
    #                     key, _ = all_modifier_keys.get_or_create(id=key_id)
    #                     value, _ = all_modifier_values.get_or_create(id=value_id)
    #                     pair, _ = all_modifier_pairs.get_or_create(key=key, value=value)
    #                 except IndexError as e:
    #                     pair = None
    #                 pairs.append(pair)
                
    #             modifier_list_object, _ = models.ModifierList.objects.get_or_create(
    #                 modifier_1=pairs[0],
    #                 modifier_2=pairs[1],
    #                 modifier_3=pairs[2],
    #                 modifier_4=pairs[3],
    #                 modifier_5=pairs[4],
    #                 modifier_6=pairs[5],
    #                 modifier_7=pairs[6],
    #                 modifier_8=pairs[7],
    #                 modifier_9=pairs[8],
    #                 modifier_10=pairs[9],
    #             )
    #         else:
    #             modifier_list_object = None
    #         if auction.get("buyout") != None: # skip all bid only auctions
    #             auction_obj = models.Auction(
    #                 auction_id=auction.get("id"),
    #                 buyout=auction.get("buyout"),
    #                 quantity=auction.get("quantity"),
    #                 time_left=auction.get("time_left"),
    #                 connected_realm=connected_realm_obj,
    #                 region=region,
    #                 item=item,
    #                 bonus_list=bonus_list_object,
    #                 modifier_list=modifier_list_object,
    #                 pet_level=auction.get("item").get("pet_level"),
    #             )
    #             auctions.append(auction_obj)
    #     models.Auction.objects.bulk_create(auctions, ignore_conflicts=True)

    # TODO This is a single time insert and probably useless. Delete after making hourly update version?
    # def insert_commodities(self):
    #     all_items = models.Item.objects.all()
    #     region = models.Region.objects.get(region=self.wowapi.region)
    #     json = async_to_sync(self.wowapi.get_commodities)()
    #     auctions = []
    #     for commodity in json["auctions"]:
    #         item_id = commodity["item"]["id"]
    #         item = all_items.get(id = item_id)

    #         auction_obj = models.Auction(
    #             auction_id=commodity["id"],
    #             buyout=commodity["unit_price"],
    #             quantity=commodity["quantity"],
    #             time_left=commodity["time_left"],
    #             item=item,
    #             region=region,
    #             connected_realm=None,
    #             bonus_list=None,
    #             modifier_list=None,
    #             pet_level=None,
    #         )
    #         auctions.append(auction_obj)
    #     models.Auction.objects.bulk_create(auctions)



#     def insert_profession_tier(self, profession_id: int):
#         """Inserts all profession tiers for a profession into the db."""
#         json = async_to_sync(self.get_profession_tiers)(profession_id)
#         profession_obj = models.ProfessionIndex.objects.get(id=profession_id)
#         if json.get("skill_tiers"):
#             for tier in json["skill_tiers"]:
#                 name = tier["name"]
#                 id = tier["id"]
#                 record = models.ProfessionTier(
#                     id=id, name=name, profession=profession_obj
#                 )
#                 record.save()

#     def insert_recipe_category(
#         self, profession_id: int, profession_tier_id: int
#     ) -> None:
#         """Inserts data from recipe category into that model and the name and id into the recipe model.

#         Args:
#             ragion_api (WowApi): A WowApi object.
#             profession_id (int): A professions id. Get from profession index.
#             profession_tier_id (int): A profession tier's id. Get from profession tiers.
#         """
#         json = async_to_sync(self.get_profession_tier_categories)(
#             profession_id, profession_tier_id
#         )
#         profession_tier_obj = models.ProfessionTier.objects.get(id=profession_tier_id)

#         recipes = []

#         if json.get("categories"):
#             for category in json["categories"]:
#                 category_name = category.get("name")
#                 category_record, created = models.RecipeCategory.objects.get_or_create(
#                     name=category_name,
#                     profession_tier=profession_tier_obj,
#                 )
#                 if created:
#                     category_record.save()
#                 for recipe in category.get("recipes"):
#                     recipe_name = recipe.get("name")
#                     recipe_id = recipe.get("id")
#                     recipe_record = models.Recipe(
#                         id=recipe_id,
#                         name=recipe_name,
#                         recipe_category=category_record,
#                     )
#                     recipes.append(recipe_record)
#         else:
#             category_name = json["name"]
#             category_record, created = models.RecipeCategory.objects.get_or_create(
#                 name=category_name,
#                 profession_tier=profession_tier_obj,
#             )
#             if created:
#                 category_record.save()

#         models.Recipe.objects.bulk_create(recipes, ignore_conflicts=True)

#     def insert_recipe(self, recipe_id: int):
#         """Inserts a recipe along with its items, products, and materials into the db."""
#         json = async_to_sync(self.get_recipe)(recipe_id)
#         # recipe id, recipe name, product foreignKey, material(s), material quantity
#         recipe_id = json["id"]
#         recipe_name = json["name"]

#         if json.get("crafted_quantity"):
#             if json.get("crafted_quantity").get("value"):
#                 product_quantity = (json.get("crafted_quantity")["value"],)
#             else:
#                 min_quantity = json.get("crafted_quantity")["minimum"]
#                 max_quantity = json.get("crafted_quantity")["maximum"]
#                 product_quantity = (min_quantity, max_quantity)
#         else:
#             product_quantity = (0,)
#         product_list = []
#         if json.get("crafted_item"):
#             product_id = json.get("crafted_item")["id"]
#             product_name = json.get("crafted_item")["name"]
#             product_item_obj, created = models.Item.objects.get_or_create(
#                 id=product_id, name=product_name
#             )
#             product_list.append(product_item_obj)
#         if json.get("alliance_crafted_item"):
#             alliance_product_id = json.get("alliance_crafted_item")["id"]
#             alliance_product_name = json.get("alliance_crafted_item")["name"]
#             alliance_product_item_obj, created = models.Item.objects.get_or_create(
#                 id=alliance_product_id, name=alliance_product_name
#             )
#             product_list.append(alliance_product_item_obj)
#         if json.get("horde_crafted_item"):
#             horde_product_id = json.get("horde_crafted_item")["id"]
#             horde_product_name = json.get("horde_crafted_item")["name"]
#             horde_product_item_obj, created = models.Item.objects.get_or_create(
#                 id=horde_product_id, name=horde_product_name
#             )
#             product_list.append(horde_product_item_obj)
#         recipe = models.Recipe.objects.get(id=recipe_id)
#         materials_list = []
#         if json.get("reagents"):
#             for mat in json.get("reagents"):
#                 mat_id = mat["reagent"]["id"]
#                 mat_name = mat["reagent"]["name"]
#                 mat_item_obj, created = models.Item.objects.get_or_create(
#                     id=mat_id, name=mat_name
#                 )
#                 mat_item_quantity = mat.get("quantity")
#                 mat_obj, created = models.Material.objects.get_or_create(
#                     item=mat_item_obj, quantity=mat_item_quantity, recipe=recipe
#                 )
#                 materials_list.append(mat_obj)

#         for product_item_obj in product_list:
#             if product_item_obj:  # obj or None
#                 if len(product_quantity) == 1:
#                     min_quantity = product_quantity[0]
#                     max_quantity = product_quantity[0]
#                 else:
#                     min_quantity = product_quantity[0]
#                     max_quantity = product_quantity[1]
#                 product_record = models.Product(
#                     recipe=recipe,
#                     item=product_item_obj,
#                     min_quantity=min_quantity,
#                     max_quantity=max_quantity,
#                 )
#                 product_record.save()

#     # TODO
#     def insert_item(self):
#         """Inserts an item into the db."""
#         pass

#     def insert_all_items(self):
#         """Inserts all items into the db."""
#         print("inserting items")
#         json = async_to_sync(self.get_all_items)()
#         items = []
#         for item in json["items"]:
#             id = item["id"]
#             vendor_buy_price = item["purchase_price"]
#             vendor_sell_price = item["sell_price"]
#             vendor_buy_quantity = item["purchase_quantity"]
#             quality = item["quality"]["type"]
#             name = item["name"]
#             if item.get("binding"):
#                 binding = item["binding"]["type"]
#             else:
#                 binding = None
#             item_record = models.Item(
#                 id=id,
#                 vendor_buy_price=vendor_buy_price,
#                 vendor_sell_price=vendor_sell_price,
#                 vendor_buy_quantity=vendor_buy_quantity,
#                 quality=quality,
#                 name=name,
#                 binding=binding,
#             )
#             items.append(item_record)

#         models.Item.objects.bulk_create(items, ignore_conflicts=True)

#     def insert_regional_data(self):
#         """Inserts data specific to a region, except for auctions, into the db."""
#         if not models.Region.objects.all():
#             print("Inserting regions...")
#             start_region = time.monotonic()
#             self.insert_regions()
#             end_region = time.monotonic()
#             elapsed_region = end_region - start_region
#             print(f"Finished inserting regions: {elapsed_region}")

#         print("Inserting connected realms index...")
#         start_conn = time.monotonic()
#         self.insert_connected_realms_index()
#         end_conn = time.monotonic()
#         elapsed_conn = end_conn - start_conn
#         print(f"Finished inserting connected realms: {elapsed_conn}")

#         print("inserting all realms...")
#         start_realms = time.monotonic()
#         self.insert_all_realms()
#         end_realms = time.monotonic()
#         elapsed_realms = end_realms - start_realms
#         print(f"Finished inserting realms: {elapsed_realms}")
#         print("finished inserting regional data")

#     def insert_profession_data(self):
#         """Inserts all profession data.

#         Items should be inserted before calling this method.
#         """
#         prof_tree = async_to_sync(self.get_all_profession_data)()
#         inserted_professions = self._insert_profession_index(prof_tree)
#         inserted_skill_tiers = self._insert_skill_tiers(prof_tree, inserted_professions)
#         inserted_categories = self._insert_skill_tier_categories(
#             prof_tree, inserted_skill_tiers
#         )
#         self._insert_all_recipes(prof_tree, inserted_categories)

#     def _insert_profession_index(self, profession_tree: list) -> list:
#         profession_records = []
#         for profession in profession_tree:
#             id = profession["id"]
#             name = profession["name"]
#             record = models.ProfessionIndex(name=name, id=id)
#             profession_records.append(record)
#         inserted_professions = models.ProfessionIndex.objects.bulk_create(
#             profession_records, ignore_conflicts=True
#         )
#         return inserted_professions

#     def _insert_skill_tiers(
#         self, profession_tree: list, profession_objects: list
#     ) -> list:
#         skill_tier_records = []
#         for index, profession in enumerate(profession_tree):
#             for skill_tier in profession["skill_tiers"]:
#                 name = skill_tier["name"]
#                 id = skill_tier["id"]
#                 record = models.ProfessionTier(
#                     id=id, name=name, profession=profession_objects[index]
#                 )
#                 skill_tier_records.append(record)
#         inserted_skill_tiers = models.ProfessionTier.objects.bulk_create(
#             skill_tier_records, ignore_conflicts=True
#         )
#         return inserted_skill_tiers

#     def _insert_skill_tier_categories(
#         self, profession_tree: list, skill_tier_objects: list
#     ) -> list:
#         category_records = []
#         for profession in profession_tree:
#             for tier_index, skill_tier in enumerate(profession["skill_tiers"]):
#                 for category in skill_tier["categories"]:
#                     name = category["name"]
#                     record = models.RecipeCategory(
#                         name=name, profession_tier=skill_tier_objects[tier_index]
#                     )
#                     category_records.append(record)
#         models.RecipeCategory.objects.bulk_create(
#             category_records, ignore_conflicts=True
#         )
#         inserted_categories = list(models.RecipeCategory.objects.all().order_by("id"))
#         return inserted_categories

#     def _insert_all_recipes(self, profession_tree: list, category_objects: list):
#         mat_records = []
#         product_records = []
#         recipe_records = []
#         category_count = 0
#         for profession in profession_tree:
#             for skill_tier in profession["skill_tiers"]:
#                 for category in skill_tier["categories"]:
#                     for recipe in category["recipes"]:
#                         id = recipe["id"]
#                         name = recipe["name"]
#                         recipe_category = category_objects[category_count]

#                         record = models.Recipe(
#                             id=id, name=name, recipe_category=recipe_category
#                         )
#                         recipe_records.append(record)

#                         product = models.Product(recipe=record)
#                         if recipe.get("crafted_quantity"):
#                             if recipe.get("crafted_quantity").get("value"):
#                                 min_and_max_quantity = recipe["crafted_quantity"][
#                                     "value"
#                                 ]
#                                 min_quantity = min_and_max_quantity
#                                 max_quantity = min_and_max_quantity
#                             else:
#                                 min_quantity = recipe["crafted_quantity"]["minimum"]
#                                 max_quantity = recipe["crafted_quantity"]["maximum"]
#                         else:
#                             max_quantity = 0
#                             min_quantity = 0

#                         if recipe.get("crafted_item"):
#                             product_id = recipe["crafted_item"]["id"]
#                             product_name = recipe["crafted_item"]["name"]
#                             product_item_obj, _ = models.Item.objects.get_or_create(
#                                 id=product_id, name=product_name
#                             )
#                             product = models.Product(
#                                 recipe=record,
#                                 item=product_item_obj,
#                                 min_quantity=min_quantity,
#                                 max_quantity=max_quantity,
#                             )
#                             product_records.append(product)

#                         if recipe.get("alliance_crafted_item"):
#                             alliance_product_id = recipe["alliance_crafted_item"]["id"]
#                             alliance_product_name = recipe["alliance_crafted_item"][
#                                 "name"
#                             ]
#                             (
#                                 alliance_product_item_obj,
#                                 _,
#                             ) = models.Item.objects.get_or_create(
#                                 id=alliance_product_id, name=alliance_product_name
#                             )
#                             product = models.Product(
#                                 recipe=record,
#                                 item=alliance_product_item_obj,
#                                 min_quantity=min_quantity,
#                                 max_quantity=max_quantity,
#                             )
#                             product_records.append(product)

#                         if recipe.get("horde_crafted_item"):
#                             horde_product_id = recipe["horde_crafted_item"]["id"]
#                             horde_product_name = recipe["horde_crafted_item"]["name"]
#                             (
#                                 horde_product_item_obj,
#                                 _,
#                             ) = models.Item.objects.get_or_create(
#                                 id=horde_product_id, name=horde_product_name
#                             )
#                             product = models.Product(
#                                 recipe=record,
#                                 item=horde_product_item_obj,
#                                 min_quantity=min_quantity,
#                                 max_quantity=max_quantity,
#                             )
#                             product_records.append(product)

#                         if recipe.get("reagents"):
#                             for mat in recipe["reagents"]:
#                                 mat_item_quantity = mat["quantity"]
#                                 mat_id = mat["reagent"]["id"]
#                                 mat_name = mat["reagent"]["name"]
#                                 mat_item_obj, _ = models.Item.objects.get_or_create(
#                                     id=mat_id, name=mat_name
#                                 )
#                                 mat_obj = models.Material(
#                                     item=mat_item_obj,
#                                     recipe=record,
#                                     quantity=mat_item_quantity,
#                                 )
#                                 mat_records.append(mat_obj)
#                     category_count += 1
#         inserted_recipes = models.Recipe.objects.bulk_create(
#             recipe_records, ignore_conflicts=True
#         )
#         inserted_products = models.Product.objects.bulk_create(
#             product_records, ignore_conflicts=True
#         )
#         inserted_mats = models.Material.objects.bulk_create(
#             mat_records, ignore_conflicts=True
#         )

#     def insert_static_data(self):
#         print("Inserting all items...")
#         start_item = time.monotonic()
#         self.insert_all_items()
#         end_item = time.monotonic()
#         elapsed_item = end_item - start_item
#         print(f"Finished inserting items: {elapsed_item}")
#         print("Inserting all profession data...")
#         start_prof = time.monotonic()
#         self.insert_profession_data()
#         end_prof = time.monotonic()
#         elapsed_prof = end_prof - start_prof
#         print(f"Finished inserting profession data: {elapsed_prof}")


# def calculate_market_price(item_id: int):
#     """Calculates the market price of an item.

#     Args:
#         item_id (int): The id of an item.
#     """
#     # excludes records with no buyout
#     auctions_with_buyout = models.Auction.objects.filter(item_id=item_id).exclude(
#         buyout=None
#     )
#     # excludes records with no unit_price
#     auctions_with_unit_price = models.Auction.objects.filter(item_id=item_id).exclude(
#         unit_price=None
#     )

#     if auctions_with_buyout.count() != 0:
#         quantity_sum = auctions_with_buyout.aggregate(Sum("quantity"))["quantity__sum"]
#         ordered_buyouts = auctions_with_buyout.values_list(
#             "buyout", flat=True
#         ).order_by("buyout")
#         bottom_10percent = round(quantity_sum * 0.1)
#         market_price = ordered_buyouts.filter(
#             buyout__lt=ordered_buyouts[bottom_10percent]
#         ).aggregate(Avg("buyout"))
#         return market_price
#     elif auctions_with_unit_price.count() != 0:
#         quantity_sum = auctions_with_unit_price.aggregate(Sum("quantity"))[
#             "quantity__sum"
#         ]
#         ordered_buyouts = auctions_with_unit_price.values_list(
#             "unit_price", flat=True
#         ).order_by("unit_price")
#         bottom_10percent = round(quantity_sum * 0.1)
#         market_price = ordered_buyouts.filter(
#             unit_price__lt=ordered_buyouts[bottom_10percent]
#         ).aggregate(Avg("unit_price"))
#         return market_price


# def calculate_avg_region_market_price(item_id: int, connected_realm_id: int):
#     """Calcluate the avg of an items market price in a region.

#     Args:
#         item_id (int): The id of an item.
#         connected_realm_id (int): The id of a connected realm.
#     """
#     pass


# def calculate_median_region_market_price(item_id: int, connected_realm_id: int):
#     """Calcluate the median of an items market price in a region.

#     Args:
#         item_id (int): The id of an item.
#         connected_realm_id (int): The id of a connected realm.
#     """
#     pass


# def calculate_recipe_profit(recipe_id: int, connected_realm_id: int):
#     """Calcluate the profit from a recipe.

#     Args:
#         item_id (int): The id of an item.
#         connected_realm_id (int): The id of a connected realm.
#     """
#     pass


# def calculate_region_recipe_profit(recipe_id: int):
#     """Calcluate the profit from a recipe.

#     Args:
#         item_id (int): The id of an item.
#     """
#     pass


# # TODO
# # New models have to be inserted
# # How will RecipeProfit, PriceData, and the new item fields be inserted?
# # Profits will have to be calculated each hour too.
# # There are a couple thousand recipes per server and dozens of connected realms to calculate for.
# # Thats a lot of dynos calculating and inserting auctions each hour.


# async def main():
#     us_api = await Insert.create("us")
#     kr_api = await Insert.create("kr")
#     eu_api = await Insert.create("eu")
#     regions = [us_api, kr_api, eu_api]

# if __name__ == "__main__":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#     asyncio.run(main())
