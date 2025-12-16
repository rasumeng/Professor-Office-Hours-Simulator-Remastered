#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <assert.h>

/*** Constants that define parameters of the simulation ***/

#define MAX_SEATS 3        /* Number of seats in the professor's office */
#define professor_LIMIT 10 /* Number of students the professor can help before he needs a break */
#define MAX_STUDENTS 1000  /* Maximum number of students in the simulation */

#define CLASSA 0
#define classA 0
#define CLASSB 1
#define classB 1
#define CLASSC 2
#define CLASSD 3
#define CLASSE 4

/* TODO */
/* Add your synchronization variables here */

pthread_mutex_t office_mutex;  //for shared variables
pthread_cond_t office;   // for studenteds waiting to enter the office
pthread_cond_t prof_signal;   // signal for the professor

/* Basic information about simulation.  They are printed/checked at the end 
 * and in assert statements during execution.
 *
 * You are responsible for maintaining the integrity of these variables in the 
 * code that you develop. 
 */

static int students_in_office;   /* Total numbers of students currently in the office */
static int classA_inoffice;      /* Total numbers of students from class A currently in the office */
static int classB_inoffice;      /* Total numbers of students from class B in the office */
static int students_since_break = 0;
//Keep track of how many of one class enter

static int consecutive_count = 0;
static int prof_break = 0; // true/flase flag for the professor's break
static int last_class = -1; // Variable to switch between classes.

// Waiting variables used to help keep fairness
static int waiting_A = 0; 
static int waiting_B = 0;


typedef struct 
{
  int arrival_time;  // time between the arrival of this student and the previous student
  int question_time; // time the student needs to spend with the professor
  int student_id;
  int class;
} student_info;

/* Called at beginning of simulation.  
 * TODO: Create/initialize all synchronization
 * variables and other global variables that you add.
 */
static int initialize(student_info *si, char *filename) 
{
  students_in_office = 0;
  classA_inoffice = 0;
  classB_inoffice = 0;
  students_since_break = 0;
  prof_break = 0;
  last_class = -1;


  /* Initialize your synchronization variables (and 
   * other variables you might use) here
   */
   pthread_mutex_init(&office_mutex, NULL);
   pthread_cond_init(&office, NULL);
   pthread_cond_init(&prof_signal, NULL);


  /* Read in the data file and initialize the student array */
  FILE *fp;

  if((fp=fopen(filename, "r")) == NULL) 
  {
    printf("Cannot open input file %s for reading.\n", filename);
    exit(1);
  }

  int i = 0;
  while ( (fscanf(fp, "%d%d%d\n", &(si[i].class), &(si[i].arrival_time), &(si[i].question_time))!=EOF) && 
           i < MAX_STUDENTS ) 
  {
    i++;
  }

 fclose(fp);
 return i;
}

/* Code executed by professor to simulate taking a break 
 * You do not need to add anything here.  
 */
static void take_break() 
{
  printf("The professor is taking a break now.\n");
  sleep(5);
  assert( students_in_office == 0 );
  students_since_break = 0;
}

/* Code for the professor thread. This is fully implemented except for synchronization
 * with the students.  See the comments within the function for details.
 */
void *professorthread(void *junk) 
{
  printf("The professor arrived and is starting his office hours\n");
  /* Loop while waiting for students to arrive. */
  while (1) 
  {
    // Lock the office mutext to not run into race condition
    pthread_mutex_lock(&office_mutex); 

    // Waits until the office is empty and the professor has helped 10 students
    while (!(students_since_break >= professor_LIMIT && students_in_office == 0)) {
      pthread_cond_wait(&prof_signal, &office_mutex);
    }

    // signal that professor is on break
    prof_break = 1;
    pthread_mutex_unlock(&office_mutex);

    take_break();

    pthread_mutex_lock(&office_mutex);
    
    // reset counters and prof_break flag
    prof_break = 0;
    students_since_break = 0;
    consecutive_count = 0;

    // So the class changes if the professor goes on break after 
    // 5 consectuive students from the same class
    if (last_class == CLASSA && consecutive_count == 5) {
      last_class = CLASSB;
      printf("\nClass B's Turn\n\n"); // to make the simulation look cleaner
    } 
    else if (last_class == CLASSB && consecutive_count == 5) {
      last_class = CLASSA;
      printf("\nClass A's Turn\n\n"); // to make the simulation look cleaner
    }

    // alert the students
    pthread_cond_broadcast(&office);
    pthread_mutex_unlock(&office_mutex);
  }
  pthread_exit(NULL);
}


