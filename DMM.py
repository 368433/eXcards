from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Sequence
from sqlalchemy import create_engine, Table, Text, distinct
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time, platform
from random import randint


#############################################################
# ENGINE initialization
Base = declarative_base()
engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

#####################################
# STATIC
class BillingCode(Base):
  __tablename__ = 'billingcode'

  id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
  code = Column(Integer)
  abbreviation = Column(String(2))
  description = Column(String)
  fee = Column(Float(5))
  location = Column(String(5))
  category = Column(String(5))
  act = relationship("Act", back_populates = "billingcode")

  def get_billingcode(self, abbreviation, location, category):
      code_id = session.query(BillingCode).filter_by(abbreviation = abbreviation,location = location, category = category)
      return code_id.one().id

  def __repr__(self):
      return "<BillingCode(id='%s', abbreviation = '%s', code='%s', description='%s', fee='%s')>" % (
                          self.id, self.abbreviation, self.code, self.description, self.fee) # done

class Facility(Base):
    __tablename__="facility"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    name = Column(String)
    abbreviation = Column(String)
    postal_code = Column(String(6))
    phone = Column(String(10))
    address =  Column(String)

    act = relationship("Act", back_populates="facility")

    def __repr__(self):
        return "<Facility(id='%s', name = '%s', phone='%s')>" % (self.id, self.name, self.phone) # done

class Secteur(Base):
    __tablename__="secteur"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    name = Column(String)
    abbreviation = Column(String)

    act = relationship("Act", back_populates="secteur")

    def __repr__(self):
        return "<Secteur(id='%s', name = '%s', abbr='%s')>" % (self.id, self.name, self.abbreviation)

class Physician(Base):
    __tablename__="physician"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    fname = Column(String)
    lname = Column(String)
    license = Column(String)
    address = Column(String)
    phone = Column(String)
    specialty = Column(String)


    def __repr__(self):
        return "<physician(id={}, license ={}, first name = {}, last name = {})>".format(self.id, self.license, self.fname, self.lname)

class ICDCode(Base):
    __tablename__="icdcode"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    code = Column(String(6))
    description = Column(String)

    # RELATIONSHIPS
    sentinel_dx = relationship("Sentinel_Dx")

    def __repr__(self):
        return "<ICD(id={}, code={}, description={})>".format(self.id, self.code, self.description)

#####################################
# DYNAMIC
class Act(Base):
    __tablename__ = 'act'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    bed = Column(String(5))
    #BOOLEANS
    was_billed = Column(Boolean, default=False)
    is_inpt =  Column(Boolean)
    #ForeignKey
    billingcode_id = Column(Integer, ForeignKey('billingcode.id'))
    facility_id = Column(Integer, ForeignKey('facility.id'))
    EOW_id = Column(Integer, ForeignKey('episode_work.id'))
    secteur_activite_id = Column(Integer, ForeignKey('secteur.id'))
    patient_id = Column(Integer, ForeignKey('patient.id'))
    #note_id = Column(Integer, ForeignKey('notedatabase.id'))

    #DEFINING RELATIONSHIPS
    billingcode = relationship("BillingCode" , back_populates="act")
    facility = relationship("Facility", back_populates="act")
    secteur = relationship("Secteur", back_populates="act")
    episode_work = relationship("Episode_Work", back_populates="act")
    notes = relationship("Notes", order_by = "desc(Notes.dateCreated)", back_populates='Act')
    #reminder = relationship("reminder", back_populates="act")

    def __init__(self, values):
        for k, v in values.items():
            if k in self.__table__.columns.keys():
                setattr(self, k, v)
        session.add(self)
        session.commit()

    def mark_completed(self):
        self.timeEnd = datetime.utcnow()
        session.commit()

    def is_active(self):
        return self.timeEnd == None

    def __repr__(self):
        return "<Act(id='%s', timeStart='%s', billingcode_id='%s')>"%(
                self.id, self.timeStart, self.billingcode_id)

class Episode_Work(Base):
    # equivalent to Card
    __tablename__='episode_work'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    lastEdit = Column(DateTime)
    #FOREIGN KEYS
    patient_id = Column(Integer, ForeignKey('patient.id'))
    #BOOLEANS
    is_inpt = Column(Boolean, default = True, nullable = False)

    #RELATIONSHIPS
    act = relationship("Act", order_by = "desc(Act.timeStart)", back_populates='episode_work')
    patient = relationship("Patient", back_populates ="episode_work")
    sentinel_dx = relationship("Sentinel_Dx", back_populates = 'episode_work')

    def __init__(self, patient):
        self.patient_id = patient.id
        session.add(self)
        session.commit()
        self.lastEdit = self.timeStart
        session.commit()

    def add_act(self):
        act = Act(get_act_data(self, self.patient_id))
        session.add(act)
        session.commit()

    def mark_completed(self):
        self.timeEnd = datetime.utcnow()
        session.commit()

    def is_active(self):
        return self.timeEnd == None

    def get_dic(self):
        return {'Started':self.timeStart, 'Diagnosis':self.sentinel_dx[0]}

    def __repr__(self):
        patient = self.patient.get_decrypted_dic()
        fname, lname, MRN = patient['fname'], patient['lname'], patient['mrn']
        last_act = self.act[-1].timeStart.strftime('%d-%b-%Y')
        return "{0} {1}, MRN {2} \nlast visit: {3}".format(fname, lname, MRN, last_act)

