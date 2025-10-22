import re
import traceback
import tkinter as tk
from datetime import datetime
from MetaDataYoutube import MetaDataYoutube
from GridField import GridField

# Configurables:
HIDE_WATCHED = False
WINDOW_SIZE = (1045, 500)
HEADER_COLUMN_NAMES = ('Progress:', 'Length:', 'Category:', 'Name:', 'Link:', 'Watched:', '')
HEADER_COLUMN_WIDTHS = (12, 12, 19, 72, 38, 13, 5)
ENTRIES_COLUMN_WIDTHS = (10, 10, 19, 80, 40, 12)
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
		self.fieldIntVars = {}
		self.feedbackStrVar = tk.StringVar(root, 'No field data entered')
		for fieldType in MetaDataYoutube.Field:
			self.fieldStrVars[fieldType] = tk.StringVar(root, MetaDataYoutube.getDefaultFieldValue(fieldType))
			if (intValue := MetaDataYoutube.getIntVarValue(fieldType, self.getFieldStrVar(fieldType).get())) is not None:
				self.fieldIntVars[fieldType] = tk.IntVar(root, intValue)

	def getIdxByName(self):
		return metaData.getIdxByName(self.getFieldStrVar(MetaDataYoutube.Field.NAME).get())

	def getFieldStrVar(self, fieldType):
		return self.fieldStrVars[fieldType]

	def getFieldIntVar(self, fieldType):
		return self.fieldIntVars.get(fieldType, None)

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

	def fieldCallback(self, name, index=None, mode=None):
		for fieldType in MetaDataYoutube.Field:
			fieldStrVars = self.getFieldStrVar(fieldType)
			if name == fieldType or name == str(fieldStrVars):
				if fieldIntVars := self.getFieldIntVar(fieldType):
					fieldStrVars.set(MetaDataYoutube.getStrVarValue(fieldType, fieldIntVars.get()))
				if fieldType == MetaDataYoutube.Field.PROGRESS or fieldType == MetaDataYoutube.Field.LENGTH:
					fieldStrVars.set(re.sub('[^0-9]', ':', fieldStrVars.get()))
				if MetaDataYoutube.isValidFieldValue(fieldType, fieldStrVars.get()):
					self.getFeedbackStrVar().set(metaData.getFieldTypeName(fieldType) + ' field valid')
					self.loadFieldsByField(fieldType, fieldStrVars.get())
				else:
					self.getFeedbackStrVar().set(metaData.getFieldTypeName(fieldType) + ' field invalid')
				break

class EntriesList:
	def __init__(self, root):
		self.entries = []
		self.fieldStrVars = []
		self.fieldIntVars = []
		self.readEntries()
		for idx in range(self.getEntryCount()):
			self.fieldStrVars.append({})
			self.fieldIntVars.append({})
			for fieldType in MetaDataYoutube.Field:
				self.fieldStrVars[idx][fieldType] = tk.StringVar(root, self.entries[idx][0][fieldType.value])
				if (intValue := MetaDataYoutube.getIntVarValue(fieldType, self.getFieldStrVar(idx, fieldType).get())) is not None:
					self.fieldIntVars[idx][fieldType] = tk.IntVar(root, intValue)

	def getEntryCount(self):
		return len(self.entries)

	def getFieldStrVar(self, idx, fieldType):
		return self.fieldStrVars[idx][fieldType]

	def getFieldIntVar(self, idx, fieldType):
		return self.fieldIntVars[idx].get(fieldType, None)

	def readEntries(self):
		self.entries.clear()
		for idx in range(metaData.getEntryCount()):
			self.entries.append((metaData.getEntryByIdx(idx), idx))
		self.entries.sort(key=lambda entry: datetime.strptime(entry[0][MetaDataYoutube.Field.ADD_TIME.value], '%Y-%m-%d %H:%M:%S.%f'))
		entriesWatched = []
		for entry in self.entries:
			if entry[0][MetaDataYoutube.Field.WATCHED.value] == str(True):
				entriesWatched.append(entry)
		for entry in entriesWatched:
			self.entries.remove(entry)
		if not HIDE_WATCHED:
			entriesWatched.extend(self.entries)
			self.entries = entriesWatched
		self.entries.reverse()

	def loadFieldByIdx(self, idx, fieldType):
		self.getFieldStrVar(idx, fieldType).set(metaData.getFieldByIdx(fieldType, self.entries[idx][1]))

	def writeFieldByIdx(self, idx, fieldType):
		metaData.setFieldByIdx(fieldType, self.entries[idx][1], self.getFieldStrVar(idx, fieldType).get())
		metaData.writeMetaData()

	def fieldCallback(self, name, index=None, mode=None):
		for idx in range(self.getEntryCount()):
			for fieldType in MetaDataYoutube.Field:
				fieldStrVars = self.getFieldStrVar(idx, fieldType)
				if (name == fieldType and index == idx) or name == str(fieldStrVars):
					if fieldIntVars := self.getFieldIntVar(idx, fieldType):
						fieldStrVars.set(MetaDataYoutube.getStrVarValue(fieldType, fieldIntVars.get()))
					if fieldType == MetaDataYoutube.Field.NAME and fieldStrVars.get() == '':
						# Empty name -> remove entry:
						metaData.removeEntry(idx)
						metaData.writeMetaData()
						createEntriesFrameGridFields()
					elif MetaDataYoutube.isValidFieldValue(fieldType, fieldStrVars.get()):
						# Valid change -> update entry:
						self.writeFieldByIdx(idx, fieldType)
					else:
						# Invalid change -> reload entry:
						self.loadFieldByIdx(idx, fieldType)
					if fieldType == MetaDataYoutube.Field.WATCHED and fieldIntVars.get() == int(True):
						# Watched -> set progress equal to length:
						self.getFieldStrVar(idx, MetaDataYoutube.Field.PROGRESS).set(self.getFieldStrVar(idx, MetaDataYoutube.Field.LENGTH).get())
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.PROGRESS)
					elif fieldType == MetaDataYoutube.Field.WATCHED and fieldIntVars.get() == int(False):
						# Not watched -> set progress to default:
						self.getFieldStrVar(idx, MetaDataYoutube.Field.PROGRESS).set(MetaDataYoutube.getDefaultFieldValue(MetaDataYoutube.Field.PROGRESS))
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.PROGRESS)
					elif fieldType == MetaDataYoutube.Field.PROGRESS and MetaDataYoutube.timeToSeconds(fieldStrVars.get()) == MetaDataYoutube.timeToSeconds(self.getFieldStrVar(idx, MetaDataYoutube.Field.LENGTH).get()):
						# Progress equal to length -> set to watched:
						self.getFieldIntVar(idx, MetaDataYoutube.Field.WATCHED).set(int(True))
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.WATCHED)
					elif fieldType == MetaDataYoutube.Field.PROGRESS and MetaDataYoutube.timeToSeconds(fieldStrVars.get()) < MetaDataYoutube.timeToSeconds(self.getFieldStrVar(idx, MetaDataYoutube.Field.LENGTH).get()):
						# Progress smaller than length -> set to not watched:
						self.getFieldIntVar(idx, MetaDataYoutube.Field.WATCHED).set(int(False))
						self.writeFieldByIdx(idx, MetaDataYoutube.Field.WATCHED)
					break

