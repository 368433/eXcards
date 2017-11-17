import ui

def button_action(sender):
	v = sender.superview
	button1 = v['segmentedcontrol1']
	if button1.selected_index == 0:
		v['textview1'].text = 'this'
	elif button1.selected_index == 1:
		v['textview1'].text = 'AAAHHHHHH'
	elif button1.selected_index == 2:
		v['textview1'].text = 'BONNNNNN'
	elif button1.selected_index == 3:
		v['textview1'].text = 'BROOOOOOO'
