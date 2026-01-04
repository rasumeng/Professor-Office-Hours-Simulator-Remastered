import csv
import threading
import time

from office import Office
from professor import Professor
from student import Student
from ui import  render_office_panel, console
from rich.live import Live

def load_students(filename, office):
    students = []
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student = Student(
                student_id=int(row["id"]),
                student_class=row["class"],
                arrival_time=float(row["arrival_time"]),
                question_time=float(row["question_time"]),
                office=office
            )
            students.append(student)
    return students

def main():
    office = Office()
    professor = Professor(office)
    students = load_students("students.csv", office)

    # Use 'with' here to manage the live panel
    with Live(render_office_panel(office._snapshot()), refresh_per_second=4, console=console) as live:
        office.live = live  # so office methods can update panel

        # Start professor thread
        threading.Thread(target=professor.run, daemon=True).start()

        # Start all students
        for student in students:
            student.start()

        # Wait for all students to finish
        for student in students:
            student.join()

        # All students finished, update final snapshot
        final_snapshot = office._snapshot()

        # Make sure office shows empty
        final_snapshot['students_in_office'] = 0
        final_snapshot['last_class'] = None
        final_snapshot['consecutive_count'] = 0

        live.update(render_office_panel(final_snapshot))

    print("\nOffice hour simulation complete.\n")



if __name__ == "__main__":
    main()
