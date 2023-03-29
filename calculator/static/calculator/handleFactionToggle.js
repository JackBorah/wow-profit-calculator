//variables need to be passed in to be used
//or set as globals by defining it in the html
// as in <script>let x = {{ someTemplateVariable }}</script>

// var alliance_product_buyout = {{ product_auction_set.0.1.0.buyout|escapejs }}
// var horde_product_buyout = {{ product_auction_set.1.1.0.buyout|escapejs }}
// var alliance_product_bid = {{ product_auction_set.0.1.0.bid|escapejs }}
// var horde_product_bid = {{ product_auction_set.1.1.0.bid|escapejs }}
// var alliance_product_unit_price = {{ product_auction_set.0.1.0.unit_price|escapejs }}
// var horde_product_unit_price = {{ product_auction_set.1.1.0.unit_price|escapejs }}

function handleFactionToggle() {
  var toggle_label = document.getElementById("faction_toggle_label");
  var product_input = document.getElementById("product");
  if (toggle_label.innerHTML === "Horde") {
    toggle_label.innerHTML = "Alliance";
    if (alliance_product_buyout != "None") {
      product_input.value = alliance_product_buyout;
    } else if (alliance_product_unit_price != "None") {
      product_input.value = alliance_product_unit_price;
    } else {
      product_input.value = alliance_product_bid;
    }
  } else if (toggle_label.innerHTML === "Alliance") {
    toggle_label.innerHTML = "Horde";
    if (horde_product_buyout != "None") {
      product_input.value = horde_product_buyout;
    } else if (horde_product_unit_price != "None") {
      product_input.value = horde_product_unit_price;
    } else {
      product_input.value = horde_product_bid;
    }
  }
  calculatePL()
}
