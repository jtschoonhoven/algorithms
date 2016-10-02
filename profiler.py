import argparse
from collections import namedtuple
import imp
import Queue
import random
import threading
import trace
import os


"""
Algorithm profiler: measure how runtime complexity varies with size of input.

CAUTION: counts lines of executed code, NOT actual number of computations.
Comprehensions and builtin functions will count as a single statement.
"""


NUM_THREADS = 20
DEFAULT_NUM_RUNS = 100
DEFAULT_STEP_SIZE = 1  # increase input length by this amount each run

# labels used in metrics and charts
INPUT_MEASURE_NAME = 'input_size'
COMPLEXITY_MEASURE_NAME = 'num_executed_statements'
CASE_NAME = 'case'

ProfileResult = namedtuple('ProfileResult', [INPUT_MEASURE_NAME, COMPLEXITY_MEASURE_NAME])


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


def get_int_list(length, sort_order='random'):
    """
    Return a list of all integers, 0-{length - 1}, ordered randomly.

    :param length: int
    :param sort_order: str - ["random"|"ascending"|"descending"]
    :return: int[]
    """
    assert sort_order in ('random', 'ascending', 'descending')

    int_list = range(length)
    if sort_order == 'random':
        random.shuffle(int_list)
    elif sort_order == 'descending':
        int_list.reverse()

    return int_list


def profile_results_to_dataframe(**kwargs):
    """
    Convert profile results to dataframe for plotting.

    :param profile_results: ProfileResult[]
    :return: pandas.DataFrame
    """
    # pandas is a big slow mess: only import it if necessary
    import pandas as pd

    merged_dataframe = pd.DataFrame()
    for profile_type, profile_results in kwargs.iteritems():
        df = pd.DataFrame(profile_results)
        df[CASE_NAME] = profile_type
        merged_dataframe = merged_dataframe.append(df)

    return merged_dataframe


def plot(result_dataframe, title=None, save_path=None, **kwargs):
    """
    Plot results and save to .png.

    :param path: str - path and filename to save image to, should end in ".png"
    :param result_dataframe: pandas.DataFrame
    :return: ggplot.ggplot
    """
    import matplotlib
    # http://stackoverflow.com/a/39539491/3076390
    matplotlib.rcParams['backend'] = 'Agg'
    import ggplot

    plot = ggplot.ggplot(result_dataframe, ggplot.aes(**kwargs))
    plot + ggplot.geom_line(size=3)
    plot + ggplot.scale_y_continuous()
    plot + ggplot.scale_color_manual(values=['teal', 'MediumAquaMarine', 'coral'])

    if save_path:
        plot.save(save_path)

    return plot


def _profile_worker(func, input_size_queue, result_queue, sort_order):
    """
    Profile a function and put ProfileResults to result_queue. Run from a child thread.

    Continues to call function for different input sizes until input_size_queue is empty.

    :param input_size_queue: Queue.Queue - queue of integers of input size
    :param result_queue: Queue.Queue - empty queue to put ProfileResults to
    :param sort_order: str - ["random"|"ascending"|"descending"]
    """
    while True:
        try:
            input_size = input_size_queue.get(block=False)
            func_args = get_int_list(input_size, sort_order)
            trace_result = trace_function(func, func_args)
            num_executed = num_executed_statements(trace_result)
            profile_result = ProfileResult(input_size, num_executed)
            result_queue.put(profile_result)
        except Queue.Empty:
            break


def profile(func, num_runs, step, sort_order):
    """
    Call function {num_run} times with input that increases by len {step} each run.

    Calls with random, ascending, or descending input depending on sort_order.

    :param func: function
    :param num_runs: int
    :param sort_order: str - ["random"|"ascending"|"descending"]
    :return: ProfileResult[]
    """
    threads = []
    results = []
    input_size_queue = Queue.Queue()
    result_queue = Queue.Queue()

    # populate input_size_queue with input lengths to profile for
    for run in xrange(1, num_runs + 1):
        input_size = run * step
        input_size_queue.put(input_size)

    # start {NUM_THREADS} profile workers
    for _ in xrange(NUM_THREADS):
        thread = threading.Thread(
            target=_profile_worker,
            args=[func, input_size_queue, result_queue, sort_order])
        thread.start()
        threads.append(thread)

    # wait for threads to finish
    for thread in threads:
        thread.join()

    # pull ProfileResults from result_queue and put to list until queue is empty
    while True:
        try:
            result = result_queue.get(block=False)
            results.append(result)
        except Queue.Empty:
            break

    return sorted(results)


def profile_and_plot(func, num_runs=None, step=None, title=None, save_path=None):
    """
    Shortcut function to profile {func} and plot results.

    :param func: function - must accept an integer list as only argument
    :param num_runs: int
    :param step: int
    :param title: str
    :param save_path: str - if present, plot will be saved to this path
    :return: None
    """
    results = {
        'best_case': profile(func, num_runs, step, 'ascending'),
        'worst_case': profile(func, num_runs, step, 'descending'),
        'random': profile(func, num_runs, step, 'random'),
    }

    result_dataframe = profile_results_to_dataframe(**results)
    mapping = {
        'x': INPUT_MEASURE_NAME,
        'y': COMPLEXITY_MEASURE_NAME,
        'color': CASE_NAME,
    }

    chart = plot(result_dataframe, title=title, save_path=save_path, **mapping)

    if save_path:
        print 'plot saved to {}'.format(save_path)
    else:
        print chart


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
    profile_and_plot(func, args.num_runs, args.step, args.module, save_path)
