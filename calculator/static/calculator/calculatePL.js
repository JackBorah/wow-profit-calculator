class stats {
    constructor() {
        // this.recipe_skill = Number(JSON.parse(document.getElementById('recipe_skill').textContent));
        // this.user_skill = Number(document.getElementById("user_skill").value);
        // this.skill_from_inspiration = Number(document.getElementById("skill_from_inspiration").value);
        this.base_inspiration = Number(document.getElementById("base_inspiration").value);
        this.base_resourcefulness = Number(document.getElementById("base_resourcefulness").value);
        this.base_multicraft = Number(document.getElementById("base_multicraft").value);
    }

    revert_inputs_to_base_stats() {
        let inspiration_input = document.getElementById("base_inspiration");
        let resourcefulness_input = document.getElementById("base_resourcefulness");
        let multicraft_input = document.getElementById("base_multicraft");

        this.inspiration = this.base_inspiration;
        this.resourcefulness = this.base_resourcefulness;
        this.multicraft = this.base_multicraft;

        inspiration_input.value = this.base_inspiration;
        resourcefulness_input.value = this.base_resourcefulness;
        multicraft_input.value = this.base_multicraft;
    }

    get_inspiration() {
        console.log(`base inspitaion ${this.base_inspiration}`);
        return this.base_inspiration / 100;
    }
    set_base_inspiration(inspiration) {
        this.base_inspiration = inspiration;
    }
    get_resourcefulness() {
        return this.base_resourcefulness/ 100;
    }
    set_base_resourcefulness(resourcefulness) {
        this.base_resourcefulness = resourcefulness;
    }
    get_multicraft() {
        return this.base_multicraft / 100;
    }
    set_base_multicraft(multicraft) {
        this.base_multicraft = multicraft;
    }
}
// This is the json data send by the view
// I don't think these are useful to access directly as the inputs, selects, and checkboxes are what is filtering these raw values into the values the user actually is interested in
// const mats = JSON.parse(document.getElementById('mats').textContent);
// const optional_mat_slots = JSON.parse(document.getElementById('optional_mat_slots').textContent);
// const product = JSON.parse(document.getElementById('product').textContent);

const recipe_stats = new stats();

const mats_inputs = document.querySelectorAll(".mat_input");
const optional_mat_inputs = document.querySelectorAll('.optional_mat');
const optional_mat_checkboxes = document.querySelectorAll(".optional_mat_slot_checkbox");
const optional_mat_selects = document.querySelectorAll(".optional_mat_slot_select");

const crafting_stat_divs = document.querySelector("#crafting_stats").querySelectorAll("div");

stat_containers = []
crafting_stat_divs.forEach((div) => {
    stat_containers.push(div);
})
// Need to make some data structure to remember the last added optional mat and its stats to be removed when selects change
prev_added_optional_stats = {}

const base_inspiration_input = document.querySelector("#base_inspiration");
const inspiration_optional_input = document.querySelector("#inspiration_optional");
const total_inspiration_input = document.querySelector("#total_inspiration");

const base_resourcefulness_input = document.querySelector("#base_resourcefulness");
const resourcefulness_optional_input = document.querySelector("#resourcefulness_optional");
const total_resourcefulness_input = document.querySelector("#total_resourcefulness");
 
const base_multicraft_input = document.querySelector("#base_multicraft");
const multicraft_optional_input = document.querySelector("#multicraft_optional");
const total_multicraft_input = document.querySelector("#total_multicraft");

const product_input = document.querySelector("#product_input");
const product_quantity = Number(document.querySelector("#product_quantity").innerHTML);
const cost_input = document.querySelector("#cost");
const inpsired_product_input = document.querySelector("#inspired_product_input");
const average_value_input = document.querySelector("#avgerage_value_input");
const profit_input = document.querySelector("#profit");

