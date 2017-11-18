import dialogs, ui, collections, datetime

import sys
PY3 = sys.version_info[0] >= 3
if PY3:
	basestring = str

class _SCFormDialogController (object):
	def __init__(self, title, sections, done_button_title='Done'):
		self.was_canceled = True
		self.shield_view = None
		self.values = {}
		self.container_view = _SCFormContainerView()
		self.container_view.frame = (0, 0, 500, 500)
		self.container_view.delegate = self
		self.view = ui.TableView('grouped')
		self.view.flex = 'WH'
		self.container_view.add_subview(self.view)
		self.container_view.name = title
		self.view.frame = (0, 0, 500, 500)
		self.view.data_source = self
		self.view.delegate = self
		self.cells = []
		
		self.sections = sections
		
		for section in self.sections:
			section_cells = []
			self.cells.append(section_cells)
			items = section[1]
			for i, item in enumerate(items):
				cell = ui.TableViewCell('value1')
				icon = item.get('icon', None)
				tint_color = item.get('tint_color', None)
				if tint_color:
					cell.tint_color = tint_color
				if icon:
					if isinstance(icon, basestring):
						icon = ui.Image.named(icon)
					if tint_color:
						cell.image_view.image = icon.with_rendering_mode(ui.RENDERING_MODE_TEMPLATE)
					else:
						cell.image_view.image = icon
					
				title_color = item.get('title_color', None)
				if title_color:
					cell.text_label.text_color = title_color
				
				t = item.get('type', None)
				key = item.get('key', item.get('title', str(i)))
				item['key'] = key
				title = item.get('title', '')
				if t == 'segmented':
					value = item.get('value', '')
					self.values[key] = value
					bgcolor = 0.9
					
					#Set up cell
					cell.selectable = False
					#cell.text_label.text = title
					#label_width = ui.measure_string(title, font=cell.text_label.font)[0]
					cell_width, cell_height = cell.content_view.width, cell.content_view.height
					cell.background_color= bgcolor

					
					#Set up scroll view
					scroll = ui.ScrollView()
					scroll_width = cell_width #max(40, cell_width - label_width - 32)
					scroll.frame = (cell_width - scroll_width, 3, scroll_width +70, cell_height-6)
					scroll.shows_horizontal_scroll_indicator = False
					scroll.background_color = bgcolor
					
					#Set up segment
					segment = ui.SegmentedControl()
					segment.segments = item.get('value', '').split("|")
					segment.value = value
					segment.name = key
					segment.action = self.segment_action
					#segment_width = max(40, cell_width - label_width - 32)
					#segment.frame = (cell_width - segment_width, 5, segment_width, cell_height -10)
					segment.background_color = 'white'
					segment_width = max(len(segment.segments)*58, 380)
					segment.frame = (-3, 0, segment_width, scroll.height )
					
					#Combining SUBVIEWS
					scroll.content_size = (len(segment.segments)*60, scroll.height)
					scroll.add_subview(segment)
					cell.content_view.add_subview(scroll)
					
				elif t == 'switch':
					value = item.get('value', False)
					self.values[key] = value
					cell.text_label.text = title
					cell.selectable = False
					switch = ui.Switch()
					w, h = cell.content_view.width, cell.content_view.height
					switch.center = (w - switch.width/2 - 10, h/2)
					switch.flex = 'TBL'
					switch.value = value
					switch.name = key
					switch.action = self.switch_action
					if tint_color:
						switch.tint_color = tint_color
					cell.content_view.add_subview(switch)
				elif t == 'text' or t == 'url' or t == 'email' or t == 'password' or t == 'number':
					value = item.get('value', '')
					self.values[key] = value
					placeholder = item.get('placeholder', '')
					cell.selectable = False
					cell.text_label.text = title
					label_width = ui.measure_string(title, font=cell.text_label.font)[0]
					if cell.image_view.image:
						label_width += min(64, cell.image_view.image.size[0] + 16)
					cell_width, cell_height = cell.content_view.width, cell.content_view.height
					tf = ui.TextField()
					tf_width = max(40, cell_width - label_width - 32)
					tf.frame = (cell_width - tf_width - 8, 1, tf_width, cell_height-2)
					tf.bordered = False
					tf.placeholder = placeholder
					tf.flex = 'W'
					tf.text = value
					tf.text_color = '#337097'
					if t == 'text':
						tf.autocorrection_type = item.get('autocorrection', None)
						tf.autocapitalization_type = item.get('autocapitalization', ui.AUTOCAPITALIZE_SENTENCES)
						tf.spellchecking_type = item.get('spellchecking', None)
					if t == 'url':
						tf.keyboard_type = ui.KEYBOARD_URL
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'email':
						tf.keyboard_type = ui.KEYBOARD_EMAIL
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'number':
						tf.keyboard_type = ui.KEYBOARD_NUMBERS
						tf.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
						tf.autocorrection_type = False
						tf.spellchecking_type = False
					elif t == 'password':
						tf.secure = True
					
					tf.clear_button_mode = 'while_editing'
					tf.name = key
					tf.delegate = self
					cell.content_view.add_subview(tf)

				elif t == 'check':
					value = item.get('value', False)
					group = item.get('group', None)
					if value:
						cell.accessory_type = 'checkmark'
						cell.text_label.text_color = cell.tint_color
					cell.text_label.text = title
					if group:
						if value:
							self.values[group] = key
					else:
						self.values[key] = value
				elif t == 'date' or t == 'datetime' or t == 'time':
					value = item.get('value', datetime.datetime.now())
					if type(value) == datetime.date:
						value = datetime.datetime.combine(value, datetime.time())
					if type(value) == datetime.time:
						value = datetime.datetime.combine(value, datetime.date.today())
					date_format = item.get('format', None)
					if not date_format:
						if t == 'date':
							date_format = '%Y-%m-%d'
						elif t == 'time':
							date_format = '%H:%M'
						else:
							date_format = '%Y-%m-%d %H:%M'
					item['format'] = date_format
					cell.detail_text_label.text = value.strftime(date_format)
					self.values[key] = value
					cell.text_label.text = title
				else:
					cell.selectable = False
					cell.text_label.text = item.get('title', '')

				section_cells.append(cell)
				
		done_button = ui.ButtonItem(title=done_button_title)
		done_button.action = self.done_action
		self.container_view.right_button_items = [done_button]

	def update_kb_height(self, h):
		self.view.content_inset = (0, 0, h, 0)
		self.view.scroll_indicator_insets = (0, 0, h, 0)
	
	def tableview_number_of_sections(self, tv):
		return len(self.cells)
	
	def tableview_title_for_header(self, tv, section):
		return self.sections[section][0]

	def tableview_title_for_footer(self, tv, section):
		s = self.sections[section]
		if len(s) > 2:
			return s[2]
		return None
	
	def tableview_number_of_rows(self, tv, section):
		return len(self.cells[section])
	
	def tableview_did_select(self, tv, section, row):
		sel_item = self.sections[section][1][row]
		t = sel_item.get('type', None)
		if t == 'check':
			key = sel_item['key']
			tv.selected_row = -1
			group = sel_item.get('group', None)
			cell = self.cells[section][row]
			if group:
				for i, s in enumerate(self.sections):
					for j, item in enumerate(s[1]):
						if item.get('type', None) == 'check' and item.get('group', None) == group and item is not sel_item:
							self.cells[i][j].accessory_type = 'none'
							self.cells[i][j].text_label.text_color = None
				cell.accessory_type = 'checkmark'
				cell.text_label.text_color = cell.tint_color
				self.values[group] = key
			else:
				if cell.accessory_type == 'checkmark':
					cell.accessory_type = 'none'
					cell.text_label.text_color = None
					self.values[key] = False
				else:
					cell.accessory_type = 'checkmark'
					self.values[key] = True
		elif t == 'date' or t == 'time' or t == 'datetime':
			tv.selected_row = -1
			self.selected_date_key = sel_item['key']
			self.selected_date_value = self.values.get(self.selected_date_key)
			self.selected_date_cell = self.cells[section][row]
			self.selected_date_format = sel_item['format']
			self.selected_date_type = t
			if t == 'date':
				mode = ui.DATE_PICKER_MODE_DATE
			elif t == 'time':
				mode = ui.DATE_PICKER_MODE_TIME
			else:
				mode = ui.DATE_PICKER_MODE_DATE_AND_TIME
			self.show_datepicker(mode)
	
	def show_datepicker(self, mode):
		ui.end_editing()
		self.shield_view = ui.View()
		self.shield_view.flex = 'WH'
		self.shield_view.frame = (0, 0, self.view.width, self.view.height)
		
		self.dismiss_datepicker_button = ui.Button()
		self.dismiss_datepicker_button.flex = 'WH'
		self.dismiss_datepicker_button.frame = (0, 0, self.view.width, self.view.height)
		self.dismiss_datepicker_button.background_color = (0, 0, 0, 0.5)
		self.dismiss_datepicker_button.action = self.dismiss_datepicker
		self.dismiss_datepicker_button.alpha = 0.0
		self.shield_view.add_subview(self.dismiss_datepicker_button)

		self.date_picker = ui.DatePicker()
		self.date_picker.date = self.selected_date_value
		self.date_picker.background_color = 'white'
		self.date_picker.mode = mode
		self.date_picker.frame = (0, self.shield_view.height - self.date_picker.height, self.shield_view.width, self.date_picker.height)
		self.date_picker.flex = 'TW'
		self.date_picker.transform = ui.Transform.translation(0, self.date_picker.height)
		self.shield_view.add_subview(self.date_picker)

		self.container_view.add_subview(self.shield_view)
		
		def fade_in():
			self.dismiss_datepicker_button.alpha = 1.0
			self.date_picker.transform = ui.Transform.translation(0, 0)
		ui.animate(fade_in, 0.3)

	def dismiss_datepicker(self, sender):
		value = self.date_picker.date
		
		if self.selected_date_type == 'date':
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)
		elif self.selected_date_type == 'time':
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)
		else:
			self.selected_date_cell.detail_text_label.text = value.strftime(self.selected_date_format)

		self.values[self.selected_date_key] = value
		
		def fade_out():
			self.dismiss_datepicker_button.alpha = 0.0
			self.date_picker.transform = ui.Transform.translation(0, self.date_picker.height)
		def remove():
			self.container_view.remove_subview(self.shield_view)
			self.shield_view = None
		ui.animate(fade_out, 0.3, completion=remove)
	
	
	def tableview_cell_for_row(self, tv, section, row):
		return self.cells[section][row]
	
	def textfield_did_change(self, tf):
		self.values[tf.name] = tf.text
	
	def switch_action(self, sender):
		self.values[sender.name] = sender.value
	
	def segment_action(self, sender):
		self.values[sender.name] = sender.segments[sender.selected_index]
		
	def done_action(self, sender):
		if self.shield_view:
			self.dismiss_datepicker(None)
		else:
			ui.end_editing()
			self.was_canceled = False
			self.container_view.close()
			
