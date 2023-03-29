from django.db import models



class Region(models.Model):
    """Server regions such as North America, Europe, Korea."""
    region = models.CharField(
        max_length=30, help_text="North America, Europe, ...", primary_key=True
    )

class ConnectedRealmsIndex(models.Model):
    """An index of all connected realm ids.

    Attribute:
        connected_realm_id (IntegerField): The connected realm id.
    """
    connected_realm_id = models.IntegerField(help_text="Id for the connected realms", primary_key=True,db_index=True)

class Realm(models.Model):
    realm_id = models.IntegerField(
        help_text="Realm specific id", primary_key=True
    )
    connected_realm = models.ForeignKey(
        "ConnectedRealmsIndex", on_delete=models.CASCADE
    )
    population = models.CharField(
        max_length=20, help_text="Low, Medium, High, Full"
    )
    name = models.CharField(max_length=30, help_text="Ex: Illidan, Stormrage, ...")
    region = models.ForeignKey("Region", on_delete=models.CASCADE)
    timezone = models.CharField(max_length=40)
    play_style = models.CharField(max_length=7, help_text="Normal, RP")

    def __str__(self):
        return self.name

class Auction(models.Model):
    """The model for all auctions from all servers.

    Attributes:
        auction_id (IntegerField): An auction's primary key.
        buyout (IntegerField): The buyout price of an auction. Can be null.
            Value is in g*sscc format.
        bid (IntegerField): The bid price of an auction. Can be null.
            Value is in g*sscc format.
        unit_price (IntegerField): The unit price of an auction. Can be null.
            Value is in g*sscc format.
        quantity (IntegerField): The number of items posted in an auction.
        timestamp (DateField): The timestamp of when the auction was added to the db.
        connected_realm (ForeginKey): The connected realm id that this auction comes from.
        item (ForeginKey): The item being auctioned.
        pet_level (IntegerField): The level of the pet being sold, if applicable. 
    """
    auction_id = models.BigIntegerField(primary_key=True)
    buyout = models.BigIntegerField()
    quantity = models.IntegerField()
    time_left = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    connected_realm = models.ForeignKey(
        "ConnectedRealmsIndex", on_delete=models.CASCADE,
        blank=True, null=True
    )
    region = models.ForeignKey("Region", on_delete=models.CASCADE)
    item = models.ForeignKey("item", on_delete=models.CASCADE)
    bonus_list = models.ForeignKey("BonusList", on_delete=models.CASCADE, blank=True, null=True)
    modifier_list = models.ForeignKey("ModifierList", on_delete=models.CASCADE, blank=True, null=True)
    pet_level = models.IntegerField(blank=True, null=True)

    class Meta:
        models.UniqueConstraint(fields = ['auction_id', 'timestamp'], name = 'unique_auction_id_and_time')

    def get_market_price():
        pass

    def get_total_quantity():
        pass

# 1. Get or create ItemBonus object with each individual bonus
# 2. Make an instance of BonusList with no attributes
# 3. Set each ItemBonus to an attribute of BonusList
# 4. Check if that BonusList already exists.
# 5. 
    # a. If it exists get it from db and attach to the auction record
    # b. Else save a new BonusList and attach that to the auction record
