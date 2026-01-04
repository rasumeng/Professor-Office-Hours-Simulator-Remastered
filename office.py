import threading
from typing import NamedTuple
from ui import office_panel, event, fairness_switch

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
    
    def _snapshot(self):
        return {
            "students_in_office": self.students_in_office,
            "classA_in_office": self.classA_in_office,
            "classB_in_office": self.classB_in_office,
            "waiting_A": self.waiting_A,
            "waiting_B": self.waiting_B,
            "students_since_break": self.students_since_break,
            "consecutive_count": self.consecutive_count,
            "last_class": self.last_class,
            "prof_on_break": self.prof_on_break
        }


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
            switched = False
            if self.last_class == "A":
                self.consecutive_count += 1
                # Debug: show switch if 5 consecutive reached
                if self.consecutive_count == 5 and self.waiting_B > 0:
                    print("\n--- Switching to Class B after 5 consecutive Class A students ---\n")
                    switched = True
            else:
                self.last_class = "A"
                self.consecutive_count = 1
            snapshot = self._snapshot()

        #UI outside of lock
        event(f"Student {student.id} (Class A) entered", "A")
        office_panel(self)

        if switched:
            fairness_switch(from_class="A", to_class="B")

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
            switched = False
            if self.last_class == "B":
                self.consecutive_count += 1
                # Debug: show switch if 5 consecutive reached
                if self.consecutive_count == 5 and self.waiting_A > 0:
                    print("\n--- Switching to Class A after 5 consecutive Class B students ---\n")
                    switched = True
            else:
                self.last_class = "B"
                self.consecutive_count = 1
            snapshot = self._snapshot()
        #UI outside of lock
        event(f"Student {student.id} (Class B) entered", "B")
        office_panel(self)

        if switched:
            fairness_switch(from_class="B", to_class="A")
    
    def leave_class_a(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classA_in_office -= 1
            
            #signal professor if break conditions are met
            if (self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT):
                self.prof_condition.notify()

            # Wake up waiting students
            snapshot = self._snapshot()
            self.condition.notify_all()
        event(f"Student {student.id} (Class A) left")
        office_panel(snapshot)

    
    def leave_class_b(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classB_in_office -= 1
            

            #signal professor if break conditions are met
            if (self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT):
                self.prof_condition.notify()

            # Wake up waiting students
            snapshot = self._snapshot()
            self.condition.notify_all()

        event(f"Student {student.id} (Class B) left", "B")
        office_panel(snapshot)