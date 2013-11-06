#!/usr/bin/python3
import sys
import random
import heapq

class Configuration: 
  def __init__(self, number_of_clients, number_of_servers, lambds, muis,
      queue_sizes, input_servers, output_servers):
    self.number_of_clients = number_of_clients
    self.number_of_servers = number_of_servers
    self.lambds = lambds
    self.muis = muis
    self.queue_sizes = queue_sizes
    self.input_servers = input_servers
    self.output_servers = output_servers

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
    return "<Event(time={0})>".format(self._time)

  def __repr__(self):
    return self.__str__()

class PriorityQueue:
  def __init__(self, initial_values = []): 
    self.heap = initial_values.copy()
    heapq.heapify(self.heap)

  def merge(self, iterable):
    self.heap = list(heapq.merge(self.heap, iterable))
    print(self.heap)
    heapq.heapify(self.heap)
    print(self.heap)

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

def calculate_destination_server(source, elements_in_queue):
  if source == 0:
    if random.random() < 0.4:
      return 1
    else:
      return 2
  if source == 1:
    return 3
  if source == 2:
    if elements_in_queue[3] < 20:
      return 3
    else:
      return -1

  return -1

def process_next_event(queue, muis, times, elements_in_queue):
  next_event = queue.pop()

  if next_event._type == 0:
    elements_in_queue[next_event._on_server] += 1

    new_event = serve(next_event, muis)
    times[next_event._on_server] = new_event._time

    queue.push(new_event)
  else:
    elements_in_queue[next_event._on_server] -= 1
    dest = calculate_destination_server(next_event._on_server, 
        elements_in_queue)

    new_event = Event(next_event._time, 0, dest)
    if new_event._on_server >= 0:
      queue.push(new_event)

def serve(event, muis, times): 
  mui = muis[event._on_server]
  serve_time= get_exponentially_distributed_value(mui)
  service_start_time = max(event._time, times[event._on_server])

  return Event(service_start_time + serve_time, 1, event._on_server)

def parse_cmd_args(args):
  number_of_clients = 10
  return Configuration(number_of_clients, 4, [2], [4, 4, 4, 4],
      [number_of_clients + 1, number_of_clients + 1, 20, number_of_clients + 1],
      [0], [3])

def get_configuration(): 
  if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
    return parse_cmd_args(sys.argv[2:])
  else:
    return None

def run_simulation(config):
  queue = PriorityQueue([Event(_, 0, 0)
    for _ in get_input_times(config.number_of_clients, config.lambds[0])])
  while(not queue.empty()):
    process_next_event(queue, config.muis, [0, 0, 0, 0], [0, 0, 0, 0])

  print("Some results")

if __name__ == '__main__':
  config = get_configuration()
  run_simulation(config)
