import ui
import SCdialogs

"""
seg = ui.SegmentedControl()
seg.segments = ('this', 'that', 'then')
view = ui.View()
seg.
cell = ui.TableViewCell('value1')
cell.add_subview(seg)
view.add_subview(cell)
view.present('sheet')
"""


#fields = [{'type':,'key':,'value':,'title':},{}]
#fields = [{'type':'text' ,'key':'lname' ,'value':'This' ,'title':'Aha' },{'type':'text' ,'key':'fname' ,'value':'amir' ,'title':'readable' }]
fields2 = [{'type':'text' ,'key':'lname' ,'value':'This' ,'title':'Aha' },	{'type':'text' ,'key':'fname' ,'value':'amir' ,'title':'readable' }, {'type': 'segmented', 'key':'abbrev', 'value':'VP|CR|TW|VC|ROUT|tytyty|kokokoko', 'title':'abb'}, {'type': 'segmented', 'key':'abbrev5', 'value':'kjkjl|lklklk|ftftftjljlj|VC|ROUT|tytyty|kokokoko', 'title':'abb'}]

print(SCdialogs.SCform_dialog(title='DIALOGS2', fields = fields2, sections = None))

