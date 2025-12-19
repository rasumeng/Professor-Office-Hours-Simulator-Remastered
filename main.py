import csv
import threading

from office import Office
from professor import Professor
from student import Student

def load_students(filename, office):
    students = []

    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student = Student(
                student_id = int(row["id"]),
                student_class = row["class"],
                arrival_time = float(row["arrival_time"]),
                question_time = float(row["question_time"]),
                office = office
            )
            students.append(student)
    
    return students

def main():
    office = Office()

    professor = Professor(office)
    professor_thread = threading.Thread(target=professor.run, daemon=True)
    professor_thread.start()

    students = load_students("students.csv", office)

    for student in students:
        student.start()
    
    for student in students:
        student.join()
    
    print("\nOffice hour simulation complete. \n")

if __name__ == "__main__":
    main()
