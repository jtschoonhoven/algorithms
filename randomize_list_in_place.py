from copy import copy
from random import randint


def randomize_list_in_place(int_list):
    """
    Randomize list in place in linear time.
    """
    max_index = len(int_list) - 1

    for index, item in enumerate(int_list):
        swap_index = randint(index, max_index)
        int_list[index] = int_list[swap_index]
        int_list[swap_index] = item

    return int_list


class Test(object):

    def test_is_random(self):
        list_1 = range(999)
        list_2 = range(999)

        original_list_1 = copy(list_1)
        original_list_2 = copy(list_2)

        randomize_list_in_place(list_1)
        randomize_list_in_place(list_2)

        # this test will fail 3/1000! times, i.e. it will never fail
        assert original_list_1 != list_1
        assert original_list_2 != list_2
        assert list_1 != list_2
