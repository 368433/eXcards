from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Sequence
from sqlalchemy import create_engine, Table, Text, distinct
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time


Base = declarative_base()
static_engine = create_engine('sqlite:///static.db', echo=False)
dynamic_engine = create_engine('sqlite:///dynamic.db', echo=False)
static_session = sessionmaker(bind=static_engine)
dynamic_session = sessionmaker(bind=dynamic_engine)


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
#     pass

#####################################
# DYNAMIC
class Act(Base):
    __tablename__ = 'act'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    bed = Column(String(5))
    clinlabadmin = Column(Integer) #clin = 1, lab = 2, admin = 3
    subject_id = Column(Integer) # the id of a patient or null if meeting or labevent
    #BOOLEANS
    was_billed = Column(Boolean, default=False)
    #ForeignKey
    billingcode_id = Column(Integer, ForeignKey('billingcode.id'))
    facility_id = Column(Integer, ForeignKey('facility.id'))
    episode_work_id = Column(Integer, ForeignKey('episode_work.id'))
    #note_id = Column(Integer, ForeignKey('notedatabase.id'))

    #DEFINING RELATIONSHIPS
    billingcode = relationship("BillingCode" , back_populates="act")
    facility = relationship("Facility", back_populates="act")
    episode_work = relationship("Episode_Work", back_populates="act")
    #note = relationship("notedatabase", foreign_keys=[note_id])
    #reminder = relationship("reminder", back_populates="act")

    def __repr__(self):
        return "<Act(id='%s', timeStart='%s', billingcode_id='%s')>"%(
                self.id, self.timeStart, self.billingcode_id)

class Episode_Work(Base):
    __tablename__='episode_work'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    #FOREIGN KEYS
    patient_id = Column(Integer, ForeignKey('patient.id'))
    #BOOLEANS
    is_clinical = Column(Boolean, default=False, nullable=False)
    is_inpt = Column(Boolean, default = True, nullable = False)
    is_completed = Column(Boolean, default = False, nullable = False)

    #RELATIONSHIPS
    act = relationship("Act", order_by = "desc(Act.timeStart)", back_populates='episode_work')
    patient = relationship("Patient", back_populates ="episode_work")
    sentinel_dx = relationship("Sentinel_Dx", back_populates = 'episode_work')

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
class Patient(Base):
    __tablename__="patient"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    ramq = Column(String(16), unique = True)
    mrn = Column(String (10), unique = True)
    dob = Column(DateTime)
    phone = Column(String(10))
    fname = Column(String (15))
    lname = Column(String (15))
    postalcode = Column(String(6))

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by = Episode_Work.id, back_populates = "patient")
    # reminder = relationship("reminder", back_populates="patient")

    def __init__(self, **kwargs):
        for entry in kwargs:
            if entry in self.__table__.columns.keys():
                self.entry
    def __str__(sefl):
        return "{} {}, MRN: {}, RAMQ: {}".format(self.fname, self.lname, self.mrn, self.ramq)

    def __repr__(self):
        return "{}".format(self.fname)


#implement after ICD 11 published
# # class ICD(Base):
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
#
#####################################

if __name__ == '__main__':
    Base.metadata.create_all(static_engine)
    Base.metadata.create_all(dynamic_engine)
