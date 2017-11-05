"""
Purpose: apply concepts learned in book intro to computation and prog
put them to use directly as applications in epsilon project
"""
# using the raise statement
# will test that ramq number has only digits in last 12 characters
# format of ramq number is XXXX CCCC CCCC CCCC where C is a digit

"""
Using the raise statement
example of use would be when processing input for name entry or act creation options selected
"""

"""
use the class concept to create new types and all related operations
could create a "card type" which would capture patient identication object, a list of acts performed on this patient on a given episode of work

A card object would have:
a patient
a referring physician opt
"""

"""
reference tables

physician db
icd db
locations db
ramqcodes db
patient db
"""

purpose of the program is to:
track my medical work with patients, lab, meetings, other
display and perform billing
perform analysis on work data

Track acts of work :
    three types of activity: clinical, lab, administrative
    all have a date of creation, a kind, a place
    should be able to set those three attributes
    a clinical act is a subtype of act. it is applied to a patient, with a list of diagnoses

clinical acts:
    patient
    datetime start
    date end
    billed
    ramq code
    episode

episode:
    date start
    date end
    diagnosis list

list_work_in_progress(work):
    **work=clinical||episode** where date end == None

#######################
i create a patient and add it to static database
need a modify static db object
"""
staticdb(Base):
    def getdic()
    def update()
class Patient(staticdb)
a = Patient(instancedic)
a.getdic()
a.update(instancedic)
"""
#######################

data structures to store the collected information

class ActOfWork (object):

    def __init__(self, )
