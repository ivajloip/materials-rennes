#!/usr/bin/python3
import sys
import random
import heapq

class Configuration: 
  def __init__(self, number_of_clients, lambds, muis,
      queue_sizes, graph_filename, output_file):
    self.number_of_clients = number_of_clients
    self.lambds = lambds
    self.muis = muis
    self.queue_sizes = queue_sizes
    self.graph_filename = graph_filename
    self.output_file = output_file

class Event:
  def __init__(self, time, event_type=0, on_server = None):
    self._time = time
    self._on_server = on_server
    self._type = event_type

  def __eq__(self, other):
    return self._time == other._time

  def __lt__(self, other):
    return self._time < other._time

  def __le__(self, other):
    return self._time <= other._time

  def __str__(self):
    return "<Event(time={0}, type={1}, server={2})>".format(self._time,
        self._type, self._on_server)

  def __repr__(self):
    return self.__str__()

class PriorityQueue:
  def __init__(self, initial_values = []): 
    self.heap = initial_values.copy()
    heapq.heapify(self.heap)

  def merge(self, iterable):
    self.heap = list(heapq.merge(self.heap, iterable))
    heapq.heapify(self.heap)

  def pop(self):
    return heapq.heappop(self.heap)

  def top(self):
    return heapq.nsmallest(1, self.heap)[0]

  def push(self, value):
    heapq.heappush(self.heap, value)

  def empty(self):
    return len(self.heap) == 0


def get_exponentially_distributed_value(l):
  return random.expovariate(l)

def get_input_times(number_of_clients, l):
  result = [get_exponentially_distributed_value(l)
      for client in range(number_of_clients)]

  return [result[0]] + [result[index - 1] + result[index]
      for index in range(1, number_of_clients)]

def calculate_destination_server(source, graph, config, output_servers,
    elements_in_queue):
  possible_dests = [_[0] for _ in graph[source]]

  if len(possible_dests) == 1:
    dest = possible_dests[0]
    if dest == len(graph):
      return -(len(elements_in_queue))
    if elements_in_queue[dest] < config.queue_sizes[dest]:
      return dest
    else:
      return -dest
  else:
    dests_probabilities = [_[1] for _ in graph[source]]
    rand_value = random.random()
    probability_ranges = [dests_probabilities[0]] + [
        dests_probabilities[index] + dests_probabilities[index - 1] for index in
          range(1, len(dests_probabilities))]

    for index in range(len(dests_probabilities)):
      if rand_value < probability_ranges[index]:
        dest = possible_dests[index]
        if dest == len(graph):
          return -(len(elements_in_queue))
        if elements_in_queue[dest] < config.queue_sizes[dest]:
          return dest
        else:
          return -dest

    return -(len(elements_in_queue))

def process_next_event(queue, config, graph, times, elements_in_queue, losses,
    wait_times, response_times, output_servers):
  next_event = queue.pop()

  if next_event._type == 0:
    elements_in_queue[next_event._on_server] += 1

    new_event = serve(next_event, config.muis, times, wait_times,
        response_times)
    times[next_event._on_server] = new_event._time

    queue.push(new_event)
  else:
    elements_in_queue[next_event._on_server] -= 1
    dest = calculate_destination_server(next_event._on_server, 
        graph, config, output_servers, elements_in_queue)

    if dest >= 0:
      new_event = Event(next_event._time, 0, dest)

      queue.push(new_event)
    else: 
      losses[-dest] += 1

def serve(event, muis, times, wait_times, response_times): 
  mui = muis[event._on_server]
  serve_time = get_exponentially_distributed_value(mui)

  service_start_time = max(event._time, times[event._on_server])

  new_event = Event(service_start_time + serve_time, 1, event._on_server)

  wait_time = -(event._time - service_start_time)
  wait_times[event._on_server] += wait_time
  response_times[event._on_server] += serve_time

  return new_event

def parse_cmd_args(raw_args):
  args_hash = {_[0] : _[1] for _ in zip(raw_args[::2], raw_args[1::2])}

  print(args_hash)

  number_of_clients = int(args_hash['-nc'])
  queue_sizes = [int(_) for _ in args_hash['-queue-sizes'].split(',')]
  muis = [int(_) for _ in args_hash['-muis'].split(',')]
  lambds = [int(_) for _ in args_hash['-lambdas'].split(',')]
  graph_filename = args_hash['-graph']
  output_file = args_hash['-output-file']

  return Configuration(number_of_clients, lambds, muis, queue_sizes,
      graph_filename, output_file)
  
  #return Configuration(, [2], [4, 4, 4, 4],
  #    [number_of_clients + 1, number_of_clients + 1, 10, number_of_clients + 1],
  #    'graph1.in')
  #
  #return Configuration(1000, [1], [20, 10, 20, 2],
  #  [1000000, 1000000, 20, 100000], 'graph1.in')

def get_configuration(): 
  if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
    return parse_cmd_args(sys.argv[2:])
  else:
    return None

def run_simulation(config):
  queue = PriorityQueue([Event(_, 0, 0)
    for _ in get_input_times(config.number_of_clients, config.lambds[0])])
  times = [0, 0, 0, 0]
  elements_in_queue = [0, 0, 0, 0]
  losses = [0, 0, 0, 0, 0]
  wait_times = [0, 0, 0, 0]
  response_times = [0, 0, 0, 0]
  graph, input_servers, output_servers, n = read_graph(config.graph_filename)

  while(not queue.empty()):
    process_next_event(queue, config, graph, times, elements_in_queue, losses,
        wait_times, response_times, output_servers)

  print("Losses {0}".format(losses))
  print("Wait times {0}".format(wait_times))
  print("response_times {0}".format(response_times))

  output_results(config, losses, wait_times, response_times)

def format_list(l):
  return ', '.join([str(_) for _ in l])

def output_results(config, losses, wait_times, response_times):
  result = ', '.join([str(config.number_of_clients),
    format_list(config.lambds), format_list(config.muis), format_list(losses), 
    format_list(wait_times), format_list(response_times)])

  with open(config.output_file, 'a') as file:
    file.writelines([result + '\n'])

def read_graph(filename):
  with open(filename, 'r') as file:
    lines = file.readlines()
    lines = [_ for _ in lines if _[0] != '#']

    n = int(lines[0])
    input_servers = [int(_) for _ in lines[1].split(' ')]
    output_servers = [int(_) for _ in lines[2].split(' ')]
    graph = [[] for _ in range(n)]

    for _ in lines[3:]:
      numbers = _.split(' ')
      start, end, probability = int(numbers[0]), int(numbers[1]), float(numbers[2])
      graph[start].append((end, probability))

    for _ in output_servers:
      graph[_].append((n, 1))

    return (graph, input_servers, output_servers, n)

if __name__ == '__main__':
  config = get_configuration()
  run_simulation(config)
