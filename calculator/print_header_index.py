import csv

crafting_data_path = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\CraftingData.csv"
spell_effect_path = r"C:\Users\Jack\Projects\wowprofitcalculator\calculator\wow_csv_data\SpellEffect.csv"
item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\Item.csv"
item_sparse_csv = r"C:\Users\Jack\Projects\wowprofitcalculator\calculator\wow_csv_data\ItemSparse.csv"
modified_crafting_reagent_item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingReagentItem.csv"
mcr_slot_x_mcr_category_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\MCRSlotXMCRCategory.csv"
modified_crafting_item_csv = r"C:\Users\borah\Projects\wow-profit-calculator\calculator\wow_csv_data\ModifiedCraftingItem.csv"
spell_reagents_csv = r"C:\Users\Jack\Projects\wowprofitcalculator\calculator\wow_csv_data\SpellReagents.csv"

def print_header_with_column_index(path):
    with open(path, encoding='utf-8-sig') as file:
        crafting_data_csv = csv.reader(file)
        for index, column_header in enumerate(next(crafting_data_csv)):
            print(f"{index}, {column_header}")

print_header_with_column_index(spell_reagents_csv)
