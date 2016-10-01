import argparse
from collections import namedtuple
import imp
import Queue
import random
import threading
import trace
import os


"""
Algorithm profiler: measure how complexity depends on size of input.
"""


ProfileResult = namedtuple('ProfileResult', ['size', 'num_executed_statements'])

NUM_THREADS = 20
DEFAULT_NUM_RUNS = 100
DEFAULT_STEP_SIZE = 1  # increase input length by this amount each run


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


def plot(result_dataframe, path=None):
    """
    Plot results and save to .png.

    :param path: str - path and filename to save image to, should end in ".png"
    :param result_dataframe: pandas.DataFrame
    :return: None
    """
    import matplotlib
    # http://stackoverflow.com/a/39539491/3076390
    matplotlib.use('Agg')
    import ggplot

    path = path or './plot.png'
    colnames = result_dataframe.columns.values

    plot = ggplot.ggplot(result_dataframe, ggplot.aes(x=colnames[0], y=colnames[1]))
    plot + ggplot.geom_area()
    plot.save(path)


def _profile_worker(input_size_queue, result_queue):
    """
    Profile a function and put ProfileResults to result_queue. Run from a child thread.

    Continues to call function for different input sizes until input_size_queue is empty.

    :param input_size_queue: Queue.Queue - queue of integers of input size
    :param result_queue: Queue.Queue - empty queue to put ProfileResults to
    """
    while True:
        try:
            input_size = input_size_queue.get(block=False)
            func_args = get_random_int_list(input_size)
            trace_result = trace_function(func, func_args)
            num_executed = num_executed_statements(trace_result)
            profile_result = ProfileResult(input_size, num_executed)
            result_queue.put(profile_result)
        except Queue.Empty:
            break


def profile(func, num_runs, step):
    """
    Call function {num_run} times with input that increases by len {step} each run.

    :param func: function
    :param num_runs: int
    """
    threads = []
    results = []
    input_size_queue = Queue.Queue()
    result_queue = Queue.Queue()

    for run in xrange(1, num_runs + 1):
        input_size = run * step
        input_size_queue.put(input_size)

    for _ in xrange(NUM_THREADS):
        thread = threading.Thread(
            target=_profile_worker, args=[input_size_queue, result_queue])
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    while True:
        try:
            result = result_queue.get(block=False)
            results.append(result)
        except Queue.Empty:
            break

    return sorted(results)


if __name__ == '__main__':
    input_choices = ('random_int_list',)
    parser = argparse.ArgumentParser(description='Profile {function} in {module}.')
    parser.add_argument(
        'module',
        help='name of module to import')
    parser.add_argument(
        '--function', '-f',
        help='name of function to profile, if not same as module')
    parser.add_argument(
        '--path', '-p',
        help='path to directory of module, if not same as script')
    parser.add_argument(
        '--num_runs', '-n',
        type=int,
        default=DEFAULT_NUM_RUNS,
        help='run profiler {n} times')
    parser.add_argument(
        '--step', '-s',
        type=int,
        default=DEFAULT_STEP_SIZE,
        help='increase input size by {s} each run')
    args = parser.parse_args()

    save_path = args.module + '.png'
    func = _get_function_from_module(args.module, args.function)
    profile_results = profile(func, args.num_runs, args.step)
    result_dataframe = profile_results_to_dataframe(profile_results)
    plot(result_dataframe, save_path)

    print result_dataframe
    print 'plot saved to {}'.format(save_path)
