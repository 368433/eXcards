import ui
import analytics
from followup import *
from creation import *

def load_create(sender):
	v = ui.load_view('views/create')
	v.present('sheet')
	#v['createscrollview']['fname'].delegate = MyTextFieldDelegate()

def load_followups(sender):
	v = ui.load_view('views/followups')
	table = v['fulist']
	table.data_source = table.delegate = buildfu()
	v.present('sheet')

def load_notes(sender):
	v = ui.load_view('views/notes')
	v.present('sheet')

def load_analytics(sender):
	v = ui.load_view('views/analytics')
	v.present('sheet')
	button1 = v['segmentedcontrol1']
	if button1.selected_index == 0:
		v['textview1'].text = 'loaded'
	button1.action = analytics.button_action

def load_reminders(sender):
	v = ui.load_view('views/analytics')
	v.present('sheet')


m = ui.load_view('views/main')
m.present('sheet')

