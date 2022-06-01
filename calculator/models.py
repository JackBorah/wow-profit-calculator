from django.db import models
from django.urls import reverse


class Realm(models.Model):
    """Model for WoW realm data.

    Attributes:
        population_choices (list): The possible popluation sizes.
            Each element is a (key, value) tuple.
        region_choices (list): The possible realm regions like ('NA', 'North America').
            Eacg element is a (key, value) tuple.
        realm_id (DecimalField): The specific id for that realm. Not connected id.
            Max digits = 4. Primary Key.
        name (CharField): Realm's name. Max length = 30.
        population (CharField): The amount of players on the realm. One of
            population_choices. Max length = 20.
        region (CharField): The region the realm is in. Ex: North America.
            Max length = 30.
        timezone (CharField): Realms timezone. Ex: America/New_York Max length = 40.
        type (CharField): Is the realm NORMAL, RP. Max length = 20.
        connected_realm_id (ForeginKey): This realms connected realm id. Refrences
            the connected realm index.
    """

    population_choices = [
        ("Low", "Low"),
        ("Med", "Medium"),
        ("High", "High"),
        ("Full", "Full"),
    ]

    #Useless?
    region_choices = [
        ("NA", "North America"),
        ("LA", "Latin America"),
        ("SA", "South America"),
        ("AU", "Australia"),
        ("NZ", "New Zealand"),
        ("EU", "European Union"),
        ("EE", "Eastern Europe"),
        ("RU", "Russia"),
        ("AF", "Africa"),
        ("ME", "Middle East"),
        ("SK", "South Korea"),
        ("TW", "Taiwan"),
        ("HK", "Hong Kong"),
        ("MU", "Macau"),
    ]

    realm_id = models.DecimalField(
        max_digits=4, decimal_places=0, help_text="Realm specific id", primary_key=True
    )
    name = models.CharField(max_length=30, help_text="Ex: Illidan, Stormrage, ...")
    population = models.CharField(
        max_length=20, help_text="Low, Medium, High, Full", choices=population_choices
    )
    region = models.CharField(
        max_length=30, help_text="North America, Europe, ...", choices=region_choices
    )
    timezone = models.CharField(max_length=40)
    type = models.CharField(max_length=7, help_text="Normal, RP")
    connected_realm_id = models.ForeignKey(
        "connectedRealmsIndex", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class ConnectedRealmsIndex(models.Model):
    """An index of all connected realm ids.

    Attribute:
        connected_realm_id (IntegerField): The connected realm id.
    """
    connected_realm_id = models.IntegerField(help_text="Id for the connected realms"
    )


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
        connected_realm_id (ForeginKey): The connected realm id that this auction comes from.
        item (ForeginKey): The item being auctioned.
        item_bonus_list (ManyToManyField): The bonus list of the auctioned item.
            Can be null.
    """
    auction_id = models.IntegerField(primary_key=True)
    buyout = models.IntegerField(blank=True, null=True)
    bid = models.IntegerField(blank=True, null=True)
    unit_price = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField()
    timestamp = models.DateField(auto_now_add=True)
    connected_realm_id = models.ForeignKey(
        "ConnectedRealmsIndex", on_delete=models.CASCADE
    )
    item = models.ForeignKey("item", on_delete=models.CASCADE)
    item_bonus_list = models.ManyToManyField("ItemBonus")


class ItemBonus(models.Model):
    """The model of all item bonuses.

    Attributes:
        id (IntegerField): The item bonus id. Primary key.
        effect (CharField): The effect of the item bonus. Max length = 50.
    """
    id = models.IntegerField(primary_key=True)
    effect = models.CharField(max_length=50)


class ProfessionIndex(models.Model):
    """The model for all professions.

    Attributes:
        id (IntegerField): The id of the profession. Primary Key.
        name (CharField): The name of the profession. Max_length = 50.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)


class ProfessionTeir(models.Model):
    """The model of all profession teirs. Ex: classic, shadowlands blacksmithing.

    Attributes:
        id (IntegerField): The teir's id. Primary Key.
        name (CharField): The teir's name. Max length = 50.
        profession (ForeginKey): The profession the teir belongs to.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    profession = models.ForeignKey("ProfessionIndex", on_delete=models.CASCADE)


class RecipeCatagory(models.Model):
    """The model for recipe catagories. Ex: consumables

    Attributes:
        id (IntegerField): The catagory id. Primary Key.
        name (CharField): The catagory name. Max length = 50.
        profession_teir (ForeginKey): The teir the catagory belongs to.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    profession_teir = models.ForeignKey("ProfessionTeir", on_delete=models.CASCADE)


class Recipe(models.Model):
    """The model for all recipes.

    Attributes:
        id (IntegerField): The id for a recipe. Primary Key.
        name (CharField): The name for a recipe. Max length = 100.
        product (ForeignKey): The item produced by a recipe.
        recipeCatagory (ForeginKey): The catagory the recipe belongs to.
        mats (ManyToManyField): The materials required by the recipe.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    product = models.ForeignKey("Item", on_delete=models.CASCADE)
    recipeCatagory = models.ForeignKey("RecipeCatagory", on_delete=models.CASCADE)
    mats = models.ManyToManyField("Material")


class Material(models.Model):
    """The model for all materials for all recipes.

    Attributes:
        item (ForeginKey): The material.
        quantity(IntegerField): The amount of the material
    """
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Item(models.Model):
    """The model for all items.

    Attributes:
        id (IntegerField): The unique id for a item. Primary Key.
        name (CharField): The name of an item. Max length = 100.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)