def pasteClipboardToStrVar(root, strVar):
	strVar.set(root.clipboard_get())

def addVideo():
	# Check validity:
	hasInvalidFields = False
	for fieldType in MetaDataYoutube.Field:
		fieldStrVars = entryAdder.getFieldStrVar(fieldType)
		if MetaDataYoutube.isValidFieldValue(fieldType, fieldStrVars.get()) == False:
			fieldStrVars.set(MetaDataYoutube.getDefaultFieldValue(fieldType))
			hasInvalidFields = True
	if hasInvalidFields:
		entryAdder.getFeedbackStrVar().set('Invalid fields have been reset')
		return
	# Check invalid progress to length and watched status:
	if MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.PROGRESS).get()) > MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.LENGTH).get()):
		entryAdder.getFeedbackStrVar().set('Invalid: Progress cannot be larger than length')
		return
	if entryAdder.getFieldIntVar(MetaDataYoutube.Field.WATCHED).get() == int(False) and MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.PROGRESS).get()) == MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.LENGTH).get()):
		entryAdder.getFeedbackStrVar().set('Invalid: Progress cannot be equal to length if not watched')
		return
	if entryAdder.getFieldIntVar(MetaDataYoutube.Field.WATCHED).get() == int(True) and MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.PROGRESS).get()) < MetaDataYoutube.timeToSeconds(entryAdder.getFieldStrVar(MetaDataYoutube.Field.LENGTH).get()):
		entryAdder.getFeedbackStrVar().set('Invalid: Progress cannot be smaller than length if watched')
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
		gridFieldType, gridFieldArg1, gridFieldArg2, gridFieldArg3 = metaData.getGridFieldData(fieldType)
		if gridFieldArg1 == 'getFieldStrVar':
			gridFieldArg1 = entryAdder.getFieldStrVar(fieldType)
		elif gridFieldArg1 == 'getFieldIntVar':
			gridFieldArg1 = entryAdder.getFieldIntVar(fieldType)
		if gridFieldArg2 == 'fieldCallback':
			gridFieldArg2 = entryAdder.fieldCallback
		elif gridFieldArg2 == 'fieldCallbackWithFieldType':
			gridFieldArg2 = lambda fieldType=fieldType: entryAdder.fieldCallback(fieldType)
		if gridFieldArg3 == 'pasteClipboardToStrVar':
			gridFieldArg3 = pasteClipboardToStrVar
		GridField.add(headerFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], gridFieldType, gridFieldArg1, gridFieldArg2, gridFieldArg3)
		column += 1
	row += 1
	GridField.add(headerFrame, row, (0, len(ENTRIES_COLUMN_WIDTHS) - 1), sum(ENTRIES_COLUMN_WIDTHS) - ENTRIES_COLUMN_WIDTHS[-1], GridField.Type.DynamicLabel, entryAdder.getFeedbackStrVar())
	GridField.add(headerFrame, row, len(ENTRIES_COLUMN_WIDTHS) - 1, ENTRIES_COLUMN_WIDTHS[-1], GridField.Type.Button, 'Add', addVideo)

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
			gridFieldType, gridFieldArg1, gridFieldArg2, gridFieldArg3 = metaData.getGridFieldData(fieldType)
			if gridFieldArg1 == 'getFieldStrVar':
				gridFieldArg1 = entriesList.getFieldStrVar(i, fieldType)
			elif gridFieldArg1 == 'getFieldIntVar':
				gridFieldArg1 = entriesList.getFieldIntVar(i, fieldType)
			if gridFieldArg2 == 'fieldCallback':
				gridFieldArg2 = entriesList.fieldCallback
			elif gridFieldArg2 == 'fieldCallbackWithFieldType':
				gridFieldArg2 = lambda i=i, fieldType=fieldType: entriesList.fieldCallback(fieldType, i)
			if gridFieldArg3 == 'pasteClipboardToStrVar':
				gridFieldArg3 = pasteClipboardToStrVar
			GridField.add(entriesFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], gridFieldType, gridFieldArg1, gridFieldArg2, gridFieldArg3)
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