// teirs are determined by skill and % of recipes skill
// rounded down
// items with 3 tiers seem to have 1 delimeter at 50% recipe skill
// items with 5 tiers probally have 3 delimeters at 25%, 50%, and 75%
// i know for a fact they have a 50% and assume the others are true
// equipable items seem to have 5 tiers and everything else 3 tiers
function determine_product_tier(recipe_skill, user_skill) {
    let tier = 0;
    let num_of_tiers = product["num_of_tiers"];
    if (num_of_tiers == 5) { 
        if (user_skill < Math.floor(recipe_skill * 0.25)) {
            tier = 0
        } 
        else if (user_skill < Math.floor(recipe_skill * 0.5)) {
            tier = 1
        }
        else if (user_skill < Math.floor(recipe_skill * 0.75)) {
            tier = 2
        }
        else if (user_skill < Math.floor(recipe_skill)) {
            tier = 3
        }
        else if (user_skill >= recipe_skill) {
            tier = 4
        }
    }
    else if (num_of_tiers == 3)
        if (user_skill < Math.floor(recipe_skill * 0.5)) {
            tier = 0
        } 
        else if (user_skill < recipe_skill) {
            tier = 1
        }
        else if (user_skill >= recipe_skill) {
            tier = 2
        }
    return tier
}
