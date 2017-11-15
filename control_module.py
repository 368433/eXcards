DATA TYPES:
    patient
    act
    episode of work
    Patient list

FUNCTIONS:
    CREATE
    READ
    UPDATE
    DELETE
    SEARCH: whoosh and whooshalchemy

patient(fname, lname, dob, phone, postalcode, ramq, mrn)
    CREATE:
        def __init__(self, fname, lname, dob, phone, postalcode, ramq, mrn):
            pass
    READ:
        def __str__(self):
            pass
        def get_patient(self, id):
            returns a dict of values
            pass
    UPDATE:
        def update_patient(self, **kwargs):
            dict = get_patient()
            newdict = dialogs(dict)
            set_newvals(object, **kwargs):
                for keys in kwargs:
                    object.keys = kwargs[keys]
                    session.add(object)
                    session.commit()
    DELETE:
        def delete_patient(self):
            pass

episodeofwork(patient, act[], start, end, diagnosis[])
    CREATE
        def __init__(self, patient, act[], start, end, diagnosis[]):
    READ
        def __str__(self):
            pass
        def get_episodeofwork(self, id):
            return a dict of values
    UPDATE
        def update_episodeofwork(self, **kwargs):
            pass
    DELETE
        def delete_episodeofwork(self):
            pass

act(start, end, patient, invsout, facility, secteur, bed, nature, billingcode, episodeofwork)
    CREATE
    READ
    UPDATE
    DELETE

patientlist(function)
    CREATE:
        def __init__(self, function):
    READ
        def get_list(self):
            return patientlist
    UPDATE
        refresh list
    DELETE

CREATE
READ
UPDATE
DELETE
