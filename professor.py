import threading
import time

class Professor:
    #Initialize threads and variables
    def __init__(self, office):
        self.office = office

    #Take a break
    def take_break(self):
        print("\n---Professor is taking a break---\n")
        time.sleep(5)

        # Reset state safely
        with self.office.lock:
            self.office.students_since_break = 0
            self.office.consecutive_count = 0
            self.office.prof_on_break = False
            self.office.last_class = None

            #Wake up all waiting students
            self.office.condition.notify_all()

        print("\n--- Counters reset. Office ready for new students. ---\n")

    
    def run(self):
        print("\n---Professor arrived and started office hours.---\n")

        while True:
            # Wait until professor should take a break
            with self.office.lock:
                while not (
                    self.office.students_since_break >= self.office.PROFESSOR_LIMIT
                    and self.office.students_in_office == 0
                ):
                    self.office.prof_condition.wait()
                
                # Professor goes on break
                self.office.prof_on_break = True

            # Take break outside the lock to avoid blocking students unnecessarily
            self.take_break()