#!/usr/bin/python3

from subprocess import call
import random

file = '/media/data/workspace/github_repos/materials-rennes/PEV/simulation/code/simulation.py'
nc = '1000'
lambds = ['10']
muis = ['10','10','10','10']
queue_sizes = ['1000','1000','10','1000']

def rand_list(start, end, count):
  return [str(random.randint(start, end)) for _ in range(count)]

for _ in range(100):
  #lambds = rand_list(1, 100, 1)
  #muis = rand_list(1, 100, 4)
  muis[0] = str(_ * 0.5 + 0.1)  #str(random.randint(1, 100))
  #queue_sizes[2] = str(random.randint(1, 40))
  call(['python3', file, '--no-gui', '-nc', nc, '-lambdas', ','.join(lambds), 
    '-muis', ','.join(muis), '-queue-sizes', ','.join(queue_sizes),
    '-graph', '/tmp/graph2.in', '-output-file', '/tmp/out_mui1_step05_10_50v50.out'])
