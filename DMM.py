from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Sequence
from sqlalchemy import create_engine, Table, Text, distinct
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
#from cryptography.fernet import Fernet
import time, SCdialogs, platform, ui, console
from random import randint


# if not platform.system().startswith('iP'):
#     import pandas as pd
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
engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

#############################################################
# password key to encrypt and decrypt Patient entries
# patientpwd = b'fWB2ISaUuCJhLzZCGxGTLW2yDE2zmfPnxzWeEiN_7TM='
# f = Fernet(patientpwd)

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

class ICD(Base):
    __tablename__="icd"

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
    predicted_dx = Column(String)
    final_dx = Column(String)

    # RELATIONSHIPS
    episode_work = relationship("Episode_Work", order_by='Episode_Work.id', back_populates = 'sentinel_dx')

    # implement ICD portion when ICD 11 out
    # icd_id = Column(Integer, ForeignKey('icd.id'))
    # icd_code = relationship("ICD", back_populates="sentinel_dx")
    def __repr__(self):
        return "<Sentinel_Dx(id = '%s')>"%(self.id)

class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    content = Column(String)
    image = Column(string)
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
# VIEW CLASSES
class PatientLists(object):

    def __init__(self, view):
        self.table= ui.TableView()
        self.items = self.get_items()
        self.data = ui.ListDataSource(items)
        self.table.delegate = self.table.data_source = self.data
        self.table.frame = view.frame
        self.data.action = self.add_act
        self.data.accessory_action = self.accessory_patient
        self.data.edit_action = self.show_patient_overview

    def get_items(self):
        return session.query(Episode_Work).filter_by(timeEnd = None).all()

    def add_act(self, sender):
        #add_followup_act()
        pass

    def mark_completed(self, sender):
        selected_EOW = sender.items[sender.selected_row]
        selected_EOW.mark_completed()
        console.hud_alert("EOW completed", 'success', 0.35)
        sender.items.remove(selected_act)

    def accessory_patient(self, sender):
        pass

    def show_patient_overview(self, sender):
        patient = sender.item[sender.selected_row].patient
        display_patient_overview(patient)

class ActiveConsultsList(object):

    def __init__(self, view):
        self.table= ui.TableView()
        self.items = self.get_items()
        self.data = ui.ListDataSource(items)
        self.table.delegate = self.table.data_source = self.data
        self.table.frame = view.frame
        self.data.action = self.mark_completed
        self.data.accessory_action = self.accessory_consult

    def accessory_consult(self, sender):
        pass

    def get_items(self):
        return session.query(Act).filter_by(timeEnd = None).all()

    def mark_completed(self, sender):
        selected_act = sender.items[sender.selected_row]
        selected_act.mark_completed()
        console.hud_alert("Act marked completed", 'success', 0.30)
        sender.items.remove(selected_act)

class Cards(ui.View):
    def __init__(self, elements):
        # This will also be called without arguments when the view is loaded from a UI file.
        # You don't have to call super. Note that this is called *before* the attributes
        # defined in the UI file are set. Implement `did_load` to customize a view after
        # it's been fully loaded from a UI file.

        # assumes list_todisplay is a list of dictionary of values to be displayed
        # as minicards
        self.width = 375 # OPTIMIZE: set widh and height variables as global at top
        self.height = 667
        self.frame = (0, 0, self.width, self.height)
        self.elements = elements
        cardsize = 80
        spacing = cardsize + 20
        self.background_color = 'white'
        self.scroll = ui.ScrollView()
        self.scroll.flex = 'WH'
        self.scroll.frame = (5, 0, self.width-10, self.height)
        #self.scroll.content_inset = (0,5,0,5)
        self.scroll.content_size = (self.scroll.width, spacing*len(elements))
        for n, data in enumerate(self.elements):
            card = self.make_card(data)
            if n == 0:
                card.frame = (0, 0, self.width, cardsize)
                card.background_color = 0.8
            else:
                card.frame = (0, n*spacing, self.width, cardsize)
            self.scroll.add_subview(card)
        self.add_subview(self.scroll)


    def make_card(self, data):
        l = ui.Label()
        l.text = data.__repr__()
        l.background_color = 0.88
        return l

    def did_load(self):
        # This will be called when a view has been fully loaded from a UI file.
        pass

    def will_close(self):
        # This will be called when a presented view is about to be dismissed.
        # You might want to save data here.
        pass

    def draw(self):
        # This will be called whenever the view's content needs to be drawn.
        # You can use any of the ui module's drawing functions here to render
        # content into the view's visible rectangle.
        # Do not call this method directly, instead, if you need your view
        # to redraw its content, call set_needs_display().
        # Example:
        # path = ui.Path.oval(0, 0, self.width, self.height)
        # ui.set_color('red')
        # path.fill()
        # img = ui.Image.named('ionicons-beaker-256')
        # img.draw(0, 0, self.width, self.height)
        pass

    def layout(self):
        # This will be called when a view is resized. You should typically set the
        # frames of the view's subviews here, if your layout requirements cannot
        # be fulfilled with the standard auto-resizing (flex) attribute.
        pass

    def touch_began(self, touch):
        # Called when a touch begins.
        pass

    def touch_moved(self, touch):
        # Called when a touch moves.
        pass

    def touch_ended(self, touch):
        # Called when a touch ends.
        pass

    def keyboard_frame_will_change(self, frame):
        # Called when the on-screen keyboard appears/disappears
        # Note: The frame is in screen coordinates.
        pass

    def keyboard_frame_did_change(self, frame):
        # Called when the on-screen keyboard appears/disappears
        # Note: The frame is in screen coordinates.
        pass

