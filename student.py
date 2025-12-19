import threading
import time

class Student(threading.Thread):
    def __init__(self, student_id, student_class, arrival_time, question_time, office):
        super().__init__()

        self.id = student_id
        self.student_class = student_class # "A" or "B"
        self.arrival_time = arrival_time
        self.question_time = question_time
        self.office = office

    def run(self):
        
        # Simulate arrival delay
        time.sleep(self.arrival_time)

        # Enter office 
        self.enter_office()

        print(f"Student {self.id} from class {self.student_class} entered the office.")

        # Ask questions
        print(
            f"Student {self.id} from class {self.student_class} "
            f"Starts asking questions for {self.question_time} minutes"
        )

        time.sleep(self.question_time)

        print(f"Student {self.id} from class {self.student_class} prepares to leave")

        # Leave the office
        self.leave_office()

        print(f"Student {self.id} from class {self.student_class} left the office")

    def enter_office(self):
        if self.student_class == "A":
            self.office.enter_class_a(self)
        elif self.student_class == "B":
            self.office.enter_class_b(self)
    
    def leave_office(self):
        if self.student_class == "A":
            self.office.leave_class_a(self)
        elif self.student_class == "B": 
            self.office.leave_class_b(self) 