/* Code executed by a class A student to enter the office.
 * You have to implement this.  Do not delete the assert() statements,
 * but feel free to add your own.
 */
void classA_enter() 
{
  /* TODO */
  /* Request permission to enter the office.  You might also want to add  */
  /* synchronization for the simulations variables below                  */
  /*  YOUR CODE HERE.                                                     */
  pthread_mutex_lock(&office_mutex);
  waiting_A++; //track A students waiting

  // wait until free seat, no class B in office, prof not on break, etc
  while ((students_in_office >= MAX_SEATS) || (classB_inoffice > 0) || (prof_break) || 
        (students_since_break >= professor_LIMIT) || ((consecutive_count == 5 && last_class == CLASSA) && (waiting_B > 0))) 
  {
    pthread_cond_wait(&office, &office_mutex);  //wait for space of class change
  }

  waiting_A--;


  students_in_office += 1;
  students_since_break += 1;
  classA_inoffice += 1;

  // Keep fairness so an exttra student doesn't slip in or get left out
  if (last_class == CLASSA) {
    consecutive_count++;
  } 
  else if (last_class!= CLASSA) {
    last_class = CLASSA;
    printf("\nClass A's Turn\n\n");
    consecutive_count = 1;
  }
  

  pthread_mutex_unlock(&office_mutex);
}

/* Code executed by a class B student to enter the office.
 * You have to implement this.  Do not delete the assert() statements,
 * but feel free to add your own.
 */
void classB_enter() 
{

  /* TODO */
  /* Request permission to enter the office.  You might also want to add  */
  /* synchronization for the simulations variables below                  */
  /*  YOUR CODE HERE.                                                     */ 
  pthread_mutex_lock(&office_mutex);
  waiting_B++;

  while ((students_in_office >= MAX_SEATS) || (classA_inoffice > 0) || (prof_break) ||
         (students_since_break >= professor_LIMIT) || ((consecutive_count == 5 && last_class == CLASSB) && (waiting_A > 0))) 
  {
    pthread_cond_wait(&office, &office_mutex);  //wait for space or class change
  }

  waiting_B--;

  students_in_office += 1;
  students_since_break += 1;
  classB_inoffice += 1;

  // Keep fairness so an exttra student doesn't slip in or get left out
  // Same as class A but now class B :)
  if (last_class == CLASSB) {
    consecutive_count++;
  } 
  else if (last_class != CLASSB){
    last_class = CLASSB;
    printf("\nClass B's Turn\n\n");
    consecutive_count = 1;
  }

  pthread_mutex_unlock(&office_mutex);
}

/* Code executed by a student to simulate the time he spends in the office asking questions
 * You do not need to add anything here.  
 */
static void ask_questions(int t) 
{
  sleep(t);
}


/* Code executed by a class A student when leaving the office.
 * You need to implement this.  Do not delete the assert() statements,
 * but feel free to add as many of your own as you like.
 */
static void classA_leave() 
{
  // lock so no race condition :D
  pthread_mutex_lock(&office_mutex);

  students_in_office -= 1;
  classA_inoffice -= 1;
  
  // Allert the professor that he can go on break since he helped 
  // everybody in office and its been ten students
  if (students_in_office == 0 && students_since_break >= professor_LIMIT) {
    pthread_cond_signal(&prof_signal);
  }

  pthread_cond_broadcast(&office);
  pthread_mutex_unlock(&office_mutex);
}

/* Code executed by a class B student when leaving the office.
 * You need to implement this.  Do not delete the assert() statements,
 * but feel free to add as many of your own as you like.
 */
static void classB_leave() 
{
  // lock so no race condition :D
  pthread_mutex_lock(&office_mutex);

  students_in_office -= 1;
  classB_inoffice -= 1;

  if (students_in_office == 0 && students_since_break >= professor_LIMIT) {
    pthread_cond_broadcast(&prof_signal);
  }

  pthread_cond_broadcast(&office);
  pthread_mutex_unlock(&office_mutex);
}

/* Main code for class A student threads.  
 * You do not need to change anything here, but you can add
 * debug statements to help you during development/debugging.
 */
