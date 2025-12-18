import threading
from typing import NamedTuple

class Office:
    #Similart to a global variable for the class (DEFINE)
    MAX_SEATS = 3
    PROFESSOR_LIMIT = 10

    def __init__(self, office):
        self.students_in_office = 0
        self.classA_in_office = 0
        self.classB_in_office = 0

        self.students_sicne_break = 0
        self.consecutive_count = 0
        self.last_class = None
        self.prof_on_break = False

        self.waiting_A = 0
        self.waiting_B = 0

        # Synchronization
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.prof_condition = threading.Condition(self.lock)