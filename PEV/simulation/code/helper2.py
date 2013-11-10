#!/usr/bin/python3

from subprocess import call
import random
from threading import Thread
import multiprocessing

file = '/media/data/workspace/github_repos/materials-rennes/PEV/simulation/code/simulation.py'
nc = '1000'

lambds_10 = ['10']
muis_10 = ['10','10','10','10', '10']
queue_sizes_10 = ['1000','1000','10', '1000', '10']

args_10 = [lambds_10, muis_10, queue_sizes_10]

lambds_40 = ['40']
muis_40 = ['40','40','40','40', '40']
queue_sizes_40 = ['1000','1000','40', '1000', '40']

args_40 = [lambds_40, muis_40, queue_sizes_40]


def generate_value(index):
  return str(index + 1)
  #return random.randint(1, 100)

def generic_alternator(args, index_arg, index_element, index, name):
  new_arg = args[index_arg].copy()
  new_arg[index_element] = generate_value(index)
  new_args = args.copy()
  new_args[index_arg] = new_arg
  graph = 'graph2_hard'

  result = ['-lambdas', ','.join(new_args[0]), '-muis', ','.join(new_args[1]),
      '-queue-sizes', ','.join(new_args[2]), '-graph', '/tmp/{0}.in'.format(graph),
      '-output-file', '/tmp/{0}/out_{1}.txt'.format(graph, name)]

  return result

def queue_sizes_alternator_10_50v50(index):
  name = 'queue_sizes_alternator_10_50v50'

  return generic_alternator(args_10, 2, 2, index, name)

def queue_sizes_alternator_40_50v50(index):
  name = 'queue_sizes_alternator_40_50v50'

  return generic_alternator(args_40, 2, 2, index, name)

def queue_sizes_2_alternator_10_50v50(index):
  name = 'queue_sizes_2_alternator_10_50v50'

  return generic_alternator(args_10, 2, 4, index, name)

def queue_sizes_2_alternator_40_50v50(index):
  name = 'queue_sizes_2_alternator_40_50v50'

  return generic_alternator(args_40, 2, 4, index, name)

def muis1_alternator_10_50v50(index):
  name = 'muis1_alternator_10_50v50'

  return generic_alternator(args_10, 1, 0, index, name)

def muis1_alternator_40_50v50(index):
  name = 'muis1_alternator_40_50v50'

  return generic_alternator(args_40, 1, 0, index, name)

def muis2_alternator_10_50v50(index):
  name = 'muis2_alternator_10_50v50'

  return generic_alternator(args_10, 1, 1, index, name)

def muis2_alternator_40_50v50(index):
  name = 'muis2_alternator_40_50v50'

  return generic_alternator(args_40, 1, 1, index, name)

def muis3_alternator_10_50v50(index):
  name = 'muis3_alternator_10_50v50'

  return generic_alternator(args_10, 1, 2, index, name)

def muis3_alternator_40_50v50(index):
  name = 'muis3_alternator_40_50v50'

  return generic_alternator(args_40, 1, 2, index, name)

def muis4_alternator_10_50v50(index):
  name = 'muis4_alternator_10_50v50'

  return generic_alternator(args_10, 1, 3, index, name)

def muis4_alternator_40_50v50(index):
  name = 'muis4_alternator_40_50v50'

  return generic_alternator(args_40, 1, 3, index, name)

def muis5_alternator_10_50v50(index):
  name = 'muis5_alternator_10_50v50'

  return generic_alternator(args_10, 1, 4, index, name)

def muis5_alternator_40_50v50(index):
  name = 'muis5_alternator_40_50v50'

  return generic_alternator(args_40, 1, 4, index, name)

def lambds1_alternator_10_50v50(index):
  name = 'lambds1_alternator_10_50v50'

  return generic_alternator(args_10, 0, 0, index, name)

def lambds1_alternator_40_50v50(index):
  name = 'lambds1_alternator_40_50v50'

  return generic_alternator(args_40, 0, 0, index, name)

def rand_list(start, end, count):
  return [str(random.randint(start, end)) for _ in range(count)]

def threaded_calculation(thread_index, count, args_generators):
  count_of_runs = 100
  for args_generator in args_generators[thread_index::count]:
    for run_index in range(count_of_runs):
      args = args_generator(run_index)
      call(['python3', file, '--no-gui', '-nc', nc] + args)

if __name__ == '__main__':
  cpus_count = multiprocessing.cpu_count()
  threads = []

  args_generators = [lambds1_alternator_10_50v50, lambds1_alternator_40_50v50,
      muis1_alternator_10_50v50, muis1_alternator_40_50v50,
      muis2_alternator_10_50v50, muis2_alternator_40_50v50,
      muis3_alternator_10_50v50, muis3_alternator_40_50v50,
      muis4_alternator_10_50v50, muis4_alternator_40_50v50,
      muis5_alternator_10_50v50, muis5_alternator_40_50v50,
      queue_sizes_alternator_10_50v50, queue_sizes_alternator_40_50v50,
      queue_sizes_2_alternator_10_50v50, queue_sizes_2_alternator_40_50v50,]

  for index in range(cpus_count):
    thread = Thread(target = threaded_calculation,
        args = (index, cpus_count, args_generators, ))
    thread.start()
    threads.append(thread)

  for thread in threads:
    thread.join()