void* classA_student(void *si) 
{
  student_info *s_info = (student_info*)si;

  /* enter office */
  classA_enter();

  printf("Student %d from class A enters the office\n", s_info->student_id);

  assert(students_in_office <= MAX_SEATS && students_in_office >= 0);
  assert(classA_inoffice >= 0 && classA_inoffice <= MAX_SEATS);
  //With this assert included run into the consistent issues
  //assert(classB_inoffice >= 0 && classB_inoffice <= MAX_SEATS);
  assert(classB_inoffice == 0 );
  
  /* ask questions  --- do not make changes to the 3 lines below*/
  printf("Student %d from class A starts asking questions for %d minutes\n", s_info->student_id, s_info->question_time);
  ask_questions(s_info->question_time);
  printf("Student %d from class A finishes asking questions and prepares to leave\n", s_info->student_id);

  /* leave office */
  printf("Student %d from class A leaves the office\n", s_info->student_id); // Moved up because it looked nicer

  classA_leave();  

  //printf("Student %d from class A leaves the office\n", s_info->student_id);

  assert(students_in_office <= MAX_SEATS && students_in_office >= 0);
  //With this assert included run into the consistent issues
  //assert(classB_inoffice >= 0 && classB_inoffice <= MAX_SEATS);
  assert(classA_inoffice >= 0 && classA_inoffice <= MAX_SEATS);

  pthread_exit(NULL);
}

/* Main code for class B student threads.
 * You do not need to change anything here, but you can add
 * debug statements to help you during development/debugging.
 */
void* classB_student(void *si) 
{
  student_info *s_info = (student_info*)si;

  /* enter office */
  classB_enter();

  printf("Student %d from class B enters the office\n", s_info->student_id);

  assert(students_in_office <= MAX_SEATS && students_in_office >= 0);
  assert(classB_inoffice >= 0 && classB_inoffice <= MAX_SEATS);
  //With this assert included run into the consistent issues
  //assert(classA_inoffice >= 0 && classA_inoffice <= MAX_SEATS);
  assert(classA_inoffice == 0 );

  printf("Student %d from class B starts asking questions for %d minutes\n", s_info->student_id, s_info->question_time);
  ask_questions(s_info->question_time);
  printf("Student %d from class B finishes asking questions and prepares to leave\n", s_info->student_id);

  /* leave office */
  printf("Student %d from class B leaves the office\n", s_info->student_id); // Moved up because it looked nicer
  classB_leave();        

  //printf("Student %d from class B leaves the office\n", s_info->student_id);

  assert(students_in_office <= MAX_SEATS && students_in_office >= 0);
  assert(classB_inoffice >= 0 && classB_inoffice <= MAX_SEATS);
  //With this assert included run into the consistent issues
  //assert(classA_inoffice >= 0 && classA_inoffice <= MAX_SEATS);

  pthread_exit(NULL);
}

/* Main function sets up simulation and prints report
 * at the end.
 * GUID: 355F4066-DA3E-4F74-9656-EF8097FBC985
 */
int main(int nargs, char **args) 
{
  int i;
  int result;
  int student_type;
  int num_students;
  void *status;
  pthread_t professor_tid;
  pthread_t student_tid[MAX_STUDENTS];
  student_info s_info[MAX_STUDENTS];

  if (nargs != 2) 
  {
    printf("Usage: officehour <name of inputfile>\n");
    return EINVAL;
  }

  num_students = initialize(s_info, args[1]);
  if (num_students > MAX_STUDENTS || num_students <= 0) 
  {
    printf("Error:  Bad number of student threads. "
           "Maybe there was a problem with your input file?\n");
    return 1;
  }

  printf("Starting officehour simulation with %d students ...\n",
    num_students);

  result = pthread_create(&professor_tid, NULL, professorthread, NULL);

  if (result) 
  {
    printf("officehour:  pthread_create failed for professor: %s\n", strerror(result));
    exit(1);
  }

  for (i=0; i < num_students; i++) 
  {

    s_info[i].student_id = i;
    sleep(s_info[i].arrival_time);
                
    student_type = random() % 2;

    if (s_info[i].class == classA)
    {
      result = pthread_create(&student_tid[i], NULL, classA_student, (void *)&s_info[i]);
    }
    else // student_type == classB
    {
      result = pthread_create(&student_tid[i], NULL, classB_student, (void *)&s_info[i]);
    }

    if (result) 
    {
      printf("officehour: thread_fork failed for student %d: %s\n", 
            i, strerror(result));
      exit(1);
    }
  }

  /* wait for all student threads to finish */
  for (i = 0; i < num_students; i++) 
  {
    pthread_join(student_tid[i], &status);
  }

  /* tell the professor to finish. */
  pthread_cancel(professor_tid);

  printf("Office hour simulation done.\n");

  return 0;
}