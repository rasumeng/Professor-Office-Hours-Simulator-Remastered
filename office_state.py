import threading
from typing import NamedTuple

class student_info(NamedTuple):
    arrival_time: int
    question_time: int
    student_id: int
    class_section: int
    