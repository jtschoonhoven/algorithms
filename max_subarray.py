from collections import namedtuple
import unittest


MaxSubarray = namedtuple('MaxSubarray', ('sum', 'start_idx', 'end_idx'))


def max_subarray(int_list):
    """
    Find the subarray from a list of integers that sums to the greatest value.

    Runtime: f(n) = O(n)
    """

    current_sum = 0
    current_start_idx = None

    max_sum = None
    max_start_idx = None
    max_end_idx = None

    for current_idx, val in enumerate(int_list):
        current_sum += val

        # value is None on first iteration or if current_sum drops below 0
        if current_start_idx is None:
            current_start_idx = current_idx

        # true if first run or new max_subarray has been found: update max stats
        if current_sum > max_sum or max_sum is None:
            max_sum = current_sum
            max_end_idx = current_idx
            max_start_idx = current_start_idx

        # if the current sum drops below zero, reset current stats
        if current_sum < 0:
            current_sum = 0
            current_start_idx = None

    return MaxSubarray(max_sum, max_start_idx, max_end_idx)


class Tests(unittest.TestCase):

    def test_max_subarray__all_positive(self):
        """Assert returns full list if all elements are positive."""
        int_list = [5, 1, 5, 2, 9, 8]
        expected = MaxSubarray(sum(int_list), 0, len(int_list) - 1)

        assert max_subarray(int_list) == expected

    def test_max_subarray__all_negative(self):
        """Assert returns least negative element if all elements are negative."""
        int_list = [-6, -2, -1, -5, -4]
        expected = MaxSubarray(-1, 2, 2)
        assert max_subarray(int_list) == expected

    def test_max_subarray__one_solution(self):
        int_list = [1, 2, -9, 3, 4, -9, 5, 6, -9]
        expected = MaxSubarray(11, 6, 7)
        assert max_subarray(int_list) == expected

    def test_max_subarray__multiple_solutions(self):
        int_list = [1, 2, -5, 1, 2]

        # there are multiple correct subarrays
        expected_1 = MaxSubarray(3, 0, 1)
        expected_2 = MaxSubarray(3, 3, 4)

        result = max_subarray(int_list)
        assert result == expected_1 or result == expected_2
