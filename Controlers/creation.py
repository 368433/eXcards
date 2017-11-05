
import ui
import console

from restartdb import *

class MyTextFieldDelegate (object):

	def textfield_should_begin_editing(self, textfield):
		return True

	def textfield_did_begin_editing(self, textfield):
		pass

	def textfield_did_end_editing(self, textfield):

		#Autoformating textfield entry at end of editing
		if textfield.name == 'fname' :
			textfield.text = textfield.text.title()
			textfield.superview['searchasyoutype'].send_to_back()
			textfield.superview['searchasyoutype'].alpha = 0.0

		if textfield.name == 'lname' :
			textfield.text = textfield.text.title()

		if textfield.name == 'mrn':
			try:
				assert (textfield.text.isdigit())
			except:
				console.hud_alert("MRN was not all digits")
				textfield.text = ''


	def textfield_should_return(self, textfield):
		textfield.end_editing()
		return True

	def textfield_should_change(self, textfield, range, replacement):
		return True

	def textfield_did_change(self, textfield):
		if textfield.name == 'fname':
			textfield.superview['searchasyoutype'].bring_to_front()
			textfield.superview['searchasyoutype'].alpha = 1.0
			table = textfield.superview['searchasyoutype']['tableview1']
			session = Session()
			newlist = session.query(Patient.fname, Patient.lname).filter(Patient.fname == textfield.text).all()
			table.data_source = ui.ListDataSource(newlist)
			table.reload()
			table.reload_data()
			session.close()

def getsegments():
	session = Session()
	acts = session.query(distinct(BillingCode.abbreviation)).filter(BillingCode.abbreviation != '').all()
	session.close()
	labels=[]
	for a in acts:
		labels.append(a[0])
	return labels

def spawnevent(sender):
	#get the dictionnary of values entered in createUI
	the_dict = get_entered_values(sender.superview)

	#create a session
	session = Session()

	########################################################
	# CREATE AND INITIALIZE A PATIENT
	p = Patient()
	p.lname = the_dict['lname']
	p.fname = the_dict['fname']
	p.ramq = the_dict['ramq']
	p.mrn = the_dict['mrn']
	p.phone = the_dict['phone']
	p.postalcode = the_dict['postalcode']
	session.add(p)
	session.commit()
	########################################################


	########################################################
	# FIND BINDING FOR LOCATION, PHYSICIAN, BILLING CODE
	loc = session.query(Facility).\
				filter(Facility.name == the_dict['act_hospital']).first()

	md = session.query(Physician).\
				filter(Physician.lname == the_dict['referringmd']).first()


	bill = session.query(BillingCode).\
				filter(BillingCode.abbreviation == the_dict['abbreviation']).\
				filter(BillingCode.category == the_dict['category']).\
				filter(BillingCode.location == the_dict['location']).first()
	########################################################

	########################################################
	a = Act()
	e = Episode_Work()
	r = Referral()
	dx = Sentinel_Dx()
	m = ModifiedAct()
	session.add(a)
	session.add(e)
	session.add(r)
	session.add(dx)
	session.add(m)

	#session.commit()
	########################################################

	#Set boolean is_inpt based on value of location for both act and episode of work
	if the_dict['location'] in ['ClinEx', 'CPriv']:
		a.is_inpt = False
		e.is_inpt = False
	else:
		a.is_inpt = True
		e.is_inpt = True

	#find the modifier
	#code to find the modifier in database

	#create the associations
	a.episode_work = e
	a.billingcode = bill
	a.facility = loc
	m.act = a
	#m.modifier = mod
	dx.episode_work =e
	e.patient = p
	r.episode_work = e
	r.act = a

	#session.commit()


	#create a sentinel diagnosis entry
	dx.predicted_dx = the_dict['diagnosis']
	#persist sentinel to memory
	session.commit()

	#close session
	session.close()
	sender.superview.superview.close()



# utility function proposed for the ui.View class - code from ccc
def get_entered_values(self):
	the_dict = {}
	for subview in self.subviews:
		if subview.name:
			if isinstance(subview, (ui.TextField, ui.TextView)):
				the_dict[subview.name] = subview.text
			elif isinstance(subview, (ui.Slider, ui.Switch)):
				the_dict[subview.name] = subview.value
			elif isinstance(subview, (ui.SegmentedControl)):
				the_dict[subview.name] = subview.segments[subview.selected_index]
			elif isinstance(subview, ui.DatePicker):
				if subview.mode == ui.DATE_PICKER_MODE_COUNTDOWN:
					the_dict[subview.name] = subview.countdown_duration
				else:
					the_dict[subview.name] = subview.date
	return the_dict
