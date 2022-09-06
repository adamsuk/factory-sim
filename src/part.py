class Part:
    def __init__(self, part_type, complete=False):
        self.part_type = part_type
        self.complete = complete

    def peek(self):
        return self.part_type
