import threading
from typing import NamedTuple
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from ui import render_office_panel, event, fairness_switch

class Office:
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
        self.waiting_A_ids = []
        self.waiting_B_ids = []

        # NEW: Log of recent events (entered/left)
        self.log = []
        self.log_limit = 10  # Max number of log entries to keep
        # Synchronization
        self.lock = threading.Lock() 
        self.condition = threading.Condition(self.lock)
        self.prof_condition = threading.Condition(self.lock)


    def add_log(self, message):
        self.log.append(message)
        if len(self.log) > self.log_limit:
            self.log.pop(0)
            
    def _snapshot(self):
        return {
            "students_in_office": self.students_in_office,
            "last_class": self.last_class,
            "consecutive_count": self.consecutive_count,
            "students_since_break": self.students_since_break,
            "prof_on_break": self.prof_on_break,
            "waiting_A_ids": list(self.waiting_A_ids),
            "waiting_B_ids": list(self.waiting_B_ids),
            "log": list(self.log)  # keep all recent events
        }





    def get_waiting_ids(self, class_type):
        return self.waiting_A_ids if class_type == 'A' else self.waiting_B_ids

    def enter_class_a(self, student):
        with self.condition:
            self.waiting_A += 1
            self.waiting_A_ids.append(student.id)
            self.add_log(f"Student {student.id} (Class A) is waiting...")


            while (self.students_in_office >= self.MAX_SEATS
                or self.classB_in_office > 0
                or self.students_since_break >= self.PROFESSOR_LIMIT
                or self.prof_on_break
                or (self.consecutive_count == 5 and self.last_class == "A" and self.waiting_B > 0)):
                self.condition.wait()

            self.waiting_A -= 1
            self.waiting_A_ids.remove(student.id)
            self.students_in_office += 1
            self.classA_in_office += 1
            self.students_since_break += 1

            self.add_log(f"Student {student.id} (Class A) entered")

            # Fairness tracking
            switched = False
            if self.last_class == "A":
                self.consecutive_count += 1
                if self.consecutive_count == 5 and self.waiting_B > 0:
                    switched = True
                    self.add_log("--- Switching to Class B after 5 consecutive Class A students ---")

            else:
                self.last_class = "A"
                self.consecutive_count = 1

            snapshot = self._snapshot()
            if self.live:
                self.live.update(render_office_panel(snapshot))
            
            return switched

        event(f"Student {student.id} (Class A) entered", "A")
        if switched:
            fairness_switch(from_class="A", to_class="B")

    def enter_class_b(self, student):
        with self.condition:
            self.waiting_B += 1
            self.waiting_B_ids.append(student.id)
            self.add_log(f"Student {student.id} (Class B) is waiting...")

            while (self.students_in_office >= self.MAX_SEATS
                or self.classA_in_office > 0
                or self.students_since_break >= self.PROFESSOR_LIMIT
                or self.prof_on_break
                or (self.consecutive_count == 5 and self.last_class == "B" and self.waiting_A > 0)):
                self.condition.wait()

            self.waiting_B -= 1
            self.waiting_B_ids.remove(student.id)
            self.students_in_office += 1
            self.classB_in_office += 1
            self.students_since_break += 1

            self.add_log(f"Student {student.id} (Class B) entered")


            switched = False
            if self.last_class == "B":
                self.consecutive_count += 1
                if self.consecutive_count == 5 and self.waiting_A > 0:
                    switched = True
                    self.add_log("--- Switching to Class A after 5 consecutive Class B students ---")
            else:
                self.last_class = "B"
                self.consecutive_count = 1

            snapshot = self._snapshot()
            if self.live:
                self.live.update(render_office_panel(snapshot))

        if switched:
            fairness_switch(from_class="B", to_class="A")

    def leave_class_a(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classA_in_office -= 1
            self.add_log(f"Student {student.id} (Class A) left")
            self.condition.notify_all()
            snapshot = self._snapshot()
            if self.live:
                self.live.update(render_office_panel(snapshot))

            if self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT:
                self.prof_condition.notify()

           

    def leave_class_b(self, student):
        with self.condition:
            self.students_in_office -= 1
            self.classB_in_office -= 1
            self.add_log(f"Student {student.id} (Class B) left")
            self.condition.notify_all()
            snapshot = self._snapshot()
            if self.live:
                self.live.update(render_office_panel(snapshot))

            if self.students_in_office == 0 and self.students_since_break >= self.PROFESSOR_LIMIT:
                self.prof_condition.notify()

