import logging
import argparse
from collections import namedtuple
import imp
import random
import trace
import os


"""
Algorithm profiler: measure how complexity depends on size of input.
"""

ProfileResult = namedtuple('ProfileResult', ['size', 'num_executed_statements'])


def _get_function_from_module(module_name, function_name=None, dir_path=None):
    """
    Dynamically import {module_name} and return module.{function_name}.

    If not specified, {function_name} is assumed to be the same as the module_name and
    {dir_path} is assumed to be the same as for this script.

    :param module_name: str - name of module to import
    :param function_name: str - name of func to import from module
    :dir_path: str - path to directory containing module
    """
    function_name = function_name or module_name
    dir_path = dir_path or os.path.dirname(os.path.realpath(__file__))

    try:
        # pyc files are compiled when the source script is called but NOT when imported:
        # make sure to run the module manually to save changes in the source to .pyc
        filepath = os.path.join(dir_path, module_name) + '.pyc'
        module = imp.load_compiled(module_name, filepath)
    except (ImportError, IOError):
        filepath = os.path.join(dir_path, module_name) + '.py'
        module = imp.load_source(module_name, filepath)

    return getattr(module, function_name)


def trace_function(func, *args, **kwargs):
    """
    :return: trace.CoverageResults
    """
    tracer = trace.Trace(trace=False)
    tracer.runfunc(func, *args, **kwargs)
    trace_result = tracer.results()

    return trace_result


def num_executed_statements(trace_result):
    """
    Given an instance of trace.CoverageResults, return the sum of executed statements.

    :param trace_result: trace.CoverageResults
    :return: int
    """
    return sum(x for x in trace_result.counts.values())


def get_random_int_list(length):
    """
    Return a list of all integers, 0-{length - 1}, ordered randomly.

    :param length: int
    :return: int[]
    """
    int_list = range(length)
    random.shuffle(int_list)

    return int_list


def profile_results_to_dataframe(profile_results):
    """
    Convert profile results to 2-column dataframe for plotting.

    :param profile_results: ProfileResult[]
    :return: pandas.DataFrame
    """
    # pandas is a big slow mess: only import it if necessary
    import pandas
    return pandas.DataFrame(profile_results)


def profile(func, num_runs=None, step=None):
    profile_results = []

    for run in xrange(1, num_runs + 1):
        input_size = run * step
        func_args = get_random_int_list(input_size)
        trace_result = trace_function(func, func_args)
        profile_result = ProfileResult(input_size, num_executed_statements(trace_result))
        profile_results.append(profile_result)

    return profile_results


if __name__ == '__main__':
    input_choices = ('random_int_list',)
    parser = argparse.ArgumentParser(description='Profile {function} in {module}.')
    parser.add_argument(
        'module', help='name of module to import')
    parser.add_argument(
        '--function', '-f', help='name of function to profile, if not same as module')
    parser.add_argument(
        '--path', '-p', help='path to directory of module, if not same as script')
    parser.add_argument(
        '--num_runs', '-n', type=int, default=10, help='run profiler {n} times')
    parser.add_argument(
        '--step', '-s', type=int, default=10, help='increase input size by {s} for run')
    args = parser.parse_args()

    func = _get_function_from_module(args.module, args.function)
    profile_results = profile(func, num_runs=args.num_runs, step=args.step)
    print profile_results_to_dataframe(profile_results)