class Sentinel_Dx(Base):
    __tablename__="sentinel_dx"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    episode_work_id = Column(Integer, ForeignKey('episode_work.id'))
    icdcode_id = Column(Integer, ForeignKey('icdcode.id'))
    predicted_dx = Column(String)
    final_dx = Column(String)

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by='Episode_Work.id', back_populates = 'sentinel_dx')
    icdcode = relationship("ICDCode", back_populates = 'sentinel_dx')

    def __repr__(self):
        return "<Sentinel_Dx(id = '%s')>"%(self.id)

class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    content = Column(String)
    image = Column(String)
    dateCreated = Column(DateTime, default=datetime.utcnow(), nullable=False)
    dateModified = Column(DateTime, default=datetime.utcnow(), nullable=False)
    act_id = Column(Integer, ForeignKey('act.id'))

    act = relationship("Act", back_populates ="Notes")

class Reminders(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    content = Column(String)
    dateCreated = Column(DateTime, default=datetime.utcnow(), nullable=False)
    dateModified = Column(DateTime, default=datetime.utcnow(), nullable=False)

    patient_id = Column (Integer, ForeignKey('patient.id'))
    act_id = Column(Integer, ForeignKey('act.id'))

    act = relationship("Act", back_populates ="reminders")
    patient = relationship("Patient", back_populates ="reminders")

#####################################
# ENCRYPTED
# all entries written to table Patient are encrypted
# using **password**
# in final stages, ask for password at load time
class Patient(Base):
    __tablename__="patient"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    ramq = Column(String)
    mrn = Column(String)
    dob = Column(DateTime)
    phone = Column(String)
    fname = Column(String)
    lname = Column(String)
    postalcode = Column(String)

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by = Episode_Work.id, back_populates = "patient")
    reminders = relationship("Reminders", order_by = "desc(Reminders.dateCreated)", back_populates = "patient")
    # reminder = relationship("reminder", back_populates="patient")

    def __init__(self, values):
        for k, v in values.items():
            #setattr(self, k, f.encrypt(v.encode('UTF-8')))
            setattr(self, k, v)
        session.add(self)
        session.commit()

    def get_columns(self):
        return self.__table__.c.keys()

    def get_decrypted_dic(self):
        dic = {}
        for entry in self.__table__.columns.keys():
            dic[entry] = getattr(self,entry)
            # if type(getattr(self, entry)) is not bytes:
            #     dic[entry] = getattr(self,entry)
            # else:
            #     dic[entry] = f.decrypt(getattr(self,entry)).decode('UTF-8')
        return dic

    def add_EOW(self):
        EOW = Episode_Work(self)
        EOW.add_act()

    def __str__(sefl):
        return "{} {}, MRN: {}, RAMQ: {}".format(self.fname, self.lname, self.mrn, self.ramq)

    def __repr__(self):
        return "{}".format(self.fname)

#####################################

def get_billingcode(criteria):
    return session.query(BillingCode).filter_by(abbreviation = criteria['abbreviation'],\
                                                location = criteria['location'],\
                                                category = criteria['category']).first()

def get_facility(criteria):
    #may need to indicate facility as a tupple (hospital,secteur) see RAMQ
    return session.query(Facility).filter_by(abbreviation = criteria['facility']).first()

#####################################
# def create_act(EOW, patient):
#     act_data = get_act_data(EOW, patient)
#     #act = Act(EOW, patient, bed, billingcode, facility, secteur, inpt, wasbilled)
#     act = Act(**act_data) #find out how to unpack dictionary
#     session.add(act)
#     session.commit()
#     return act
#
# def create_encounter():
#     patient = Patient(**get_new_patient_data())
#     EOW = Episode_Work(patient)
#     act = create_act(**get_act_data(EOW))
#
# def get_new_patient_data():
#     #return dialogs(newpatientdata)
#     pass
#
# # class followup_list(object):
# #     def __init__(self, table, function):
#         self.data = session.query(table).filter_by(function).all()

def build_dummy():
    #get headings from patient table
    headings = ['fname','lname','ramq','mrn','phone']
    #dummy patients
    amir = ['amir','ibrahim','fsdfr23rwer','342432432', '432234234']
    badr = ['badr','kykuyk','32432gdfgd','09893435', '564546543']
    tito = ['tito','rweght','gdfgh87867','8768768', '676732134']
    rabi = ['rabi','fsdfewr','hkjlh8786','43256576', '112232349']
    patients = [amir, badr,tito,rabi]

    for p in patients:
        Patient(dict(zip(headings, p)))

#####################################

if __name__ == '__main__':
    pass