function update_total_stats(event) {
    const base_inspitation_value = Number(base_inspiration_input.value);
    const optional_inspiration_value = Number(inspiration_optional_input.value);
    total_inspiration_input.value = base_inspitation_value + optional_inspiration_value;

    const base_resourcefulness_value = Number(base_resourcefulness_input.value);
    const optional_resourcefulness_value = Number(resourcefulness_optional_input.value);
    total_resourcefulness_input.value = base_resourcefulness_value + optional_resourcefulness_value;

    const base_multicraft_value = Number(base_multicraft_input.value);
    const optional_multicraft_value = Number(multicraft_optional_input.value);
    total_multicraft_input.value = base_multicraft_value + optional_multicraft_value;

    calculate_cost()
}

function update_base_stats(event) {
    const stat_type = event.target.parentElement.id;
    const base_stat = event.target.value;

    if (stat_type === "resourcefulness") {
        recipe_stats.set_base_resourcefulness(base_stat);
    }
    else if (stat_type === "inspiration") {
        recipe_stats.set_base_inspiration(base_stat);
    }
    else if (stat_type === "multicraft") {
        recipe_stats.set_base_multicraft(base_stat);
    }

    update_total_stats();
}

function update_sagacious_incense(event) {
    const sagacious_incense_checkbox = event.target;
    const inspiration_buff = 20;
    if (sagacious_incense_checkbox.checked) {
        total_inspiration_input.value = (Number(total_inspiration_input.value) + inspiration_buff).toFixed(0);
    }
    else {
        total_inspiration_input.value = (Number(total_inspiration_input.value) - inspiration_buff).toFixed(0);
    }
    
    calculate_avg_product_value();
}

function update_optional_mat_stats(event) {
    const optional_item_parent = event.target.parentElement;
    const checkbox = optional_item_parent.querySelector("#" + optional_item_parent.id + "_checkbox");
    const selected_index = optional_item_parent.querySelector("select").selectedIndex;
    const selected_item = optional_item_parent.querySelector("select").options[selected_index];
    
    handle_added_stats(inspiration_optional_input, checkbox, "inspiration", selected_item);
    handle_added_stats(multicraft_optional_input, checkbox, "multicraft", selected_item);
    handle_added_stats(resourcefulness_optional_input, checkbox, "resourcefulness", selected_item);

    update_total_stats();
}

function handle_added_stats(input, checkbox, statType, selected_item) {
    if (checkbox.id + `_${statType}` in prev_added_optional_stats) {
        const prev_stat = prev_added_optional_stats[checkbox.id + `_${statType}`];
        const current_stat = Number(input.value);
        input.value = Math.abs((current_stat - prev_stat)).toFixed(0);
        delete prev_added_optional_stats[checkbox.id + `_${statType}`];
    }
    if (selected_item.dataset[statType] && checkbox.checked) {
        const item_stat = Number(selected_item.dataset[statType]);
        const current_stat = Number(input.value);
        input.value = (current_stat + item_stat).toFixed(0);
        
        prev_added_optional_stats[checkbox.id + `_${statType}`] = item_stat;
    }
}

function calculate_cost() {
    let cost = 0;
    let resourcefulness = recipe_stats.get_resourcefulness();
    let pct_saved_from_resourcefulness = 0.3; // this isn't accurate since talent points change this .3 is roughly the median

    for (let mat_input of mats_inputs) {
        let quantity = mat_input.parentElement.querySelector('.matQuantity').innerText;
        //base cost
        cost += Number(mat_input.value) * Number(quantity);
        //resourcefulness
        cost = cost - (cost * resourcefulness * pct_saved_from_resourcefulness)
    }

    optional_mat_inputs.forEach((optional_mat_input, index) => {
        if (optional_mat_checkboxes[index].checked) {
            let quantity = optional_mat_input.parentElement.querySelector('.optional_mat_quantity').innerText;
            cost += Number(optional_mat_input.value) * Number(quantity);
        }
    });
    cost_input.value = cost.toFixed(2);

    calculate_avg_product_value();
}

