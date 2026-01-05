from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

console = Console()
MAX_SEATS = 3

def render_office_panel(office):
    status = Text()
    status.append(f"Seats: {office['students_in_office']} / {MAX_SEATS}\n", style="bold")
    status.append(f"Current Class: {office['last_class']}\n")
    status.append(f"Since Break: {office['students_since_break']}\n")
    status.append(f"Consecutive: {office['consecutive_count']}\n")
    status.append("Professor: ON BREAK\n" if office['prof_on_break'] else "Professor: Teaching\n",
                  style="red" if office['prof_on_break'] else "green")

    # Waiting students
    waiting_a = ", ".join(map(str, office['waiting_A_ids'])) if office['waiting_A_ids'] else "None"
    waiting_b = ", ".join(map(str, office['waiting_B_ids'])) if office['waiting_B_ids'] else "None"
    status.append("\nWaiting:\n")
    status.append(f"    Class A: {waiting_a}\n")
    status.append(f"    Class B: {waiting_b}\n")

    # Recent event log
    if office['log']:
        status.append("\nRecent Events:\n")
        for line in office['log']:
            status.append(f"  {line}\n")

    return Panel(status, title="OFFICE STATUS", border_style="cyan")


def office_panel_live(office):
    """Create a Live panel for the office that can be updated in real-time."""
    live = Live(render_office_panel(office), refresh_per_second=2, console=console)
    live.start()  # Start the live display
    return live

def event(message, student_class=None):
    color = "blue" if student_class == "A" else "green" if student_class == "B" else "yellow"
    console.print(message, style=color)

# Commented out for future use

# def fairness_switch(from_class, to_class):
#     console.print(
#         Panel(
#             f"⚖️ Switching to Class {to_class}",
#             border_style="magenta"
#         )
#     )
