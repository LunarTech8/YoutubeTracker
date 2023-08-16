import traceback
import tkinter as tk
from datetime import datetime
from MetaDataYoutube import MetaDataYoutube
from GridField import GridField

# Configurables:
WINDOW_SIZE = (1045, 500)
HEADER_COLUMN_NAMES = ('Progress:', 'Length:', 'Category:', 'Name:', 'Link:', 'Watched:', '')
HEADER_COLUMN_WIDTHS = (12, 12, 18, 72, 38, 12, 5)
ENTRIES_COLUMN_WIDTHS = (10, 10, 17, 80, 40, 12)
assert len(HEADER_COLUMN_NAMES) == len(HEADER_COLUMN_WIDTHS)
assert len(MetaDataYoutube.SORTED_FIELD_TYPES) == len(ENTRIES_COLUMN_WIDTHS)
# Global variables:
metaData = MetaDataYoutube()
entriesList = None
entryAdder = None
headerFrame = None
entriesFrame = None

class EntryAdder:
	def __init__(self, root):
		self.fieldStrVars = {}
		self.feedbackStrVar = tk.StringVar(root, 'No field data entered')
		for fieldType in MetaDataYoutube.Field:
			self.fieldStrVars[fieldType] = tk.StringVar(root, metaData.getDefaultFieldValue(fieldType))

	def getIdxByName(self):
		return metaData.getIdxByName(self.getFieldStrVar(MetaDataYoutube.Field.NAME).get())

	def getFieldStrVar(self, fieldType):
		return self.fieldStrVars[fieldType]

	def getFeedbackStrVar(self):
		return self.feedbackStrVar

	def getFields(self):
		fields = []
		for fieldStrVar in self.fieldStrVars.values():
			fields.append(fieldStrVar.get())
		return fields

	def loadFieldsByField(self, fieldType, fieldValue):
		entryIdx = metaData.getIdxByField(fieldType, fieldValue)
		if entryIdx != None:
			entry = metaData.getEntryByIdx(entryIdx)
			for fieldType in MetaDataYoutube.Field:
				self.getFieldStrVar(fieldType).set(entry[fieldType.value])

	def fieldCallback(self, name, index, mode):
		for fieldType in MetaDataYoutube.Field:
			fieldStrVars = self.getFieldStrVar(fieldType)
			if str(fieldStrVars) == name:
				if metaData.isValidFieldValue(fieldType, fieldStrVars.get()):
					self.getFeedbackStrVar().set(metaData.getFieldTypeName(fieldType) + ' field valid')
					self.loadFieldsByField(fieldType, fieldStrVars.get())
				else:
					self.getFeedbackStrVar().set(metaData.getFieldTypeName(fieldType) + ' field invalid')
				break

class EntriesList:
	def __init__(self, root):
		self.entries = []
		self.fieldStrVars = []
		self.readEntries()
		for idx in range(self.getEntryCount()):
			self.fieldStrVars.append({})
			for fieldType in MetaDataYoutube.Field:
				self.fieldStrVars[idx][fieldType.value] = tk.StringVar(root, self.entries[idx][0][fieldType.value])

	def getEntryCount(self):
		return len(self.entries)

	def getFieldStrVar(self, idx, fieldType):
		return self.fieldStrVars[idx][fieldType.value]

	def readEntries(self):
		entries = []
		for idx in range(metaData.getEntryCount()):
			entries.append((metaData.getEntryByIdx(idx), idx))
		entries.sort(key=lambda entry: datetime.strptime(entry[0][MetaDataYoutube.Field.ADD_TIME.value], '%Y-%m-%d %H:%M:%S.%f'))
		self.entries.clear()
		for entry in entries:
			if entry[0][MetaDataYoutube.Field.WATCHED.value] == str(True):
				self.entries.append(entry)
		for entry in self.entries:
			entries.remove(entry)
		self.entries.extend(entries)

	def loadFieldByIdx(self, idx, fieldType):
		self.getFieldStrVar(idx, fieldType).set(metaData.getFieldByIdx(fieldType, self.entries[idx][1]))

	def writeFieldByIdx(self, idx, fieldType):
		metaData.setFieldByIdx(fieldType, self.entries[idx][1], self.getFieldStrVar(idx, fieldType).get())
		metaData.writeMetaData()

	def fieldCallback(self, name, index, mode):
		for idx in range(self.getEntryCount()):
			for fieldType in MetaDataYoutube.Field:
				fieldStrVars = self.getFieldStrVar(idx, fieldType)
				if str(fieldStrVars) == name:
					if fieldType == MetaDataYoutube.Field.NAME and fieldStrVars.get() == '':
						# Empty name -> remove entry:
						metaData.removeEntry(idx)
						metaData.writeMetaData()
						createEntriesFrameGridFields()
					elif metaData.isValidFieldValue(fieldType, fieldStrVars.get()):
						# Valid change -> update entry:
						self.writeFieldByIdx(idx, fieldType)
					else:
						# Invalid change -> reload entry:
						self.loadFieldByIdx(idx, fieldType)
					if fieldType == MetaDataYoutube.Field.WATCHED and fieldStrVars.get() == str(True):
						# Watched -> set progress equal to length:
						self.getFieldStrVar(idx, MetaDataYoutube.Field.PROGRESS).set(self.getFieldStrVar(idx, MetaDataYoutube.Field.LENGTH).get())
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.PROGRESS)
					elif fieldType == MetaDataYoutube.Field.PROGRESS and fieldStrVars.get() == self.getFieldStrVar(idx, MetaDataYoutube.Field.LENGTH).get():
						# Progress equal to length -> set to watched:
						self.getFieldStrVar(idx, MetaDataYoutube.Field.WATCHED).set(str(True))
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.WATCHED)
					break

