class stats {
    constructor() {
        // this.recipe_skill = Number(JSON.parse(document.getElementById('recipe_skill').textContent));
        // this.user_skill = Number(document.getElementById("user_skill").value);
        // this.skill_from_inspiration = Number(document.getElementById("skill_from_inspiration").value);
        this.base_inspiration = Number(document.getElementById("inspiration").value);
        this.inspiration = this.base_inspiration;
        this.base_resourcefulness = Number(document.getElementById("resourcefulness").value);
        this.resourcefulness = this.base_resourcefulness;
        this.base_multicraft = Number(document.getElementById("multicraft").value);
        this.multicraft = this.base_multicraft;

    }

    update_stats() {
        let inspiration_input = document.getElementById("inspiration");
        let resourcefulness_input = document.getElementById("resourcefulness");
        let multicraft_input = document.getElementById("multicraft");

        this.base_inspiration = inspiration_input.value;
        this.inspiration = this.base_inspiration;
        this.base_resourcefulness = resourcefulness_input.value;
        this.resourcefulness = this.base_resourcefulness;
        this.base_multicraft = multicraft_input.value;
        this.multicraft = this.base_multicraft;
    }

    revert_inputs_to_base_stats() {
        let inspiration_input = document.getElementById("inspiration");
        let resourcefulness_input = document.getElementById("resourcefulness");
        let multicraft_input = document.getElementById("multicraft");

        this.inspiration = this.base_inspiration;
        this.resourcefulness = this.base_resourcefulness;
        this.multicraft = this.base_multicraft;

        inspiration_input.value = this.base_inspiration;
        resourcefulness_input.value = this.base_resourcefulness;
        multicraft_input.value = this.base_multicraft;
    }

    get_inspiration() {
        return this.inspiration / 1000;
    }

    get_resourcefulness() {
        return this.resourcefulness / 1000;
    }

    get_multicraft() {
        return this.multicraft / 1000;
    }

    add_optional_mats_stat_buffs(checkboxes) {
        let checkbox;
        let checked;
        let mat_index;
        let tier_index;
        let optional_mat;
        let optional_mat_inspiration;
        let optional_mat_resourcefulness;
        let optional_mat_multicraft;
        let inspiration_input;
        let resourcefulness_input;
        let multicraft_input;

        this.update_stats()
        this.revert_inputs_to_base_stats();

        for (let i = 0; i < checkboxes.length; i++) {
            checkbox = checkboxes[i];
            checked = checkbox.checked;

            if (checked) {
                mat_index = checkbox.getAttribute("matindex");
                tier_index = Number(document.getElementById(`optional_mat_${mat_index}_select`).value) - 1;

                optional_mat = optional_mats[mat_index]["tiers"][tier_index];
                optional_mat_inspiration = Number(optional_mat["inspiration"]);
                optional_mat_resourcefulness = Number(optional_mat["resourcefulness"]);
                optional_mat_multicraft = Number(optional_mat["multicraft"]);
        
                if (optional_mat_inspiration) {
                    this.inspiration += optional_mat_inspiration;
                    inspiration_input = document.getElementById("inspiration");
                    inspiration_input.value = this.inspiration;
                } 
                else if (optional_mat_resourcefulness) {
                    this.resourcefulness += optional_mat_resourcefulness;
                    resourcefulness_input = document.getElementById("resourcefulness");
                    resourcefulness_input.value = this.resourcefulness;
                }
                else if (optional_mat_multicraft) {
                    this.multicraft += optional_mat_multicraft;
                    multicraft_input = document.getElementById("multicraft");
                    multicraft_input.value = this.multicraft;
                }
            }
        }
    }
}

const mats = JSON.parse(document.getElementById('mats').textContent);
const optional_mats = JSON.parse(document.getElementById('optional_mats').textContent);
const product = JSON.parse(document.getElementById('product').textContent);
const recipe_stats = new stats();


// 1. Get stats from dom
// 2. Get checked optional mat costs from dom
// 3. Get checked optional mat objects from django
// 4. Add checked optional mats stats to current stats
// 5. Calculate cost and save to cost var
// 6. Calculate product's value and save to value var
// 7. Calculate profit from value - cost
// 8. Return profit variable
function calculate_profit() {
    let profit_input = document.getElementById("profit");
    let avg_product_value;
    let profit;

    cost = calculate_cost(recipe_stats);

    avg_product_value = calculate_value(recipe_stats);

    profit = avg_product_value - cost;
    profit_input.value = profit;
}

function calculate_cost(recipe_stats) {
    let cost = 0;
    let cost_input = document.getElementById("cost");
    let checkboxes = document.querySelectorAll(".optional_mat_checkbox");
    
    recipe_stats.add_optional_mats_stat_buffs(checkboxes);

    cost += calculate_optional_mat_cost(checkboxes);
    cost += calculate_mats_cost_with_resourcefulness(recipe_stats);

    cost_input.value = cost;
    return cost;
}

function calculate_optional_mat_cost(checkboxes) {
    let optional_mat_cost = 0;
    let optional_mat_input;
    let checked;
    
    for (let i = 0; i < checkboxes.length; i++) {
        checked = checkboxes[i].checked;
        if (checked) {
            optional_mat_input = document.getElementById(`optional_mat_${i}_input`);
            optional_mat_cost += Number(optional_mat_input.value);
        }
    }
    return optional_mat_cost;
}

