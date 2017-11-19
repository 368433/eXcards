import time, SCdialogs, platform, ui, console
from DMM1 import *
import threading

#####################################
# VIEW CLASSES
class PatientLists(object):

    # def __init__(self):
    # 	self.items = self.get_items()
    # 	super().__init__(self.items)
    # 
    # 	self.action = self.add_act
    	
    def __init__(self, view):
        self.table= ui.TableView()
        self.items = self.get_items()
        self.data = MODListDataSource(self.items)
        self.data.font = ('Courier', 14)
        self.data.detail_font = ('Courier', 11)
        self.data.number_of_lines = 2
        self.table.delegate = self.table.data_source = self.data
        self.table.frame = (0,0, view.width, view.height)
        self.data.action = self.add_act
        self.data.accessory_action = self.accessory_patient
        self.data.edit_action = self.show_patient_overview

    def get_items(self):
        EOW = get_active_EOW()
        items = []
        for e in EOW:
        	if e.act == []:
        		act = None
        	else:
        		act = e.act[-1]
        	items.append((e.patient, e, act, e.sentinel_dx))
        #EOW = session.query(Episode_Work).filter_by(timeEnd = None).all()
        return items
        #return get_incomplete_EOW()

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

class MODListDataSource(ui.ListDataSource):
	def tableview_cell_for_row(self, tv, section, row):
		item = self.items[row]
		cell = ui.TableViewCell('subtitle')
		cell.text_label.number_of_lines = self.number_of_lines
		if isinstance(item, dict):
			cell.text_label.text = item.get('title', '')
			img = item.get('image', None)
			if img:
				if isinstance(img, basestring):
					cell.image_view.image = Image.named(img)
				elif isinstance(img, Image):
					cell.image_view.image = img
			accessory = item.get('accessory_type', 'none')
			cell.accessory_type = accessory
		elif isinstance(item, tuple):
			cell.text_label.text = str(item[0])
			cell.detail_text_label.text = str(item[1]) + ' - ' + str(item[2])
		else:
			cell.text_label.text = str(item)
		if self.text_color:
			cell.text_label.text_color = self.text_color
		if self.highlight_color:
			bg_view = View(background_color=self.highlight_color)
			cell.selected_background_view = bg_view
		if self.font:
			cell.text_label.font = self.font
		if self.detail_font:
			cell.detail_text_label.font = self.detail_font
		return cell

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
        return get_incomplete_acts()

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
# HELPER FUNCTIONS
def get_act_data(EOW, patient):
    actkeys = Act().__table__.columns.keys()
    fields = [{'type':'segmented','key':'facility' ,'value':'HPB|ICM|PCV' ,'title':'Facility'},
              {'type':'segmented','key':'abbreviation' ,'value':'VP|C|TW|VC' ,'title':'Abbreviation'},
              {'type':'segmented','key':'location' ,'value':'CHCD|Cprive' ,'title':'Location'},
              {'type':'segmented','key':'category' ,'value':'ROUT|MIEE' ,'title':'Category'},
              {'type':'switch','key':'is_inpt' ,'value':True ,'title':'Is Inpatient'},
              {'type':'number','key':'bed' ,'value':'' ,'title':'Bed'},
              {'type':'segmented','key':'secteur' ,'value':'ClinExt|GenWard' ,'title':'Secteur'}]
    process = SCdialogs.SCform_dialog(title = 'New Act', fields = fields)
    process['EOW_id'] = EOW.id
    process['patient_id'] = patient.id
    process['billingcode'] = get_act_billing(process)
    process['facility_secteur'] = get_facility_secteur(process)
    return process

def create_new_patient():
    fields = [{'type':'text','key':'fname' ,'value':'' ,'title':'First Name'},
              {'type':'text','key':'lname' ,'value':'' ,'title':'Last Name'},
              {'type':'segmented','key':'sex' ,'value':'Male|Female' ,'title':'Sex'},
              {'type':'text','key':'ramq' ,'value':'' ,'title':'RAMQ'},
              {'type':'text','key':'mrn' ,'value':'' ,'title':'MRN'},
              {'type':'date','key':'dob' ,'title':'Date of birth'},
              {'type':'number','key':'phone' ,'value':'' ,'title':'Phone'},
              {'type':'text','key':'postalcode' ,'value':'' ,'title':'Postal Code'}]
    data = SCdialogs.SCform_dialog(title='New patient', fields = fields)
    if data != None:
        return Patient(**data)

def set_sentinel_dx(EOW):
	fields = [{'type':'text','key':'predicted_dx' ,'value':'' ,'title':'1st predic. Dx'},
	{'type':'text','key':'predicted_dx' ,'value':'' ,'title':'2nd predic. Dx'},
	{'type':'text','key':'predicted_dx' ,'value':'' ,'title':'3rd predic. Dx'}]
	
	data = SCdialogs.SCform_dialog(title='New patient', fields = fields)
	if data != None:
		for dx in data.values():
			values = {}
			values['EOW_id'] = EOW.id
			values['predicted_dx']= dx
			Sentinel_Dx(**values)

def create_new_EOW():
    new_patient = create_new_patient()
    if new_patient:
    	EOW = new_patient.add_EOW()
    	EOW.add_act(**get_act_data(EOW, new_patient))
    	set_sentinel_dx(EOW)

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

def parsemainview(sender):
    session = Session()
    if sender.selected_index == 0:
    	#console.hud_alert("this is new", 'success', 0.4)
    	sender.selected_index = -1
    	create_new_EOW()

class frontView (ui.View):
	def will_close(self):
		pass
		#session.close()
		
if __name__ == '__main__':
    v = ui.load_view('category')
    customlistview = v['view1']
    #patientlist = PatientLists(customlistview)
    #customlistview.add_subview(patientlist.table)
    v['segmentedcontrol1'].selected_index = -1
    v['segmentedcontrol1'].action = parsemainview
    v.present('sheet')


