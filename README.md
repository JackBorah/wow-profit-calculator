# WoW Profit Calculator
##### By Jack Borah

This website will calculate the profit from crafting items, or how much you would lose crafting.

The price data comes from blizzards api which updates every hour. 
This data will fill in the calculator fields initally but custom prices can be inserted by users. 

Recepies will be broken down first by expansion, then profession.
I will first implement shadowlands fully, and maybe move onto the other expansions. I could also do shadowlands and classic as they are the main versions. 
I want to show the profitablility at different market prices. 
    100 copper ore @ 30g each
    100 copper ore @ 40g each
    I've been to quick to buy 200 ores but only calculated profit as if they all cost 30g/ea showing the profit for each bracket would be useful. But how would that fit on the screen? If something needs 6 input mats that would be 6 different lists of prices.
        solutions:
            have a quantity amount specified so if someone wants to buy 200 ores the profit will be calculated from the prices and the amount.
            have a seperate list of posted auctions at different prices that users can select to calculate profit

As of this planning I don't think I will include any recipies that can't be completely sourced from the auction house, although something like crafters marks are fine as they are craftable.

Since I only have a handle on Django right now that will be the backend. 

I will have django render a page with the profits displayed but I could also allow users to input prices and have calculation on the front end for their custom prices. This should be faster the having a user sending a request back to Django and then waiting for a response. 

The site will be decorated with bootstrap. I think thats enough to style the whole thing. 

I'm always worried about secutity and have to look into that. 
