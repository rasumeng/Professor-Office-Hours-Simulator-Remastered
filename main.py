from professor import Professor, threading
from office import Office  
from student import Student

#Create Shared office
office = Office()

#create prof object
prof = Professor(office)

prof_thread = threading.Thread(target=prof.run)
prof_thread.start()
