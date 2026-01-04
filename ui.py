from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def office_panel(office):
    status = Text()
    status.append(f"Seats: {office.students_in_office} / 3\n", style="bold")
    status.append(f"Current Class: {office.last_class}\n")
    status.append(f"Since Break: {office.students_since_break}\n")
    status.append(f"Consecutive: {office.consecutive_count}\n")
    status.append(
        "Professor: ON BREAK\n" if office.prof_on_break else "Professor: Teaching\n",
        style="red" if office.prof_on_break else "green"
    )

    console.print(
        Panel(status, title="OFFICE STATUS", border_style="cyan")
    )

def event(message, student_class=None):
    color = "blue" if student_class == "A" else "green" if student_class == "B" else "yellow"
    console.print(message, style=color)

def fairness_switch(new_class):
    console.print(
        Panel(
            f"⚖️ Switching to Class {new_class}",
            border_style="magenta"
        )
    )
