#!/usr/bin/python3
import sys
import random
import heapq

class Configuration: 
  def __init__(self, number_of_clients, lambds, muis,
      queue_sizes, graph_filename, output_file, repetitions):
    self.number_of_clients = number_of_clients
    self.lambds = lambds
    self.muis = muis
    self.queue_sizes = queue_sizes
    self.output_file = output_file
    self.init_graph(graph_filename)
    self.repetitions = repetitions

  def init_graph(self, filename):
    with open(filename, 'r') as file:
      lines = file.readlines()
      lines = [_ for _ in lines if _[0] != '#']

      self.number_of_servers = int(lines[0])
      self.input_servers = [int(_) for _ in lines[1].split(' ')]
      output_servers = [int(_) for _ in lines[2].split(' ')]
      self.graph = [[] for _ in range(self.number_of_servers)]

      for _ in lines[3:]:
        numbers = _.split(' ')
        start, end, probability = (int(numbers[0]), int(numbers[1]),
            float(numbers[2]))
        self.graph[start].append((end, probability))

      for _ in output_servers:
        self.graph[_].append((self.number_of_servers, 1))

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

class RunStatistics:
  def __init__(self, n):
    self.wait_times = [0.0 for _ in range(n)]
    self.losses = [0.0 for _ in range(n + 1)]
    self.response_times = [0.0 for _ in range(n)]
    
  def merge(self, other, merger=float.__add__):
    self.wait_times = [merger(*_)
        for _ in zip(self.wait_times, other.wait_times)]
    self.losses = [merger(*_) for _ in zip(self.losses, other.losses)]
    self.response_times = [merger(*_)
        for _ in zip(self.response_times, other.response_times)]

  def normalize(self, runs):
    final_wait_times = [_ / runs for _ in self.wait_times]
    final_losses = [_ / runs for _ in self.losses]
    final_response_times = [_ / runs for _ in self.response_times]

    return (final_wait_times, final_losses, final_response_times)
      

def get_exponentially_distributed_value(l):
  return random.expovariate(l)

def get_input_times(number_of_clients, l):
  result = [get_exponentially_distributed_value(l)
      for client in range(number_of_clients)]

  return [result[0]] + [result[index - 1] + result[index]
      for index in range(1, number_of_clients)]

def correct_dest_error(dest, config, elements_in_queue):
    if dest == config.number_of_servers:
      return -(config.number_of_servers)
    if elements_in_queue[dest] < config.queue_sizes[dest]:
      return dest
    else:
      return -dest

def calculate_destination_server(source, config, elements_in_queue):
  graph = config.graph
  number_of_servers = config.number_of_servers
  possible_dests = [_[0] for _ in graph[source]]

  if len(possible_dests) == 1:
    return correct_dest_error(possible_dests[0], config, elements_in_queue)
  else:
    dests_probabilities = [_[1] for _ in graph[source]]
    probability_ranges = [dests_probabilities[0]] + [
        dests_probabilities[index] + dests_probabilities[index - 1] for index in
          range(1, len(dests_probabilities))]
    rand_value = random.random()

    for index in range(len(dests_probabilities)):
      if rand_value < probability_ranges[index]:
        dest = possible_dests[index]

        return correct_dest_error(dest, config, elements_in_queue)

    return -(number_of_servers)

def process_next_event(queue, config, times, elements_in_queue, statistics):
  next_event = queue.pop()

  if next_event._type == 0:
    elements_in_queue[next_event._on_server] += 1

    new_event = serve(next_event, config.muis, times, statistics.wait_times,
        statistics.response_times)
    times[next_event._on_server] = new_event._time

    queue.push(new_event)
  else:
    elements_in_queue[next_event._on_server] -= 1
    dest = calculate_destination_server(next_event._on_server, config,
        elements_in_queue)

    if dest >= 0:
      new_event = Event(next_event._time, 0, dest)

      queue.push(new_event)
    else: 
      statistics.losses[-dest] += 1

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

  number_of_clients = int(args_hash['-nc'])
  queue_sizes = [int(_) for _ in args_hash['-queue-sizes'].split(',')]
  muis = [float(_) for _ in args_hash['-muis'].split(',')]
  lambds = [int(_) for _ in args_hash['-lambdas'].split(',')]
  graph_filename = args_hash['-graph']
  output_file = args_hash.get('-output-file', None)
  repetitions = int(args_hash.get('-repetitions', 100))

  return Configuration(number_of_clients, lambds, muis, queue_sizes,
      graph_filename, output_file, repetitions)

def get_configuration(): 
  if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
    return parse_cmd_args(sys.argv[2:])

def square_merger(a, b):
  return a + b * b

def run_simulation(config):
  final_statistics = RunStatistics(config.number_of_servers)
  squared_final_statistics = RunStatistics(config.number_of_servers)

  repetitions = config.repetitions

  for _ in range(repetitions):
    queue = PriorityQueue([Event(_, 0, 0)
      for _ in get_input_times(config.number_of_clients, config.lambds[0])])
    times = [0 for _ in range(config.number_of_servers)]
    elements_in_queue = [0 for _ in range(config.number_of_servers)]
    statistics = RunStatistics(config.number_of_servers)

    while(not queue.empty()):
      process_next_event(queue, config, times, elements_in_queue, statistics)

    final_statistics.merge(statistics)
    squared_final_statistics.merge(statistics, square_merger)

  final_data = final_statistics.normalize(repetitions)
  final_wait_times, final_losses, final_response_times = final_data

  output_results(config, final_losses, final_wait_times, final_response_times)

  print_all_statistics(final_statistics, squared_final_statistics, repetitions)

def calculate_confidence_intervals(value, squared_value, n):
  coefficient = 1.64
  variance = ((squared_value - n * value * value) / (n - 1)) ** 0.5
  deviation = coefficient * variance / (n ** 0.5)

  return (value - deviation, value + deviation)

def print_statistic(repetitions, data, squared_data, name):
  message_template = (
      "{0} for server {1} is in the interval ({2:.4f}, {3:.4f})" +
      " with confidence 90%")
  for _ in range(len(data)):
    interval = calculate_confidence_intervals(data[_], squared_data[_],
        repetitions)

    print(message_template.format(name, _, *interval))

def print_all_statistics(statistics, squared_statistics, repetitions):
  data = statistics.normalize(repetitions)
  wait_times, losses, response_times = data

  squared_data = squared_statistics.normalize(1)
  squared_wait_times, squared_losses, squared_response_times = squared_data

  print_statistic(repetitions, losses[:-1], squared_losses[:-1], "Loses")

  interval = calculate_confidence_intervals(losses[-1], squared_losses[-1], 
      repetitions)
  print("Passed through the whole system are in ({:.4f}, {:.4f}) with confidence 90%".
      format(*interval))

  print_statistic(repetitions, wait_times, squared_wait_times, "Wait times")
  print_statistic(repetitions, response_times, squared_response_times,
      "Response times")

def format_list(l):
  return ', '.join([str(_) for _ in l])

def output_results(config, losses, wait_times, response_times):
  if config.output_file == None:
    return

  result = ', '.join([str(config.number_of_clients),
    format_list(config.lambds), format_list(config.muis), format_list(losses), 
    format_list(wait_times), format_list(response_times), 
    format_list(config.queue_sizes)])

  with open(config.output_file, 'a') as file:
    file.writelines([result + '\n'])

if __name__ == '__main__':
  config = get_configuration()
  run_simulation(config)
