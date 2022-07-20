import os
import sys
import timeit
from dotenv import load_dotenv
import django
from pprint import pprint
import getwowdata

load_dotenv()

sys.path.append(os.path.join(sys.path[0], ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wowprofitcalculator.settings")

django.setup()

if __name__ == "__main__":

    from calculator import consume_api, models

    test_dict = {"a": 1, "b": 2, "c": 3, "z": 4, "y": 5, "z": 6}

    def consume_illidan_auctions():
        """
        Make instance of WowApi.
        Get auctions from blizzard api
        Loop through all auctions but do nothing to them.
        """
        us_realm_api = getwowdata.WowApi("us")
        illidan_id = 57
        count = 0
        values = consume_api.consume_auctions(us_realm_api, illidan_id)
        for auction in values:
            # count += 1
            # print(f'\r{count} auctions consumed', end='')
            pass

    def consume_illidan_auctions_no_yield():
        us_realm_api = getwowdata.WowApi("us")
        illidan_id = 57
        json = us_realm_api.get_auctions(illidan_id)
        for auction in json["auctions"]:
            pass

    def long_for_loop():
        count = 0
        for i in range(140000):
            # count += 1
            # print(f'\r{count}', end='')
            pass
        # print('\n')

    def get_or_create():
        """Significant"""
        models.ItemBonus.objects.get_or_create(id=1)

    def get_only():
        """Significant"""
        models.ItemBonus.objects.get(id=1517)

    def get_all():
        """Insignificant"""
        models.ItemBonus.objects.all()

    def queryset_get():
        """Significant"""
        x = models.ItemBonus.objects.all()
        x.get(id=1517)

    def yield_statement():
        for i in range(140000):
            yield i

    def yield_consumer():
        """Under a second but significant"""
        for i in yield_statement():
            pass

    def return_statement():
        x = []
        for i in range(140000):
            x.append(i)
        return x

    def return_consumer():
        """Under a second but significant"""
        x = return_statement()
        for i in x:
            pass

    def dict_get():
        """Insignificant"""
        test_dict.get("a")

    def dict_index():
        """Insignificant"""

        test_dict["a"]

    def create_list():
        """Insignificant"""
        x = []

    def dict_index_many_keys():
        """Insignificant"""
        auction_id = test_dict.get("x")
        buyout = test_dict.get("y")
        bid = test_dict.get("z")
        unit_price = test_dict.get("a")
        quantity = test_dict.get("b")
        time_left = test_dict.get("c")

    def single_query_looped_through():
        items = models.Item.objects.all()
        for x in items:
            pass

    def one_query_per_loop_iteration():
        for x in range(140000):
            item = models.Item.objects.get(id=117373)

    def insert_illidan_auctions():
        """Illidan is a large server. Higher sample time."""
        us_realm_api = getwowdata.WowApi("us")
        illidan_id = 57
        consume_api.insert_auctions(us_realm_api, illidan_id)

    def insert_winterhoof_auctions():
        """Winterhoof is a small server. Smaller sample time."""
        us_realm_api = getwowdata.WowApi("us")
        winterhoof_id = 4
        consume_api.insert_auctions(us_realm_api, winterhoof_id)

    if __name__ == "__main__":
        print("\n")
        # print(timeit.timeit('consume_illidan_auctions()',globals=globals(), number=10)/10)
        # print(timeit.timeit('insert_illidan_auctions()',globals=globals(), number=1)/1)
        print(
            timeit.timeit("insert_winterhoof_auctions()", globals=globals(), number=1)
            / 1
        )
        # print(timeit.timeit('consume_illidan_auctions_no_yield()',globals=globals(), number=1))
        # print(timeit.timeit('long_for_loop()', globals=globals(), number = 1))
        # print(timeit.timeit("get_or_create()", globals=globals(), number=100) / 100)
        # print(timeit.timeit("get_only()", globals=globals(), number=100) / 100)
        # print(timeit.timeit('get_all()', globals=globals(), number = 1000) / 1000)
        # print(timeit.timeit('queryset_get()', globals=globals(), number = 1000) / 1000)
        # print(timeit.timeit('yield_consumer()', globals=globals(), number = 1000) / 1000)
        # print(timeit.timeit('return_consumer()', globals=globals(), number = 1000) / 1000)
        # print(timeit.timeit('create_list()', globals=globals(), number = 1000))
        # print(timeit.timeit('dict_index_many_keys()', globals=globals(), number = 1000) / 1000)
        # print(timeit.timeit('single_query_looped_through()', globals=globals(), number = 10) / 10)
        # print(timeit.timeit('one_query_per_loop_iteration()', globals=globals(), number = 1) / 1)
