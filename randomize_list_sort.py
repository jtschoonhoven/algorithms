from collections import defaultdict
from random import randint

from merge_sort import merge_sort as sort_algorithm


def randomize_list_sort(int_list):
    """
    Randomize the order of int_list.

    Works by assigning "rank" to each item in {int_list} by generating a list of random
    integers. That list is sorted, then used as a key to permute the input list.

    This is an inefficient, n lg(n) solution. An in-place linear alternative exists.
    """
    max_random_int = len(int_list) ** 3

    # generate list of random "ranks" to assign to input list
    ranks = []
    rank_int_mapping = defaultdict(list)
    for item in int_list:
        random_int = randint(0, max_random_int)
        ranks.append(random_int)
        rank_int_mapping[random_int].append(item)

    sorted_ranks = sort_algorithm(ranks)

    # use ranks to shuffle result
    result = []
    for rank in sorted_ranks:
        item = rank_int_mapping[rank].pop()
        result.append(item)

    return result


class Test(object):

    def test_is_random(self):
        list_1 = range(1000)
        list_2 = range(1000)

        random_list_1 = randomize_list_sort(list_1)
        random_list_2 = randomize_list_sort(list_2)

        # this test will fail 3/1000! times, i.e. it will never fail
        assert random_list_1 != list_1
        assert random_list_2 != list_2
        assert random_list_1 != random_list_2
