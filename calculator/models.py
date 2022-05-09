from decimal import Decimal
from tkinter import CASCADE
from django.db import models
from django.urls import reverse

# Acess tokens are needed for the blizzard api
class Realm(models.Model):

    population_choices = [
        ('Low', 'Low'),
        ('Med', 'Medium'),
        ('High', 'High'),
        ('Full', 'Full')
    ]

    region_choices = [
        ('NA', 'North America'),
        ('LA', 'Latin America'),
        ('SA', 'South America'),
        ('AU', 'Australia'),
        ('NZ', 'New Zealand'),
        ('EU', 'European Union'),
        ('EE', 'Eastern Europe'),
        ('RU', 'Russia'),
        ('AF', 'Africa'),
        ('ME', 'Middle East'),
        ('SK', 'South Korea'),
        ('TW', 'Taiwan'),
        ('HK', 'Hong Kong'),
        ('MU', 'Macau')
    ]

    realmId = models.DecimalField(max_digits=4, decimal_places=0, help_text="Realm specific id", primary_key=True)
    name = models.CharField(max_length=30, help_text="Ex: Illidan, Stormrage, ...")
    population = models.CharField(max_length=20, help_text="Low, Medium, High, Full", help_text="Low, Medium, High, Full", choices=population_choices)
    region = models.CharField(max_length=30, help_text="North America, Europe, ...", choices=region_choices)
    timezone = models.CharField(max_length=40)
    type = models.CharField(max_length=20, help_text="Normal, RP, PVP, PVPRP")
    connectedRealmId = models.ForeignKey('connectedRealm', on_delete=CASCADE)

def __str__(self):
    return self.name

class connectedRealmsIndex(models.Model):
    connectedId = models.DecimalField(max_digits=4, decimal_places=0, help_text="Id for the connected realms")

class auction(models.Model):
    auctionId = models.BigIntegerField(primary_key=True)
    itemId = models.ForeignKey('items', on_delete=CASCADE)
    name = models.CharField(max_length=60)
    buyout = models.IntegerField()
    quantity = models.DecimalField(max_digits=7, decimal_places=0)
    timestamp = models.DateField(auto_now_add=True)
    connectedRealmId = models.ForeignKey('connectedRealm')
    itemBonusList = models.ManyToManyField("itemBonus")

class itemBonus(models.Model):
    id = models.IntegerField()
    effect = models.CharField(max_length=50)

class professionIndex(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

class professionTeir(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    profession = models.ForeignKey("professionIndex", on_delete=models.CASCADE)

class recipeCatagory(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    professionIndex = models.ForeignKey("professionIndex", on_delete=models.CASCADE)
    professionTeir = models.ForeignKey("professionTeir", on_delete=models.CASCADE)

class recipe(models.Model):
    product = models.ForeignKey("item", on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    professionIndex = models.ForeignKey("professionIndex", on_delete=models.CASCADE)
    professionTeir = models.ForeignKey("professionTeir", on_delete=models.CASCADE)
    recipeCatagory = models.ForeignKey("recipeCatagory", on_delete=models.CASCADE)
    reagent = models.ManyToManyField("item")

class material(models.Model):
    recipe = models.ForeignKey("recipe", on_delete=models.CASCADE)
    item = models.ForeignKey("item", on_delete=models.CASCADE)
    quantity = models.IntegerField()

class item(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    recipe = models.ForeignKey("recipe", on_delete=models.CASCADE, null=True)






