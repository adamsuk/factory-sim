from part import Part

from const import complete_part

class Worker:
    def __init__(self, pos, side, complete_part=[], complete_delay=4):
        self.pos = pos
        self.side = side
        self.complete_part = complete_part
        self.complete_part.sort()
        self.hand = []
        self.complete_time = None
        self.complete_delay = complete_delay
    
    def __str__(self):
        hand_part_types = [i.peek() for i in self.hand]
        hand_part_types.sort()
        return ', '.join(hand_part_types)
    
    def add_hand(self, item, time):
        if self.required_part(item) and not self.complete_time:
            self.hand.append(item)
            if self.complete_hand():
                self.hand = [Part(part_type='P', complete=True)]
                self.complete_time = time + self.complete_delay
            return True
        return False
    
    def required_part(self, item):
        if not self.complete_time:
            hand_part_types = [i.peek() for i in self.hand]
            missing_part_types = list(set(self.complete_part) - set(hand_part_types))
            return item.peek() in missing_part_types
        else:
            return False
    
    def complete_hand(self):
        if self.complete_time:
            return True
        else:
            hand_part_types = [i.peek() for i in self.hand]
            hand_part_types.sort()
            return hand_part_types == complete_part
    
    def place(self, idx=0):
        self.complete_time = None
        return self.hand.pop(idx)