function calculate_avg_product_value() {
    const product_value = Number(product_input.value);

    let avg_value = calculate_value_with_multicraft(product_value, product_quantity);
    console.log(avg_value)

    if (!inpsired_product_input) {
        average_value_input.value = avg_value.toFixed(2);
    }
    else {
        average_value_input.value = calulate_value_with_inspiration(avg_value).toFixed(2);
    }

    calculate_profit()
}

function calculate_value_with_multicraft(product_value, product_quantity) {
    let multicraft = Number(total_multicraft_input.value) / 100;
    let multicraft_yield = 1.75;
    let quantity_operand = 1;

    if (multicraft == 0) {
        quantity_operand = product_quantity;
    }
    else {
        quantity_operand = product_quantity * multicraft * multicraft_yield
    }
    return (product_value * product_quantity) * (1-multicraft) + (product_value * product_quantity * multicraft_yield) * multicraft;
}

function calulate_value_with_inspiration(avg_value) {
    const inspiration = Number(total_inspiration_input.value) / 100;
    const inspired_product_value = Number(inpsired_product_input.value);
    return avg_value * (1 - inspiration) + inspired_product_value * inspiration;
}

function calculate_profit() {
    const product_value = Number(average_value_input.value);
    const cost_value = Number(cost_input.value);

    profit_input.value = (product_value - cost_value).toFixed(2);
    // TODO multicraft works do the others?
}

for (let mat_input of mats_inputs) {
    mat_input.addEventListener("change", calculate_cost);
}
for (let optional_mat_input of optional_mat_inputs) {
    optional_mat_input.addEventListener("change", calculate_cost);
}
for (let optional_mat_checkbox of optional_mat_checkboxes) {
    optional_mat_checkbox.addEventListener("change", update_optional_mat_stats);
}
for (let optional_mat_select of optional_mat_selects) {
    optional_mat_select.addEventListener("change", update_optional_mat_stats)
}
document.querySelector("#sagacious_incense").addEventListener("change", update_sagacious_incense);
base_resourcefulness_input.addEventListener("change", update_base_stats);
base_multicraft_input.addEventListener("change", update_base_stats);
base_inspiration_input.addEventListener("change", update_base_stats);
product_input.addEventListener("change", calculate_avg_product_value);
inpsired_product_input.addEventListener("change", calculate_avg_product_value);


// 1. Get buyouts of the produced item
    // Depends on the tier of the produced item without inspiration
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
// function calculate_product_value(stats) {
//     let avg_value_input = document.getElementById("avgerage_value_input");
//     let value = Number(document.getElementById("product_input").value);
//     let inspired_value = Number(document.getElementById("inspired_product_input").value);
//     let inspiration = stats.get_inspiration();
//     let multicraft = stats.get_multicraft();
//     const product_quantity = Number(document.getElementById("product_quantity"));

//     value = calculate_value_with_inspiration(value, inspired_value, product_quantity, inspiration);
//     if (product["multicraftable"]) {
//         value += calculate_value_with_multicraft(value, multicraft);
//     }
//     avg_value_input.value = value;
//     return value
// }
// // inspiration logic:
// // Change to increase sill by some insp. If that increase crosses a tier boundry then the product is of higher tier
// // if it doesn't cross the boundry then inspiration is useless
// function calculate_value_with_inspiration(value, inspired_value, product_quantity, inspiration) {
//     value *= product_quantity;
//     inspired_value *= product_quantity;
//     value_with_inspiration = (value * (1 - inspiration)) + (inspired_value * inspiration);
//     return value_with_inspiration;
// }
// function calculate_profit() {
//     let profit_input = document.getElementById("profit");
//     let avg_product_value;
//     let profit;

//     cost = calculate_cost(recipe_stats);

//     avg_product_value = calculate_value(recipe_stats);

//     profit = avg_product_value - cost;
//     profit_input.value = profit;
// }

// function calculate_value_with_multicraft(value, multicraft) {
//     multicraft_value = value * multicraft * 2.5
//     return multicraft_value
// }

