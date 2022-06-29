"""All models used in the crafting calculator."""
from django.db import models


class Realm(models.Model):
    """Model for WoW realm data.

    Attributes:
        population_choices (list): The possible popluation sizes.
            Each element is a (key, value) tuple.
        region_choices (list): The possible realm regions like ('NA', 'North America').
            Eacg element is a (key, value) tuple.
        connected_realm (ForeginKey): This realms connected realm id. Refrences
            the connected realm index.
        population (CharField): The amount of players on the realm. One of
            population_choices. Max length = 20.
        realm_id (DecimalField): The specific id for that realm. Not connected id.
            Max digits = 4. Primary Key.
        name (CharField): Realm's name. Max length = 30.
        region (CharField): The region the realm is in. Ex: North America.
            Max length = 30.
        timezone (CharField): Realms timezone. Ex: America/New_York Max length = 40.
        play_style (CharField): Is the realm NORMAL, RP. Max length = 20.
    """

    population_choices = [
        ("Low", "Low"),
        ("Med", "Medium"),
        ("High", "High"),
        ("Full", "Full"),
    ]

    connected_realm = models.ForeignKey(
        "connectedRealmsIndex", on_delete=models.CASCADE
    )
    population = models.CharField(
        max_length=20, help_text="Low, Medium, High, Full", choices=population_choices
    )
    realm_id = models.DecimalField(
        max_digits=4, decimal_places=0, help_text="Realm specific id", primary_key=True
    )
    name = models.CharField(max_length=30, help_text="Ex: Illidan, Stormrage, ...")
    region = models.CharField(
        max_length=30, help_text="North America, Europe, ..."
    )
    timezone = models.CharField(max_length=40)
    play_style = models.CharField(max_length=7, help_text="Normal, RP")

    def __str__(self):
        return self.name


class ConnectedRealmsIndex(models.Model):
    """An index of all connected realm ids.

    Attribute:
        connected_realm_id (IntegerField): The connected realm id.
    """
    connected_realm_id = models.IntegerField(help_text="Id for the connected realms", primary_key=True)

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
        item_bonus_list (ManyToManyField): The bonus list of the auctioned item.
            Can be null.
        item_modifier_list (ManyToManyField): The modifier list of the auctioned item.
    """
    auction_id = models.BigIntegerField(primary_key=True)
    buyout = models.BigIntegerField(blank=True, null=True)
    bid = models.BigIntegerField(blank=True, null=True)
    unit_price = models.BigIntegerField(blank=True, null=True)
    quantity = models.IntegerField()
    time_left = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    connected_realm = models.ForeignKey(
        "ConnectedRealmsIndex", on_delete=models.CASCADE
    )
    item = models.ForeignKey("item", on_delete=models.CASCADE)
    pet_level = models.IntegerField(blank=True, null=True)

    class Meta:
        models.UniqueConstraint(fields = ['auction_id', 'timestamp'], name = 'unique_auction_id_and_time')



class ItemBonus(models.Model):
    """The model of all item bonuses.

    Attributes:
        id (IntegerField): The item bonus id. Primary key.
        effect (CharField): The effect of the item bonus. Max length = 50.
    """
    id = models.IntegerField(primary_key=True)
    auctions = models.ManyToManyField("Auction", blank=True)

class ItemModifier(models.Model):
    """The model of all item modifiers.

        An item can have multiple modifiers with different types and values.

    Attributes:
        id (AutoField): An incrementing number. Primary key.
        type (IntegerField): Found in "type": int inside of auctions modifiers list.
        value (IntegerField): Found in "value": int inside of auctions modifiers list.
    """
    id = models.AutoField(primary_key=True)
    modifier_type = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    auctions = models.ManyToManyField("Auction", blank=True)

class ProfessionIndex(models.Model):
    """The model for all professions.

    Attributes:
        id (IntegerField): The id of the profession. Primary Key.
        name (CharField): The name of the profession. Max_length = 50.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class ProfessionTier(models.Model):
    """The model of all profession tiers. Ex: classic, shadowlands blacksmithing.

    Attributes:
        id (IntegerField): The tier's id. Primary Key.
        name (CharField): The tier's name. Max length = 50.
        profession (ForeginKey): The profession the tier belongs to.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    profession = models.ForeignKey("ProfessionIndex", on_delete=models.CASCADE)

    class Meta:
        ordering = ['profession', 'id']


class RecipeCategory(models.Model):
    """The model for recipe catagories. Ex: consumables

    Attributes:
        id (IntegerField): The category id. Primary Key.
        name (CharField): The category name. Max length = 50.
        profession_tier (ForeginKey): The tier the category belongs to.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    profession_tier = models.ForeignKey("ProfessionTier", on_delete=models.CASCADE)


class Recipe(models.Model):
    """The model for all recipes.

    Attributes:
        id (IntegerField): The id for a recipe. Primary Key.
        name (CharField): The name for a recipe. Max length = 100.
        product (ForeignKey): The item produced by a recipe.
        recipeCategory (ForeginKey): The category the recipe belongs to.
        mats (ManyToManyField): The materials required by the recipe.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    recipe_category = models.ForeignKey("RecipeCategory", on_delete=models.CASCADE)
    mats = models.ManyToManyField("Material")


class Material(models.Model):
    """The model for all materials for all recipes.

    Attributes:
        item (ForeginKey): The material.
        quantity(IntegerField): The amount of the material
    """
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Product(models.Model):
    """The model for all recipe products.
    
    Attributes:
        item (ForeginKey): The product.
        recipe (ForeignKey): The recipe the item comes from.
        quantity_min (IntegerField): The minimum amount of a product produced. 
        quantity_max (IntegerField): The maximum amount of an item produced.
    """
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    #A single recipe can have many products. Such as an alliance and horde version.
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    min_quantity = models.IntegerField()
    max_quantity = models.IntegerField()

class Item(models.Model):
    """The model for all items.

    Attributes:
        id (IntegerField): The unique id for a item. Primary Key.
        name (CharField): The name of an item. Max length = 100.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