function calculate_mats_cost_with_resourcefulness(recipe_stats) {
    let cost = 0;
    let mats_quantity = document.querySelectorAll(".matQuantity")
    let mats_inputs = document.querySelectorAll(".mat_input");
    let resourcefulness = recipe_stats.get_resourcefulness();

    for (let i = 0; i < mats_inputs.length; i++) {
        let price = mats_inputs[i].value;
        let quantity = Number(mats_quantity[i].innerHTML);

        cost += calculate_mat_price_with_resourcefulness(price, resourcefulness) * quantity;
    }
    return cost
}

function calculate_mat_price_with_resourcefulness(mat_price, resourcefulness) {
    return mat_price - (mat_price * resourcefulness)
}

// 1. Get buyouts of the produced item
    // Depends on the tier of the produced item without inspiratino
    // a. take skill from user_skill inputbox
    // b. call get_product_tier(user_skill, recipe_skill)
    // c. find that products buyout in context
// 2. Calculate value with inspiration
    // a. if user_skill + skill_from_inspiration crosses a tier boundry get its value
    // b. formula = current_tier_value * (1-inspiration) + inspired_tier_value * inspiration
// 3. Calculate value with multicraft
    // a. only include if the recipe can multicraft
        // Seems like only stackable items can multicraft I don't know if that means all stackable items can or just some
    // a. formula = (product_value * multicraft * 2.5), where 2.5 is the avg number produced by proc
// 4. return value
function calculate_value(recipe_stats) {
    let avg_value_input = document.getElementById("avgerage_value_input");
    let value = Number(document.getElementById("product_input").value);
    let inspired_value = Number(document.getElementById("inspired_product_input").value);
    let inspiration = recipe_stats.get_inspiration();
    let multicraft = recipe_stats.get_multicraft();

    value += calculate_value_with_inspiration(value, inspired_value, inspiration);
    if (product["multicraftable"]) {
        value += calculate_value_with_multicraft(value, multicraft);
    }
    avg_value_input.value = value;
    return value
}
// inspiration logic:
// Change to increase sill by some int. If that increase crosses a tier boundry then the product is of higher tier
// if it doen'st cross the boundry then inspirfation is useless
function calculate_value_with_inspiration(value, inspired_value, inspiration) {
    value_with_inspiration = (value * (1 - inspiration)) + (inspired_value * inspiration)
    return value_with_inspiration
}

function calculate_value_with_multicraft(value, multicraft) {
    multicraft_value = value * multicraft * 2.5
    return multicraft_value
}

function handleChangingTier(select) {
    let mat_index = Number(select.getAttribute("matindex"));
    let tier = Number(select.value) - 1;
    let materials_div = document.getElementById("materials");
    let optional_materials_div = document.getElementById("optional materials");
    let product_div = document.getElementById("product_container");

    let inputbox;
    let buyout;

    if (materials_div.contains(select)) {
        inputbox = document.getElementById(`mat_${mat_index}_input`);
        buyout = Number(mats[mat_index]["tiers"][tier]["buyout"]);
    }
    else if (optional_materials_div.contains(select)) {
        inputbox = document.getElementById(`optional_mat_${mat_index}_input`);
        buyout = Number(optional_mats[mat_index]["tiers"][tier]["buyout"]);
    }
    else if (product_div.contains(select)) {
        if (select.getAttribute("id") == "product_select") {
            inputbox = document.getElementById('product_input');
            buyout = Number(product["tiers"][tier]["buyout"]);
        }
        else if (select.getAttribute("id") == "inspired_product_select") {
            inputbox = document.getElementById('inspired_product_input');
            buyout = Number(product["tiers"][tier]["buyout"]);
        }
    }
    else {
        console.log("Select tag is not a child of any expected divs!")
    }

    inputbox.value = buyout;
    calculate_profit()
} 

// 1. get checkbox
// 2. if unchecked
    // a. subtract added stats from stats object
    // b. subtract opt_mat value from cost input box
// 3. if checked
    // a. add stats to stats object
    // b. add cost to costs input box
function handleOptionalMatCheckbox(checkbox) {
    cost_input = document.getElementById("cost");
    let cost = Number(cost_input.value);

    if (checkbox.checked) {
        recipe_stats.add_optional_mats_stat_buffs(checkbox, optional_mats);
        cost += get_optional_mat_cost(checkbox);
        cost_input.value = Math.round(cost)
    }
    else {
        recipe_stats.subtract_optional_mats_stat_buffs(checkbox, optional_mats);
        cost -= get_optional_mat_cost(checkbox);
        cost_input.value = Math.round(cost);
    }
    calculate_profit();
}

function get_optional_mat_cost(checkbox) {
    mat_index = checkbox.getAttribute("matindex");
    let checked_input = document.getElementById(`optional_mat_${mat_index}_input`);
    return Number(checked_input.value);
}

/*
How to handle optional mats.

Why are they important?
They increase crafting stats or combat stats
Since people will use these the crafting stats and item costs need to be included in the calculation

Implementation
Goal
Optional mat prices need to be added to the cost calculation and their stats need to be added
to the stats for the complete calculation. 

How it is currently. Cost calculation is seperate from optional mat calculation. 
Optional mats are included in the cost when its associated checkbox is checked.
When it is uncheceked the number in the input is subtracted from the cost.
The price can be modified when checked and cause the subtraction to be larger or smaller then the 
addition.

How it should work
Checking the box will include it in the cost. Its stats are added to the users current stats.
If the user changes the price of the optional mats then that new price is used in the cost calculation
and the old cost is removed. When the checkbox is unchecked the stats and price is not counted in the
cost calculator. 

How to implement
HAve a parent calculator function that calls an optional mat and mat cost calculator and outs the cost.
It checks to see what boxes are checked and factors those into the calculation and adds their stats. 
If unchecked it is ignored. Everything will call this onchange so anychanges to stats, prices, or checkboxes
will cause a new calculation of cost.
*/