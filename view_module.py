import ui
from control_module import *

##################################
class master_view(ui.View):
	def __init__(self):
		# This will also be called without arguments when the view is loaded from a UI file.
		# You don’t have to call super. Note that this is called *before* the attributes
		# defined in the UI file are set. Implement `did_load` to customize a view after
		# it’s been fully loaded from a UI file.
		self.width = 375
		self.height = 667

	def did_load(self):
		# This will be called when a view has been fully loaded from a UI file.
		pass

	def will_close(self):
		# This will be called when a presented view is about to be dismissed.
		# You might want to save data here.
		pass

	def draw(self):
		# This will be called whenever the view’s content needs to be drawn.
		# You can use any of the ui module’s drawing functions here to render
		# content into the view’s visible rectangle.
		# Do not call this method directly, instead, if you need your view
		# to redraw its content, call set_needs_display().
		# Example:
		#path = ui.Path.oval(0, 0, self.width, self.height)
		#ui.set_color('red')
		#path.fill()
		#img = ui.Image.named('ionicons-beaker-256')
		#img.draw(0, 0, self.width, self.height)
		pass

	def layout(self):
		# This will be called when a view is resized. You should typically set the
		# frames of the view’s subviews here, if your layout requirements cannot
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

##################################
# Front view
class front_view(masterview):
    #subviews:
    ##buttons
    buttonlist = ['New Episode', 'Followups', 'Reminders', 'Notes', 'Analytics']
    for bu in buttonlist:
        button = ui.Button()
        button.name = bu
        button.background = 'coral'
        self.add_subview(button)
    ##
    incomplete acts list: tableview
    pass

##################################
# add patient view
class add_patient_view(masterview):
    pass


##################################
# add act view class
class add_act_view(masterview):
    pass

##################################
# show followups view class
class show_followups_view(masterview):
    list = ui.tableview()

##################################
# show reminders view class
class show_reminders(masterview):
    list = ui.tableview()

##################################
# show notes view class
class show_notes_view(masterview):
    list = ui.tableview()


if __name__ == '__main__':
    front_view()
