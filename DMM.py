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
  code = Column(String)
  abbreviation = Column(String(2))
  description = Column(String)
  fee = Column(Float(5))
  location = Column(String(5))
  category = Column(String(5))

  def get_billingcode(self):
      return self.code

  def get_billingfee(self):
      return self.fee

class Facility(Base):
    """
    le numero d'etablissement ou d'installation (5 chiffres) se compose comme suit
    le 1er chiffre represente la categorie d'etablissement [0communautaire][4universitaire]
    les 3 chiffres du centre constituent le numero d'etablissement
    le dernier chiffre = categorie unite de soins (1=clinique externe) AKA SECTEUR
    """
    __tablename__="facility"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    abbreviation = Column(String)
    postal_code = Column(String(6))
    phone = Column(String(10))
    ramqnumber = Column(String)

    def __repr__(self):
        return "Facility(id='{}', name = '{}', phone='{}')".format(self.id, self.name, self.phone) # done

class Secteur(Base):
    __tablename__="secteur"

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    abbreviation = Column(String)
    name = Column(String)
    ramqnumber = Column(String)

    def __repr__(self):
        return "Secteur(id='{}', name = '{}', abbr='{}')".format(self.id, self.name, self.abbreviation)

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
        return "physician(id={}, license ={}, first name = {}, last name = {})".format(self.id, self.license, self.fname, self.lname)

class ICDCode(Base):
    __tablename__="icdcode"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    code = Column(String(6), primary_key=True)
    description = Column(String)

    # RELATIONSHIPS
    sentinel_dx = relationship("Sentinel_Dx", back_populates = 'icdcode')

    def __repr__(self):
        return "ICD(id={}, code={}, description={})".format(self.id, self.code, self.description)

#####################################
# DYNAMIC
class Act(Base):
    __tablename__ = 'act'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    bed = Column(String(5))
    facility_secteur = Column(String(5)) #(ddddX,XXXXd)
    #num_facility = Column(String(5)) #ddddX
    billingcode = Column(String) # a tuple of (code,abbrv,loc,cat)
    #BOOLEANS
    was_billed = Column(Boolean, default=False)
    is_inpt =  Column(Boolean)
    #ForeignKey
    EOW_id = Column(Integer, ForeignKey('episode_work.id'))
    patient_id = Column(Integer, ForeignKey('patient.id'))

    #DEFINING RELATIONSHIPS
    episode_work = relationship("Episode_Work", back_populates="act")
    notes = relationship("Notes", order_by = "desc(Notes.dateCreated)", back_populates='act')
    reminders = relationship("Reminders", back_populates="act")

    def __init__(self, **values):
        set_values(self, **values)
        session.add(self)
        session.commit()

    def mark_completed(self):
        self.timeEnd = datetime.utcnow()
        session.commit()

    def is_active(self):
        return self.timeEnd == None

    def __repr__(self):
        return "Act(id='{}', timeStart='{}', billingcode_id='{}')".format(
                self.id, self.timeStart, self.billingcode_id)

class Episode_Work(Base):
    # equivalent to Card
    __tablename__='episode_work'

    id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
    timeStart = Column(DateTime, default=datetime.utcnow(), nullable=False)
    timeEnd = Column(DateTime)
    lastEdit = Column(DateTime)
    nextVisit = Column(DateTime)
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

    def add_act(self, **values):
        act = Act(**values)
        session.add(act)
        session.commit()

    def mark_completed(self):
        self.timeEnd = datetime.utcnow()
        session.commit()

    def is_active(self):
        return self.timeEnd == None

    def get_dic(self):
        return {'Started':self.timeStart, 'Diagnosis':self.sentinel_dx[0]}

    def to_see_today(self):
        return self.nextVisit.date() == datetime.today().date()

    def __repr__(self):
        patient = self.patient.get_decrypted_dic()
        fname, lname, MRN = patient['fname'], patient['lname'], patient['mrn']
        last_act = self.act[-1].timeStart.strftime('%d-%b-%Y')
        return "{0} {1}, MRN {2} \nlast visit: {3}".format(fname, lname, MRN, last_act)

class Sentinel_Dx(Base):
    __tablename__="sentinel_dx"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    EWO_id = Column(Integer, ForeignKey('episode_work.id'))
    icd_code = Column(String, ForeignKey('icdcode.code'))
    predicted_dx = Column(String)
    final_dx = Column(String)

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by='Episode_Work.id', back_populates = 'sentinel_dx')
    icdcode = relationship("ICDCode", back_populates = 'sentinel_dx')

    def __init__(self, **values):
        set_values(self, **values)
        self.final_dx = None
        session.add(self)
        session.commit()

    def set_final_dx(self, dx):
        # assumes dx is a string
        self.final_dx = dx
        session.commit()

    def accuracy(self):
        if final_dx == None:
            return 0
        elif final_dx == predicted_dx:
            return 1
        else:
            return 0

    def __repr__(self):
        return "Sentinel_Dx(id = '{}')".format(self.id)

class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    content = Column(String)
    imagepath = Column(String)
    dateCreated = Column(DateTime, default=datetime.utcnow(), nullable=False)
    dateModified = Column(DateTime, default=datetime.utcnow(), nullable=False)
    act_id = Column(Integer, ForeignKey('act.id'))

    act = relationship("Act", back_populates ="notes")

    def __init__(self, imagepath, content, act_id):
        self.imagepath = imagepath
        self.content = content
        self.act_id = act_id
        session.add(self)
        session.commit()

    def add_content(self, content):
        self.content += content
        self.dateModified = datetime.utcnow()
        session.commit()

    def get_imagepath(self):
        return self.imagepath

    def get_content(self):
        return self.content

    def __repr__(self):
        return "Last Modified: {}\nContent: {:.50}".format(self.dateModified, self.content)

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

    def __init__(self, **values):
        if values:
            set_values(self, **values)
            session.add(self)
            session.commit()

    def get_columns(self):
        return self.__table__.c.keys()

    def modify_data(self, values):
        #assumes values is a dictionary of values corresponding
        #to self table entries
        set_values(self, **values)
        session.commit()

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
# HELPER FUNCTIONS

def set_values(table, encrypted=False, **values):
    """
    assumes table is a table defined in schema
    and values a dictionary of values
    """
    for k, v in values.items():
        if k in table.__table__.columns.keys():
            if encrypted:
                setattr(table, k, f.encrypt(v.encode('UTF-8')))
            else:
                setattr(table, k, v)

def get_act_billing(criteria):
    abb = criteria['abbreviation']
    loc = criteria['location']
    cat = criteria['category']
    billingcode = session.query(BillingCode).\
                filter_by(abbreviation = abb, location = loc, category = cat).first()
    return (billingcode, abb, loc, cat)

def get_facility_secteur(criteria):
    #may need to indicate facility as a tupple (hospital,secteur) see RAMQ
    facility = session.query(Facility).filter_by(abbreviation = criteria['facility']).first().ramqnumber
    secteur =  session.query(Facility).filter_by(abbreviation = criteria['secteur']).first().ramqnumber
    return facility +','+ secteur

#####################################

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
