from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Sequence
from sqlalchemy import create_engine, Table, Text, distinct
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from cryptography.fernet import Fernet
import base64, os, time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import time

# #############################################################
# import base64, os
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# #############################################################
# # password key to encrypt and decrypt Patient entries
# password = b'amiribrahim'
# salt = os.urandom(16)
# kdf = PBKDF2HMAC(
#     algorithm = hashes.SHA256(),
#     length = 32,
#     salt = salt,
#     iterations = 100000,
#     backend = default_backend()
# )
# key = base64.urlsafe_b64encode(kdf.derive(password))
# f = Fernet(key)

#############################################################
# ENGINE initialization
Base = declarative_base()
static_engine = create_engine('sqlite:///static.db', echo=False)
dynamic_engine = create_engine('sqlite:///dynamic.db', echo=False)
static_session = sessionmaker(bind=static_engine)
dynamic_session = sessionmaker(bind=dynamic_engine)
session = dynamic_session()

#############################################################
# password key to encrypt and decrypt Patient entries
patientpwd = b'fWB2ISaUuCJhLzZCGxGTLW2yDE2zmfPnxzWeEiN_7TM='
f = Fernet(patientpwd)


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

  def __repr__(self):
      return "<BillingCode(id='%s', abbreviation = '%s', code='%s', description='%s', fee='%s')>" % (
                          self.id, self.abbreviation, self.code, self.description, self.fee) # done

class Facility(Base):
    __tablename__="facility"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    name = Column(String)
    postal_code = Column(String(6))
    phone = Column(String(10))
    address =  Column(String)

    act = relationship("Act", back_populates="facility")

    def __repr__(self):
        return "<Facility(id='%s', name = '%s', phone='%s')>" % (self.id, self.name, self.phone) # done

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

# class ICD(Base):
#     __tablename__="icd"
#
#     id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
#     code = Column(String(6))
#     description = Column(String)
#
#     # RELATIONSHIPS
#     sentinel_dx = relationship("Sentinel_Dx")
#
#     def __repr__(self):
#         return "<ICD(id={}, code={}, description={})>".format(self.id, self.code, self.description)
#     pass

#####################################
# DYNAMIC
class Act(Base):
    __tablename__ = 'act'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    bed = Column(String(5))
    subject_id = Column(Integer) # the id of a patient or null if meeting or labevent
    #BOOLEANS
    was_billed = Column(Boolean, default=False)
    is_inpt =  Column(Boolean)
    #ForeignKey
    billingcode_id = Column(Integer, ForeignKey('billingcode.id'))
    facility_id = Column(Integer, ForeignKey('facility.id'))
    episode_work_id = Column(Integer, ForeignKey('episode_work.id'))
    #secteur_activite_id = Column(Integer, ForeignKey('facility.id'))
    patient_id = Column(Integer, ForeignKey('patient.id'))
    #note_id = Column(Integer, ForeignKey('notedatabase.id'))

    #DEFINING RELATIONSHIPS
    billingcode = relationship("BillingCode" , back_populates="act")
    facility = relationship("Facility", back_populates="act")
    episode_work = relationship("Episode_Work", back_populates="act")
    #note = relationship("notedatabase", foreign_keys=[note_id])
    #reminder = relationship("reminder", back_populates="act")

    def __init__(self, EOW, patient, bed, billingcode, facility, secteur, inpt, wasbilled):
        self.episode_work_id = EOW.id
        self.patient_id = patient.id
        self.bed = bed
        self.billingcode_id = billingcode.id
        self.facility_id = facility.id
        self.secteur_activite_id = secteur.id
        self.is_inpt = inpt
        self.was_billed = wasbilled

    def __repr__(self):
        return "<Act(id='%s', timeStart='%s', billingcode_id='%s')>"%(
                self.id, self.timeStart, self.billingcode_id)

class Episode_Work(Base):
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

    # def add_act(self, patient):
    #     act = get_act_data(self, patient)
    #     session.add(act)
    #     session.commit()

    def __repr__(self):
        return "{}".format(self.id)

class Sentinel_Dx(Base):
    __tablename__="sentinel_dx"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    episode_work_id = Column(Integer, ForeignKey('episode_work.id'))
    predicted_dx = Column(String)
    final_dx = Column(String)

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by='Episode_Work.id', back_populates = 'sentinel_dx')

    # implement ICD portion when ICD 11 out
    # icd_id = Column(Integer, ForeignKey('icd.id'))
    # icd_code = relationship("ICD", back_populates="sentinel_dx")
    def __repr__(self):
        return "<Sentinel_Dx(id = '%s')>"%(self.id)

# class Notes(Base):
#     pass
#
# class Reminders(Base):
#     pass
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
    # reminder = relationship("reminder", back_populates="patient")

    def __init__(self, values):
        # assumes values is a dictionary containing column data
        # if 'fname' in dico:
        #     self.fname = dico['fname']
        # for entry in kwargs:
        #     if entry in self.__table__.columns.keys():
        #         self.__dict__[entry] = f.encrypt(kwargs[entry].encode('UTF-8'))
        #         #self.__dict__[entry] = kwargs[entry]
        for k, v in values.items():
            setattr(self, k, v)
        session.add(self)
        session.commit()

    def get_columns(self):
        return self.__table__.c.keys()

    def get_decrypted_dic(self):
        dic = {}
        for entry in self.__table__.columns.keys():
            if type(self.__dict__[entry]) is not bytes:
                dic[entry] = self.__dict__[entry]
            else:
                value = f.decrypt(self.__dict__[entry])
                dic[entry] = value.decode('UTF-8')
        return dic

    def __str__(sefl):
        return "{} {}, MRN: {}, RAMQ: {}".format(self.fname, self.lname, self.mrn, self.ramq)

    def __repr__(self):
        return "{}".format(self.fname)

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
# def get_act_data(EOW):
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
    Base.metadata.create_all(static_engine)
    Base.metadata.create_all(dynamic_engine)
    # remove after testing phase
    build_dummy()
