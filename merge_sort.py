

def _merge(left_list, right_list):
    """
    Combine two pre-sorted lists of integers into one sorted list.
    """
    merged_lists = []

    # avoid IndexError by appending infinity to each subarray as a sentinal
    # the loop below will never increment past this and values will always be in range
    left_list.append(float('inf'))
    right_list.append(float('inf'))

    left_pointer = 0
    right_pointer = 0

    # one iteration for each item in both lists, less the two sentinal values
    for _ in xrange(len(left_list) + len(right_list) - 2):
        left_item = left_list[left_pointer]
        right_item = right_list[right_pointer]

        if left_item > right_item:
            merged_lists.append(right_item)
            right_pointer += 1
        else:
            merged_lists.append(left_item)
            left_pointer += 1

    return merged_lists


def merge_sort(int_list):
    """
    Sort a list of integers by dividing list in half recursively and recombining.

    This implementation uses memory inefficiently for the sake of readability.
    Runtime: f(n) = O(nlgn)
    """

    # split the list in two
    mid_idx = len(int_list) / 2
    left_list = int_list[:mid_idx]
    right_list = int_list[mid_idx:]

    # recurse until subarrays have length 1: a subarray of length one is always sorted
    if len(left_list) > 1:
        left_list = merge_sort(left_list)
    if len(right_list) > 1:
        right_list = merge_sort(right_list)

    # at this point subarrays are sorted and can be merged in linear time
    return _merge(left_list, right_list)


class Tests(unittest.TestCase):

    def test_sort__six_element_list(self):
        int_list = [2, 1, 9, 7, 7, 1]
        expected = [1, 1, 2, 7, 7, 9]

        assert merge_sort(int_list) == expected

    def test_sort__empty_list(self):
        int_list = []
        expected = []

        assert merge_sort(int_list) == expected

    def test_sort__one_element_list(self):
        int_list = [1]
        expected = [1]

        assert merge_sort(int_list) == expected
