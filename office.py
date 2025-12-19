import threading
from typing import NamedTuple

class Office:
    #Similart to a global variable for the class (DEFINE)
    MAX_SEATS = 3
    PROFESSOR_LIMIT = 10

    def __init__(self):
        self.students_in_office = 0
        self.classA_in_office = 0
        self.classB_in_office = 0

        self.students_since_break = 0
        self.consecutive_count = 0
        self.last_class = None
        self.prof_on_break = False

        self.waiting_A = 0
        self.waiting_B = 0

        # Synchronization
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.prof_condition = threading.Condition(self.lock)

    def enter_class_a(self, student):
        with self.condition:
            self.waiting_A += 1

            while (self.students_in_office >= self.MAX_SEATS 
                or self.classB_in_office > 0 
                or self.students_since_break >= self.PROFESSOR_LIMIT 
                or self.prof_on_break
                or (self.consecutive_count == 5 and self.last_class == "A" and self.waiting_B > 0)
                ):
                self.condition.wait()

            # Student is allowed to enter
            self.waiting_A -= 1
            self.students_in_office += 1
            self.classA_in_office += 1
            self.students_since_break += 1

            # Fairness tracking
            if self.last_class == "A":
                self.consecutive_count += 1
                # Debug: show switch if 5 consecutive reached
                if self.consecutive_count == 5 and self.waiting_B > 0:
                    print("\n--- Switching to Class B after 5 consecutive Class A students ---\n")
            else:
                self.last_class = "A"
                self.consecutive_count = 1

    def enter_class_b(self, student):
        with self.condition:
            self.waiting_B += 1

            while (self.students_in_office >= self.MAX_SEATS 
                or self.classA_in_office > 0 
                or self.students_since_break >= self.PROFESSOR_LIMIT 
                or self.prof_on_break
                or (self.consecutive_count == 5 and self.last_class == "B" and self.waiting_A > 0)
                ):
                self.condition.wait()

            # Student is allowed to enter
            self.waiting_B -= 1
            self.students_in_office += 1
            self.classB_in_office += 1
            self.students_since_break += 1

            # Fairness tracking
            if self.last_class == "B":
                self.consecutive_count += 1
                # Debug: show switch if 5 consecutive reached
                if self.consecutive_count == 5 and self.waiting_A > 0:
                    print("\n--- Switching to Class A after 5 consecutive Class B students ---\n")
            else:
                self.last_class = "B"
                self.consecutive_count = 1
    
    def leave_class_a(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classA_in_office -= 1

            #signal professor if break conditions are met
            if (self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT):
                self.prof_condition.notify()

            # Wake up waiting students
            self.condition.notify_all()
    
    def leave_class_b(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classB_in_office -= 1

            #signal professor if break conditions are met
            if (self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT):
                self.prof_condition.notify()

            # Wake up waiting students
            self.condition.notify_all()