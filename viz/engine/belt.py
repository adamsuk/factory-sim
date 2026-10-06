from part import Part

class Belt:
    def __init__(self, size=4):
        self.size = size
        self.belt = [Part(None)] * size
        self.time_used = [None] * size
    
    def add(self, item):
        self.belt.insert(0, item)
        last_item = self.belt[-1]
        self.belt = self.belt[0:self.size]
        return last_item

    def peek(self, idx):
        return self.belt[idx]

    def pick(self, idx, time):
        if not self.in_use(idx, time):
            self.time_used[idx] = time
            item = self.belt[idx]
            self.belt[idx] = Part(None)
            return item
    
    def place(self, idx, time, item):
        if not self.in_use(idx, time):
            self.time_used[idx] = time
            self.belt[idx] = item
    
    def in_use(self, idx, time):
        return self.time_used[idx] == time
