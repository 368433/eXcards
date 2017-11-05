
# coding: utf-8

import ui
import console

from restartdb import *
from creation import get_entered_values

def viewfulist(sender):
	updatelist(sender.superview.superview['seginoutpt'])
	sender.superview.superview.remove_subview(sender.superview)

def buildfu():
	#called by the initial loading of followupview
	return fulistdatasource(generatefulist(0))

class fulistdatasource(object):

	def __init__(self,items):
		self.items = items
	
	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(self.items)

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		patient = self.items[row][0]
		episode = self.items[row][1]
		cell = ui.TableViewCell('subtitle')
		cell.text_label.text = patient.fname + ' ' + patient.lname + ', MRN: ' + patient.mrn
		session = Session()
		episode = session.query(Episode_Work).filter(Episode_Work.id == episode.id).one()
		lastvisit = episode.act[-1].timeStart.strftime('%d-%b-%Y')
		diagnosis = episode.sentinel_dx[0].predicted_dx
		cell.detail_text_label.text = 'Last visit: {:<18.18}{:>18.18}'.format(lastvisit, diagnosis)
		session.close()
		cell.text_label.font = ('Courier', 16)
		cell.detail_text_label.font = ('Courier', 11)
		return cell

	def tableview_title_for_header(self, tableview, section):
		# Return a title for the given section.
		# If this is not implemented, no section headers will be shown.
		#return 'Some Section'
		pass

	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		return True

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		return True

	def tableview_delete(self, tableview, section, row):
		# Called when the user confirms deletion of the given row.
		pass

	def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
		# Called when the user moves a row with the reordering control (in editing mode).
		pass
		
	def tableview_did_select(self, tableview, section, row):
		editview = ui.load_view('views/editfollowup')
		editview.name = str(self.items[row][1].id)
		tableview.superview.add_subview(editview)

	def tableview_did_deselect(self, tableview, section, row):
		# Called when a row was de-selected (in multiple selection mode).
		pass

	def tableview_title_for_delete_button(self, tableview, section, row):
		# Return the title for the 'swipe-to-***' button.
		return 'Delete'

def generatefulist(is_outpt):
	session = Session()
	followuplist = session.query(Patient, Episode_Work).filter(Episode_Work.is_completed == False, Episode_Work.is_inpt != is_outpt, Patient.id ==  Episode_Work.patient_id).order_by(Episode_Work.id).all()
	session.close()
	return followuplist

def updatelist(sender):
	mainview = sender.superview
	table = mainview['fulist']
	data = generatefulist(sender.selected_index)
	table.data_source.items = data
	table.reload()
	table.reload_data()
	
#class fulistdelegate (object):
	
def addact(sender):
	the_dict = get_entered_values(sender.superview)
	editscreen = sender.superview.superview
	a = Act()

	session = Session()
	a.billingcode = session.query(BillingCode).\
				filter(BillingCode.abbreviation == the_dict['abbreviation']).\
				filter(BillingCode.category == the_dict['category']).\
				filter(BillingCode.location == the_dict['location']).first()
	
	a.facility = session.query(Facility).\
				filter(Facility.name == the_dict['act_hospital']).first()
	
	a.episode_work_id = int(editscreen.name)
	session.add(a)
	session.commit()

	if the_dict['location'] in ['ClinEx', 'CPriv']:
		a.is_inpt = False
		a.episode_work.is_inpt = False
	else:
		a.is_inpt = True
		a.episode_work.is_inpt = True
	session.commit()
	session.close()
	
	#update main follow up list with the changes made in edit view
	#update is done with the segmented in/outpt state prior to edit view
	updatelist(editscreen.superview['seginoutpt'])
	
	#close the edit followup screen view
	editscreen.superview.remove_subview(editscreen)

