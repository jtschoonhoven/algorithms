

def insertion_sort(int_list):
    """
    Sort a list of integers, moving left to right, shifting items left as needed.

    Runtime: f(n) = O(n^2)
    """
    for idx, item in enumerate(int_list):
        if idx == 0:
            continue

        prev_idx = idx - 1
        prev_item = int_list[prev_idx]

        # swap item with left neighbor until sorted
        while prev_item > item and prev_idx >= 0:
            int_list[prev_idx + 1] = prev_item
            prev_idx -= 1
            prev_item = int_list[prev_idx]

        int_list[prev_idx + 1] = item

    return int_list


class Tests():

    def test_sort__increasing(self):
        int_list = [1, 2, 3]
        expected = [1, 2, 3]

        assert insertion_sort(int_list) == expected

    def test_sort__decreasing(self):
        int_list = [3, 2, 1]
        expected = [1, 2, 3]

        assert insertion_sort(int_list) == expected

    def test_sort__random(self):
        int_list = [2, 1, 9, 7, 7, 1]
        expected = [1, 1, 2, 7, 7, 9]

        assert insertion_sort(int_list) == expected
