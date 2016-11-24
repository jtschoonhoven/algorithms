from collections import namedtuple


MaxDelta = namedtuple('MaxDelta', ('delta', 'start_idx', 'end_idx'))


def max_delta(int_list):
    """
    Find the indices of two items in a list that, left to right, have the greatest delta.

    Runtime: f(n) = O(n)
    """
    if len(int_list) == 1:
        return MaxDelta(delta=0, start_idx=0, end_idx=0)

    current_low_idx = 0
    current_high_idx = 1

    start_delta = int_list[current_high_idx] - int_list[current_low_idx]
    max_delta = MaxDelta(start_delta, current_low_idx, current_high_idx)

    for current_idx, val in enumerate(int_list):

        # skip the first two iterations, we've already compared the first two elements
        if current_idx <= current_high_idx:
            continue

        # if value is greater than one we've seen before, update current_high_idx
        if val > int_list[current_high_idx]:
            current_high_idx = current_idx

            # if we've found a new current_high_idx, check if we've found a new max_delta
            current_delta = int_list[current_high_idx] - int_list[current_low_idx]
            if current_delta > max_delta.delta:
                max_delta = MaxDelta(current_delta, current_low_idx, current_high_idx)

        # if value is lower than one we've seen before, update current_low_idx
        elif val < int_list[current_low_idx]:
            current_low_idx = current_idx

            # ensure max_delta is found even if all elements are decreasing
            # to allow max_deltas where start_idx and end_idx are the same, where delta
            # would always be 0, don't subtract 1 from currend_idx below
            incremental_delta = int_list[current_idx] - int_list[current_idx - 1]
            if incremental_delta > max_delta.delta:
                max_delta = MaxDelta(incremental_delta, current_idx - 1, current_idx)

    return max_delta


class Tests():

    def test_max_delta__all_increasing(self):
        """Assert result spans full list if all elements are increasing."""
        int_list = [-2, -1, 0, 2, 9]
        expected = MaxDelta(11, 0, len(int_list) - 1)

        assert max_delta(int_list) == expected

    def test_max_delta__all_decreasing(self):
        """Assert result is smallest negative delta if all elements are decreasing."""
        int_list = [9, 4, 2, 0, -1, -3]
        expected = MaxDelta(-1, 3, 4)
        assert max_delta(int_list) == expected

    def test_max_delta__one_solution(self):
        int_list = [1, 2, -9, 3, 4, -8, 5, 6, -9]
        expected = MaxDelta(15, 2, 7)
        assert max_delta(int_list) == expected

    def test_max_delta__multiple_solutions(self):
        int_list = [3, 5, 1, 2, 1, 6, 5]

        # there are multiple correct deltas
        expected_1 = MaxDelta(5, 2, 5)
        expected_2 = MaxDelta(5, 4, 5)

        result = max_delta(int_list)
        assert result == expected_1 or result == expected_2
