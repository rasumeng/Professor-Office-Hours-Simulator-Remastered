import threading
import time

class Professor:
    #Initialize threads and variables
    def __init__(self, office):
        self.office = office

    #Take a break
    def take_break(self):
        print("Professor is taking a break")
        time.sleep(5)

        # Reset state safely
        while self.office.lock:
            self.office.students_since_break = 0
            self.office.consecutive_count = 0
            self.office.prof_on_break = False

            #Wake up all waiting students
            self.office.condition.notify_all()
    
    def run(self):
        print("Professor arrived and started office hours.")

        while True:
            # Wait uuntil:
            # - helped 10 students
            # - office is empty
            with not(
                self.office.students_since_break >= self.office.PROFESSOR_LIMIT
                and self.office.students_in_office == 0
            ):
                self.office.prof_condition.wait()
            
            self.office.prof_on_break = True
        
        self.take_break()