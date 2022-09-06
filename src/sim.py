import simpy
import random

from belt import Belt
from part import Part
from worker import Worker

from const import sim_time, belt_size, worker_positions, complete_part, complete_delay, part_types

def factory(env):
    # initial setup
    belt = Belt(belt_size)
    workers = {}
    workers_bottom = []
    complete_parts = 0
    waste_parts = 0
    total_parts = 0

    # setup workers
    for worker_pos in worker_positions:
        workers[worker_pos] = []
        for belt_pos in range(0, belt_size):
            worker = Worker(
                pos=belt_pos,
                side=worker_pos,
                complete_part=complete_part,
                complete_delay=complete_delay
            )
            workers[worker_pos].insert(belt_pos, worker)

    # simulation loop
    while True:
        # loop over belt and worker positions to check items
        print('TIME: {}'.format(env.now))
        for worker_pos in worker_positions:
            for belt_pos, worker in enumerate(workers[worker_pos]):
                item = belt.peek(belt_pos)
                print('--- Position: {}, Worker: {}, Part: {}'.format(belt_pos, worker_pos, item.peek()))
                print('--- REQUIRED PART: {}'.format(worker.required_part(item)))

                if not belt.in_use(belt_pos, env.now):

                    # if the item is needed and added to the workers hand
                    if worker.required_part(item=item) and not worker.complete_hand():
                        # pick the item off the belt
                        print('   --- PICKING PART')
                        picked_item = belt.pick(belt_pos, env.now)
                        worker.add_hand(item=picked_item, time=env.now)
                    
                    print('   --- Belt in use: {}'.format(belt.in_use(belt_pos, env.now)))
                    print('   --- Workers hand: {}'.format(str(worker)))
                    print('   --- Complete hand: {}'.format(worker.complete_hand()))
                    print('   --- Complete time: {}'.format(worker.complete_time))

                    # if the worker has a complete part
                    if worker.complete_hand() and (not worker.complete_time or env.now >= worker.complete_time):
                        if item.peek() == None:
                            print('   --- COMPLETE PART!!!')
                            placed_item = worker.place()
                            belt.place(idx=belt_pos, time=env.now, item=placed_item)

        # add new item to belt and get last one off
        new_part_type = random.choice(part_types + [None])
        if new_part_type != None:
            total_parts += 1
        last = belt.add(Part(new_part_type))

        if last.complete:
            complete_parts += 1
        elif last.peek() != None:
            waste_parts += 1

        print('TOTAL PARTS: {}'.format(total_parts))
        print('COMPLETE PARTS: {}'.format(complete_parts))
        print('WASTE PARTS: {}'.format(waste_parts))

        yield env.timeout(1)

env = simpy.Environment()
env.process(factory(env))
env.run(until=sim_time)
