import ui
import dialogs

#==================== copied from dialogs: begin
import collections
import sys
PY3 = sys.version_info[0] >= 3
if PY3:
    basestring = str

def my_form_dialog(title='', fields=None, sections=None, done_button_title='Done'):
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

    c = dialogs._FormDialogController(title, sections, done_button_title=done_button_title)

    #==================== dialogs.form_dialog modification 1: begin
    for i in range(0,len(c.cells[0])):          # loop on rows of section 0
        cell = c.cells[0][i]                                    # ui.TableViewCell of row i
        # some fields types are subviews of the cell:
        #   text,number,url,email,password,switch
        #  but check, date and time are not set as subviews of cell.content_view
        if len(cell.content_view.subviews) > 0:
            tf = cell.content_view.subviews[0]      # ui.TextField of value in row
            # attention: tf.name not set for date fields
            if tf.name == 'segmented':
                item = c.sections[0][1][i]  # section 0, 1=items, row i
                segmented = ui.SegmentedControl()
                segmented.name = cell.text_label.text
                segmented.frame = tf.frame
                segmented.segments = item['segments']
                cell.content_view.remove_subview(tf)
                del c.values[tf.name]
                del tf
                cell.content_view.add_subview(segmented)
    #==================== dialogs.form_dialog modification 1: end

    c.container_view.present('sheet')
    c.container_view.wait_modal()
    # Get rid of the view to avoid a retain cycle:
    c.container_view = None
    if c.was_canceled:
        return None

#==================== dialogs.form_dialog modification 2: begin
    for i in range(0,len(c.cells[0])):          # loop on rows of section 0
        cell = c.cells[0][i]                                    # ui.TableViewCell of row i
        # some fields types are subviews of the cell:
        #   text,number,url,email,password,switch
        #  but check, date and time are not set as subviews of cell.content_view
        for tf in cell.content_view.subviews:
            if 'SegmentedControl' in str(type(tf)):
                item = c.sections[0][1][i]  # section 0, 1=items, row i
                c.values[tf.name] = item['segments'][tf.selected_index]
#==================== dialogs.form_dialog modification 2: end

    return c.values
#==================== copied from dialogs: end

fields = []
field = {'title':'title 1','type':'text','value':'test 1'}
fields.append(field)
field = {'title':'title 2','type':'text','value':'test 1','key':'segmented','segments':['seg1','seg2']}
fields.append(field)
updated_fields = my_form_dialog(title='my dialog title', fields=fields)
print(updated_fields)