def pasteClipboardToStrVar(root, strVar):
	strVar.set(root.clipboard_get())

def addVideo():
	# Check validity:
	hasInvalidFields = False
	for fieldType in MetaDataYoutube.Field:
		fieldStrVars = entryAdder.getFieldStrVar(fieldType)
		if metaData.isValidFieldValue(fieldType, fieldStrVars.get()) == False:
			fieldStrVars.set(metaData.getDefaultFieldValue(fieldType))
			hasInvalidFields = True
	if hasInvalidFields:
		entryAdder.getFeedbackStrVar().set('Invalid fields have been reset')
		return
	# Add or update video:
	if entryAdder.getIdxByName() == None:
		metaData.addEntry(entryAdder.getFields())
		metaData.writeMetaData()
		entryAdder.getFeedbackStrVar().set('New entry added')
	else:
		metaData.updateEntry(entryAdder.getIdxByName(), entryAdder.getFields())
		metaData.writeMetaData()
		entryAdder.getFeedbackStrVar().set('Entry updated')
	createEntriesFrameGridFields()

def createHeaderFrameGridFields():
	global entryAdder
	for widget in headerFrame.winfo_children():
		widget.destroy()
	entryAdder = EntryAdder(headerFrame)
	# Create grid fields for headers:
	row = 0
	for column in range(len(HEADER_COLUMN_NAMES)):
		GridField.add(headerFrame, row, column, HEADER_COLUMN_WIDTHS[column], GridField.Type.Header, HEADER_COLUMN_NAMES[column])
	# Create grid fields for adder fields:
	column = 0
	row += 1
	for fieldType in MetaDataYoutube.SORTED_FIELD_TYPES:
		if fieldType == MetaDataYoutube.Field.WATCHED:
			GridField.add(headerFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.Button, 'Add', addVideo)
		else:
			fieldSet = metaData.getSortedFieldSet(fieldType)
			if fieldSet != None:
				GridField.add(headerFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.Combobox, entryAdder.getFieldStrVar(fieldType), fieldSet)
			else:
				GridField.add(headerFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.TextEntry, entryAdder.getFieldStrVar(fieldType), entryAdder.fieldCallback, pasteClipboardToStrVar)
		column += 1

def createEntriesFrameGridFields():
	global entriesList
	for widget in entriesFrame.winfo_children():
		widget.destroy()
	entriesList = EntriesList(entriesFrame)
	# Create grid fields for list entries:
	for i in range(entriesList.getEntryCount()):
		row = i + 1
		column = 0
		for fieldType in MetaDataYoutube.SORTED_FIELD_TYPES:
			fieldSet = metaData.getSortedFieldSet(fieldType)
			if fieldSet != None:
				GridField.add(entriesFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.Combobox, entriesList.getFieldStrVar(i, fieldType), fieldSet, entriesList.fieldCallback)
			else:
				GridField.add(entriesFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.TextEntry, entriesList.getFieldStrVar(i, fieldType), entriesList.fieldCallback, pasteClipboardToStrVar)
			column += 1

def createControlWindow(root):
	global headerFrame
	global entriesFrame
	root.title('Youtube tracker')
	root.geometry(str(WINDOW_SIZE[0]) + 'x' + str(WINDOW_SIZE[1]))
	root.resizable(0, 1)
	# Set up fixed header frame and scrollable entries frame:
	outerFrame = tk.Frame(root)
	outerFrame.pack(fill=tk.BOTH, expand=1)
	headerFrame = tk.Canvas(outerFrame)
	headerFrame.pack(side=tk.TOP, fill=tk.X, expand=0)
	createHeaderFrameGridFields()
	entriesCanvas = tk.Canvas(outerFrame)
	entriesCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
	entriesScrollbar = tk.Scrollbar(outerFrame, orient=tk.VERTICAL, command=entriesCanvas.yview)
	entriesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	entriesCanvas.configure(yscrollcommand=entriesScrollbar.set)
	entriesCanvas.bind('<Configure>', lambda event: entriesCanvas.configure(scrollregion=entriesCanvas.bbox('all')))
	entriesFrame = tk.Frame(entriesCanvas)
	entriesCanvas.create_window((0, 0), window=entriesFrame, anchor='nw')
	createEntriesFrameGridFields()

def main():
	try:
		createControlWindow(tk.Tk())
		tk.mainloop()
	except Exception:
		print(traceback.format_exc())
		input('Press enter to close traceback.')

if __name__ == "__main__":
	main()