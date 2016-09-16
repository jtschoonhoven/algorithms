import unittest


def _max_crossing_subarray(int_list, start_idx, l_end_idx, r_start_idx, end_idx):
    """
    Find the maximum subarray of int_list between start and end that crosses the mid_idx.

    Attacks the problem by considering left and right subarrays separately, working
    outwards from the *midpoint*. The greatest crossing subarray must include (at least)
    the last item of the left array and the first item of the right array, so summing
    the max left and right gives us the max crossing subarray.

    Runtime: O(n)

    :param int_list: int[]
    :param start_idx: int - index of first element in left subarray
    :param l_end_idx: int - index of last item in left subarray (inclusive)
    :param r_start_idx: int - index of first item in right subarray
    :param end_idx: int -index of last item in right subarray (inclusive)
    """
    l_current_sum = 0
    l_greatest_sum = float('-inf')
    l_greatest_idx = float('-inf')

    # right to left, find the max subarray of the left list that touches the midpoint
    for idx in xrange(l_end_idx, start_idx - 1, -1):
        l_current_sum += int_list[idx]
        if l_current_sum > l_greatest_sum:
            l_greatest_sum = l_current_sum
            l_greatest_idx = idx

    r_current_sum = 0
    r_greatest_sum = float('-inf')
    r_greatest_idx = float('-inf')

    # left to right, find the max subarray of the right list that touches the midpoint
    for idx in xrange(r_start_idx, end_idx + 1):
        r_current_sum += int_list[idx]
        if r_current_sum > r_greatest_sum:
            r_greatest_sum = r_current_sum
            r_greatest_idx = idx

    # combine right and left to get the max crossing subarray
    max_crossing_sum = l_greatest_sum + r_greatest_sum
    max_crossing_start = l_greatest_idx
    max_crossing_end = r_greatest_idx

    return max_crossing_sum, max_crossing_start, max_crossing_end


def max_subarray(int_list, start_idx=None, end_idx=None):
    """
    Find the contiguous subarray of int_list that sums to the greatest value.

    A solution to problems of the type, "given a list of stock prices per day,
    choose the buy and sell daysthat would yield the greatest profit".

    Runtime: O(n lg(n))

    :param int_list: int[]
    :param l_idx: int|None - index of first element to consider
    :param r_idx: int|None - index of last element (inclusive)
    :return: (int, int, int) - 3-tup for max subarray: sum, start_idx, end_idx (inclusive)
    """
    if start_idx is None:
        # set start and end indexes on first iteration if ommitted
        start_idx = 0
        end_idx = len(int_list) - 1

    # if this is a one element list we can calculate the return values directly
    if end_idx == start_idx:
        return int_list[start_idx], start_idx, end_idx

    # find the left-end and right-start indexes of the halved int_list
    # this *could* be done with a single "mid_idx" value, but it's easier to reason about
    # if the indexes are inclusive
    l_end_idx = (end_idx + start_idx) / 2
    r_start_idx = l_end_idx + 1

    # divide int_list in half recursively (down to one-element lists) then find the sum
    # and start/end index of the greatest subarray
    l_max_sum, l_max_start, l_max_end = max_subarray(int_list, start_idx, l_end_idx)
    r_max_sum, r_max_start, r_max_end = max_subarray(int_list, r_start_idx, end_idx)

    # also check whether there is a greater subarray that crosses left and right subs
    c_max_sum, c_max_start, c_max_end = _max_crossing_subarray(
        int_list, start_idx, l_end_idx, r_start_idx, end_idx)

    # return the greatest subarray
    if l_max_sum >= c_max_sum and l_max_sum >= r_max_sum:
        return l_max_sum, l_max_start, l_max_end
    elif c_max_sum >= r_max_sum:
        return c_max_sum, c_max_start, c_max_end
    else:
        return r_max_sum, r_max_start, r_max_end


class Tests(unittest.TestCase):

    def test_max_subarray__all_positive(self):
        """Assert returns full list if all elements are positive."""
        int_list = [5, 1, 5, 2, 9, 8]
        expected = sum(int_list), 0, len(int_list) - 1

        assert max_subarray(int_list) == expected

    def test_max_subarray__all_negative(self):
        """Assert returns least negative element if all elements are negative."""
        int_list = [-6, -2, -1, -5, -4]
        expected = -1, 2, 2
        assert max_subarray(int_list) == expected

    def test_max_subarray__one_solution(self):
        int_list = [1, 2, -9, 3, 4, -9, 5, 6, -9]
        expected = 11, 6, 7
        assert max_subarray(int_list) == expected

    def test_max_subarray__multiple_solutions(self):
        int_list = [1, 2, -5, 1, 2]

        # there are multiple correct subarrays
        expected_1 = 3, 0, 1
        expected_2 = 3, 3, 4

        result = max_subarray(int_list)
        assert result == expected_1 or result == expected_2