class _SCFormContainerView (ui.View):
	def __init__(self):
		self.delegate = None
		
	def keyboard_frame_will_change(self, f):
		r = ui.convert_rect(f, to_view=self)
		if r[3] > 0:
			kbh = self.height - r[1]
		else:
			kbh = 0
		if self.delegate:
			self.delegate.update_kb_height(kbh)

def SCform_dialog(title='', fields=None, sections=None, done_button_title='Done'):
	if not sections and not fields:
		raise ValueError('sections or fields are required')
	if not sections:
		sections = [('', fields)]
	if not isinstance(title, basestring):
		raise TypeError('title must be a string')
	for section in sections:
		if not isinstance(section, collections.Sequence):
			raise TypeError('Sections must be sequences (title, fields)')
		if len(section) < 2:
			raise TypeError('Sections must have 2 or 3 items (title, fields[, footer]')
		if not isinstance(section[0], basestring):
			raise TypeError('Section titles must be strings')
		if not isinstance(section[1], collections.Sequence):
			raise TypeError('Expected a sequence of field dicts')
		for field in section[1]:
			if not isinstance(field, dict):
				raise TypeError('fields must be dicts')

	c = _SCFormDialogController(title, sections, done_button_title=done_button_title)
	c.container_view.frame = (0,0,375,667)
	c.container_view.present('sheet')
	c.container_view.wait_modal()
	# Get rid of the view to avoid a retain cycle:
	c.container_view = None
	if c.was_canceled:
		return None
	return c.values
