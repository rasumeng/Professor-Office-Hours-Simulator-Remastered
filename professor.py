import threading
import time

class Professor:
    def __init__(self, office):
        self.office = office
        self.students_since_break = 0
        self.students_in_office = 0
        self.prof_break = False
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)