# 6. Append auction record to auctions and bulk_create at the end.
# Auction.objects.get_or_create(bonus_list_)
class BonusList(models.Model):
    bonus_1 = models.ForeignKey("ItemBonus", related_name="bonus_1_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_2 = models.ForeignKey("ItemBonus", related_name="bonus_2_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_3 = models.ForeignKey("ItemBonus", related_name="bonus_3_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_4 = models.ForeignKey("ItemBonus", related_name="bonus_4_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_5 = models.ForeignKey("ItemBonus", related_name="bonus_5_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_6 = models.ForeignKey("ItemBonus", related_name="bonus_6_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_7 = models.ForeignKey("ItemBonus", related_name="bonus_7_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_8 = models.ForeignKey("ItemBonus", related_name="bonus_8_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_9 = models.ForeignKey("ItemBonus", related_name="bonus_9_set", on_delete=models.CASCADE, blank=True, null=True)
    bonus_10 = models.ForeignKey("ItemBonus", related_name="bonus_10_set", on_delete=models.CASCADE, blank=True, null=True)


class ItemBonus(models.Model):
    """The model of all item bonuses."""
    id = models.IntegerField(primary_key=True, db_index=True)
    effect = models.TextField(blank=True, null=True)
    value_0 = models.IntegerField(blank=True, null=True)
    value_1 = models.IntegerField(blank=True, null=True)
    value_2 = models.IntegerField(blank=True, null=True)

class ModifierList(models.Model):
    modifier_1 = models.ForeignKey("ModifierPair", related_name="modifier_1_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_2 = models.ForeignKey("ModifierPair", related_name="modifier_2_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_3 = models.ForeignKey("ModifierPair", related_name="modifier_3_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_4 = models.ForeignKey("ModifierPair", related_name="modifier_4_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_5 = models.ForeignKey("ModifierPair", related_name="modifier_5_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_6 = models.ForeignKey("ModifierPair", related_name="modifier_6_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_7 = models.ForeignKey("ModifierPair", related_name="modifier_7_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_8 = models.ForeignKey("ModifierPair", related_name="modifier_8_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_9 = models.ForeignKey("ModifierPair", related_name="modifier_9_set", on_delete=models.CASCADE, blank=True, null=True)
    modifier_10 = models.ForeignKey("ModifierPair", related_name="modifier_10_set", on_delete=models.CASCADE, blank=True, null=True)

class ModifierPair(models.Model):
    key = models.ForeignKey("ModifierKey", on_delete=models.CASCADE, blank=True, null=True)
    value = models.ForeignKey("ModifierValue", on_delete=models.CASCADE, blank=True, null=True)

class ModifierKey(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    effect = models.TextField(blank=True, null=True)

class ModifierValue(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    effect = models.TextField(blank=True, null=True)


class ProfessionIndex(models.Model):
    """The model for all professions.

    The Auto incrementing primary key doesn't resert to zero if
    records are deleted from the db.

    Attributes:
        id (IntegerField): The id of the profession. Primary Key.
        name (CharField): The name of the profession. Max_length = 50.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class RecipeCategory(models.Model):
    """The model for recipe catagories. Ex: consumables

    Attributes:
        name (CharField): The category name. Max length = 100.
        profession (ForeginKey): The profession the category belongs to.
    """

    name = models.CharField(max_length=100)
    profession = models.ForeignKey("ProfessionIndex", on_delete=models.CASCADE)

class Recipe(models.Model):
    """The model for all recipes.

    Attributes:
        id (IntegerField): The id for a recipe. Primary Key.
        name (CharField): The name for a recipe. Max length = 100.
        recipeCategory (ForeginKey): The category the recipe belongs to.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    recipe_category = models.ForeignKey("RecipeCategory", on_delete=models.CASCADE, blank=True, null=True)
    spell = models.ForeignKey("Spell", on_delete=models.CASCADE)
    crafting_data = models.ForeignKey("CraftingData", on_delete=models.CASCADE, blank=True, null=True)

class Product(models.Model): # recipes can produce different quality versions of the same item
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.FloatField()
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)

class Material(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(blank=True, null=True)
    recraft_quantity = models.IntegerField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    optional_material_slot = models.ForeignKey("OptionalMaterialSlot", on_delete=models.CASCADE, blank=True, null=True)
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)

class OptionalMaterialSlot(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)


class Item(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    quality = models.ForeignKey("CraftingQuality", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    binding = models.CharField(max_length=50, blank=True, null=True)
    MCR_item = models.ForeignKey("ModifiedCraftingReagentItem", on_delete=models.CASCADE, blank=True, null=True)

    def get_market_price(self):
        pass

class CraftingStats(models.Model):
    item = models.OneToOneField("Item", on_delete=models.CASCADE)
    resourcefulness = models.IntegerField(blank=True, null=True)
    increase_material_from_resourcefulness = models.FloatField(blank=True, null=True)
    inspiration = models.IntegerField(blank=True, null=True)
    skill_from_inspiration = models.FloatField(blank=True, null=True)
    multicraft = models.IntegerField(blank=True, null=True)
    skill = models.IntegerField(blank=True, null=True)
    crafting_speed = models.FloatField(blank=True, null=True)


class Spell(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)


class CraftingQuality(models.Model):
    id = models.IntegerField(primary_key=True)
    quality_tier = models.IntegerField()


class CraftingData(models.Model):
    id = models.IntegerField(primary_key=True)


class ModifiedCraftingReagentSlot(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    modified_crafting_category = models.ManyToManyField("ModifiedCraftingCategory")


class ModifiedCraftingCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)


class ModifiedCraftingReagentItem(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    modified_crafting_category = models.ForeignKey("ModifiedCraftingCategory", on_delete=models.CASCADE, blank=True, null=True)
