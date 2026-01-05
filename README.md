# 🧑‍🏫 Professor Office Hours Simulator (Remastered)

A concurrency-based simulation inspired by the controlled chaos of real university office hours.

This project is a **Python reimplementation and expansion** of a systems-level C project originally built using POSIX threads, mutexes, and condition variables. The remastered version focuses on **clarity, visualization, and extensibility**, while preserving the core concurrency challenges.

---

## 📖 Background & Inspiration

Anyone who’s attended office hours knows the struggle:
- Limited seating  
- Students from different classes competing for time  
- Professors needing breaks  
- Fairness complaints when one group dominates  

The original C version of this project simulated these constraints using low-level threading primitives.  
This remastered version translates that logic into Python, emphasizing **software design**, **readability**, and **debug-friendly output**, while still modeling real concurrency problems like race conditions, fairness, and synchronization.

---

## 🎯 What This Project Simulates

A professor teaches **two classes (Class A and Class B)** and holds shared office hours with strict rules:

### Core Rules
- 🪑 **Limited Capacity**: Only **3 students** may be in the office at once.
- 🚫 **Class Mutual Exclusion**: Students from Class A and Class B **cannot mix** in the office.
- ⚖️ **Fairness Rule**: After **5 consecutive students** from one class, the other class must be given a turn (if waiting).
- ☕ **Professor Break Rule**: After helping **10 students total**, the professor takes a mandatory break.
- ⛔ **No Entry During Breaks**: Students must wait while the professor is on break.
- 🔁 **Progress Without Starvation**: Waiting students are eventually served.

---

## 🧠 How It Works

### Thread Model
- Each student is represented as a **thread**
- The professor runs in a **separate thread**
- A shared `Office` object coordinates all access

### Synchronization
- `threading.Lock` ensures mutual exclusion
- `threading.Condition` manages waiting and signaling
- Fairness is enforced using counters and class tracking

### Data-Driven Simulation
Students are loaded from a CSV file (`students.csv`), allowing easy modification of:
- Arrival order
- Question duration
- Class distribution

---

## 🗂️ Project Structure
├── main.py # Simulation entry point
├── office.py # Core synchronization & fairness logic
├── professor.py # Professor behavior & break handling
├── student.py # Student thread behavior
├── students.csv # Input data for student arrivals
└── README.md

---

## ▶️ How to Run

### Requirements
- Python **3.10+**

### Run the Simulation
```bash
cd .\Professor-Office-Hours-Simulator-Remastered\
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