// function handleChangingTier(select) {
//     let mat_index = select.getAttribute("matindex");
//     let selected_index = select.selectedIndex;
//     let selected_option = select.options[selected_index];
//     let category_index = selected_option.parentNode.getAttribute("optgroupindex");
//     let materials_div = document.getElementById("materials");
//     let optional_materials_div = document.getElementById("optional materials");
//     let product_div = document.getElementById("product_container");
//     let inputbox;
//     let buyout;
//     let item_tier;
//     let checkbox = document.getElementById(`optional_mat_slot_${mat_index}_checkbox`)
    
//     if (checkbox.checked) {
//         //subtract stats from
//         // how do I get this last value?
//     }

//     if (materials_div.contains(select)) {
//         inputbox = document.getElementById(`mat_${mat_index}_input`);
//         buyout = Number(mats[mat_index]["tiers"][selected_index]["buyout"]);
//     }
//     else if (optional_materials_div.contains(select)) {
//         inputbox = document.getElementById(`optional_mat_${mat_index}_input`);
//         item_tier = select.options[selected_index].value - 1;

//         buyout = Number(optional_mat_slots[mat_index]["categories"][category_index]["items"][item_tier]["buyout"])
//     }
//     else if (product_div.contains(select)) {
//         if (select.getAttribute("id") == "product_select") {
//             inputbox = document.getElementById('product_input');
//             buyout = Number(product["tiers"][selected_index]["buyout"]);
//         }
//         else if (select.getAttribute("id") == "inspired_product_select") {
//             inputbox = document.getElementById('inspired_product_input');
//             buyout = Number(product["tiers"][selected_index]["buyout"]);
//         }
//     }
//     else {
//         console.log("Select tag is not a child of any expected divs!")
//     }
//     inputbox.value = buyout;
//     calculate_profit()
// } 

// function handlechangingStats() {
    
// }

// function handleOptionalMatCheckbox(checkbox) {
//     cost_input = document.getElementById("cost");
//     let cost = Number(cost_input.value);

//     if (checkbox.checked) {
//         recipe_stats.add_optional_mats_stat_buffs(checkbox);
//         cost += get_optional_mat_cost(checkbox);
//         cost_input.value = Math.round(cost)
//     }
//     else {
//         recipe_stats.subtract_optional_mats_stat_buffs(checkbox);
//         cost -= get_optional_mat_cost(checkbox);
//         cost_input.value = Math.round(cost);
//     }
//     calculate_profit();
// }

// function get_optional_mat_cost(checkbox) {
//     mat_index = checkbox.getAttribute("matindex");
//     let checked_input = document.getElementById(`optional_mat_${mat_index}_input`);
//     return Number(checked_input.value);
// }

// /*
// How to handle optional mats.

// Why are they important?
// They increase crafting stats or combat stats
// Since people will use these the crafting stats and item costs need to be included in the calculation

// Implementation
// Goal
// Optional mat prices need to be added to the cost calculation and their stats need to be added
// to the stats for the complete calculation. 

// How it is currently. Cost calculation is seperate from optional mat calculation. 
// Optional mats are included in the cost when its associated checkbox is checked.
// When it is uncheceked the number in the input is subtracted from the cost.
// The price can be modified when checked and cause the subtraction to be larger or smaller then the 
// addition.

// How it should work
// Checking the box will include it in the cost. Its stats are added to the users current stats.
// If the user changes the price of the optional mats then that new price is used in the cost calculation
// and the old cost is removed. When the checkbox is unchecked the stats and price is not counted in the
// cost calculator. 

// How to implement
// HAve a parent calculator function that calls an optional mat and mat cost calculator and outs the cost.
// It checks to see what boxes are checked and factors those into the calculation and adds their stats. 
// If unchecked it is ignored. Everything will call this onchange so anychanges to stats, prices, or checkboxes
// will cause a new calculation of cost.
// */