#####################################
def get_act_data(EOW, patient_id):
    fields = [{'type':'segmented','key':'facility' ,'value':'HPB|ICM|PCV' ,'title':'Facility'},
              {'type':'segmented','key':'abbreviation' ,'value':'VP|C|TW|VC' ,'title':'Abbreviation'},
              {'type':'segmented','key':'location' ,'value':'CHCD|Cprive' ,'title':'Location'},
              {'type':'segmented','key':'category' ,'value':'ROUT|MIEE' ,'title':'Category'},
              {'type':'switch','key':'is_inpt' ,'value':True ,'title':'Is Inpatient'},
              {'type':'number','key':'bed' ,'value':'' ,'title':'Bed'},
              {'type':'text','key':'secteur' ,'value':'' ,'title':'Secteur'}]
    process = SCdialogs.SCform_dialog(title = 'New Act', fields = fields)
    process['EOW_id'] = EOW.id
    process['patient_id'] = patient_id
    process['billingcode_id'] = get_billingcode(process).id
    process['facility_id'] = get_facility(process).id
    #process['secteur_id'] = get_secteur(process)
    return process

def create_new_patient():
    fields = [{'type':'text','key':'fname' ,'value':'' ,'title':'First Name'},
              {'type':'text','key':'lname' ,'value':'' ,'title':'Last Name'},
              {'type':'text','key':'ramq' ,'value':'' ,'title':'RAMQ'},
              {'type':'text','key':'mrn' ,'value':'' ,'title':'MRN'},
              {'type':'date','key':'dob' ,'title':'Date of birth'},
              {'type':'number','key':'phone' ,'value':'' ,'title':'Phone'},
              {'type':'text','key':'postalcode' ,'value':'' ,'title':'Postal Code'}]
    data = SCdialogs.SCform_dialog(title='New patient', fields = fields)
    if data != None:
        return Patient(data)

def create_new_EOW():
    new_patient = create_new_patient()
    if new_patient != None:
    	EOW = Episode_Work(new_patient)
    	EOW.add_act()
    # except :
    # 	console.hud_alert("Could not create patient", 'success', 0.5)

def get_billingcode(criteria):
    return session.query(BillingCode).filter_by(abbreviation = criteria['abbreviation'],\
                                                location = criteria['location'],\
                                                category = criteria['category']).first()

def get_facility(criteria):
    #may need to indicate facility as a tupple (hospital,secteur) see RAMQ
    return session.query(Facility).filter_by(abbreviation = criteria['facility']).first()

def display_patient_overview(patient):
    # dic = self.get_decrypted_dic()
    # #can use list comprehension:
    # #list(x.get_dic() for x in self.episode_work)
    # #  or can map() with labmda
    # #  getdic = lambda x:x.get_dic()
    # #  EOW = list(map(getdic, self.episode_work))
    # EOW = list(x.get_dic() for x in self.episode_work)
    v = Cards([patient] + patient.episode_work)
    v.present('sheet')

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

def build_empty_db():
    try:
        if platform.system().startswith('iP'):
            raise ValueError("You are running on IOS")
        df = pd.read_csv('Model/Billingcodes.csv')
        Base.metadata.create_all(engine)
        df.to_sql('BillingCode, engine')
    except ValueError as msg:
        print(msg)
        print("Databases were not created and not populated. Run on Mac")

def parsemainview(sender):
    if sender.selected_index == 0:
    	#console.hud_alert("this is new", 'success', 0.4)
    	sender.selected_index = -1
    	create_new_EOW()
#####################################

if __name__ == '__main__':
    v = ui.load_view('category')
    v['segmentedcontrol1'].selected_index = -1
    v['segmentedcontrol1'].action = parsemainview
    v['segmentedcontrol1'].selected_index = -1
    v.present('sheet')
