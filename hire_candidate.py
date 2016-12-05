import math
from random import randint

from randomize_list_in_place import randomize_list_in_place


def _should_hire_candidate(candidate_index, score, num_candidates):
    """
    Decide if candidate {candidate_index} should be hired.

    Optimal solution for variation of problem where we only care about hiring the best
    possible candidate (i.e. hiring the second-best is considered a failure).

    :param candidate_index: int - candidate's position in list of candidates
    :param score: int|float - number representing candidate quality
    :param num_candidates: int - total candidates
    :return: bool
    """
    global best_score
    num_test_candidates = num_candidates / math.e

    if score > best_score:
        best_score = score
        if candidate_index >= num_test_candidates:
            return True

    if candidate_index == num_candidates - 1:
        return True

    return False


def _assess_hired_candidate(number_list, number):
    """
    Return 1 if best possible candidate was hired, else 0.

    :param number_list: int[] | float[]
    :param number: int | float
    :return: int
    """
    if max(number_list) == number:
        return 1
    return 0


def hire_candidate(candidates_list):
    """
    Simulates the "hiring problem" where the goal is to hire the best possible candidate.

    Candidates and their objective "quality" scores are represented by a list of numbers.
    The catch is that only one candidate may be considered at a time: you must make an
    offer immediately after meeting (and scoring) a candidate. In this variation, we
    only care about hiring the candidate with the highest score. Hiring any other
    candidate is considered a failure.

    :param candidates_list: int[]|float[] - list of candidate "quality scores"
    :return: int - 1 or 0 whether best possible candidate was hired
    """
    global best_score
    best_score = float('-inf')

    for index, score in enumerate(candidates_list):
        is_hired = _should_hire_candidate(index, score, len(candidates_list))
        if is_hired:
            return _assess_hired_candidate(candidates_list, score)

    raise Exception('Failed to hire a candidate!')


class Test(object):

    def _generate_random_scores(self, num_candidates):
        multiplier = randint(0, 99)
        scores_list = [i for i in xrange(num_candidates)]
        scores_list = map(lambda x: x * multiplier, scores_list)
        randomize_list_in_place(scores_list)
        return randomize_list_in_place([i for i in xrange(num_candidates)])

    def test_should_hire_candidate(self):
        num_trials = 10000
        results = []

        for trial in xrange(num_trials):
            candidates_list = self._generate_random_scores(100)
            result = hire_candidate(candidates_list)
            results.append(result)

        # the best candidate will be hired more than 1/3 of the time
        average_score = sum(results) / float(num_trials)
        assert average_score > float(1) / 3
