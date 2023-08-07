import traceback
import tkinter as tk
from MetaDataYoutube import MetaDataYoutube
from GridField import GridField

# Configurables:
WINDOW_SIZE = (1045, 500)
HEADER_COLUMN_NAMES = ('Watched:', 'Progress:', 'Length:', 'Category:', 'Name:', 'Link:', '')
HEADER_COLUMN_WIDTHS = (10, 12, 12, 18, 72, 38, 5)
ENTRIES_COLUMN_WIDTHS = (10, 10, 10, 20, 80, 40)
assert len(HEADER_COLUMN_NAMES) == len(HEADER_COLUMN_WIDTHS)
assert len(MetaDataYoutube.SORTED_FIELD_TYPES) == len(ENTRIES_COLUMN_WIDTHS)
# Global variables:
controlWindow = NotImplemented

class ControlWindow:
	def __init__(self, root):
		self.metaData = MetaDataYoutube()
		self.entries = []
		self.fieldStrVars = []
		self.feedbackStrVar = tk.StringVar(root, 'No field data entered')
		self.readEntries()
		for idx in range(self.getEntryCount()):
			self.fieldStrVars.append({})
			for fieldType in MetaDataYoutube.Field:
				self.fieldStrVars[idx][fieldType.value] = tk.StringVar(root, self.entries[idx][fieldType.value])

	def getEntryCount(self):
		return len(self.entries)

	def getFieldStrVar(self, idx, fieldType):
		return self.fieldStrVars[idx][fieldType.value]

	def getFeedbackStrVar(self):
		return self.feedbackStrVar

	def readEntries(self):
		self.entries.clear()
		for idx in range(self.metaData.getEntryCount()):
			self.entries.append(self.metaData.getEntryByIdx(idx))
		self.entries.sort(key=lambda entry: next(iter(entry[MetaDataYoutube.Field.NAME.value])))

	def loadFieldsByField(self, fieldType, fieldValue):
		entryIdx = self.metaData.getIdxByField(fieldType, fieldValue)
		if entryIdx != None:
			entry = self.metaData.getEntryByIdx(entryIdx)
			for fieldType in MetaDataYoutube.Field:
				self.getFieldStrVar(entryIdx, fieldType).set(entry[fieldType.value])

	def fieldCallback(self, name, index, mode):
		for fieldType in MetaDataYoutube.Field:
			fieldStrVars = self.getFieldStrVar(0, fieldType)  # TODO: think about how to get idx here
			if str(fieldStrVars) == name:
				if self.metaData.isValidFieldValue(fieldType, fieldStrVars.get()):
					self.getFeedbackStrVar().set(self.metaData.getFieldTypeName(fieldType) + ' field valid')
					self.loadFieldsByField(fieldType, fieldStrVars.get())
				else:
					self.getFeedbackStrVar().set(self.metaData.getFieldTypeName(fieldType) + ' field invalid')
				break

def pasteClipboardToStrVar(root, strVar):
	strVar.set(root.clipboard_get())

def createControlWindow(root):
	global controlWindow
	root.title('Youtube list')
	root.geometry(str(WINDOW_SIZE[0]) + 'x' + str(WINDOW_SIZE[1]))
	root.resizable(0, 1)
	# Set up fixed header frame and scrollable entries frame:
	outerFrame = tk.Frame(root)
	outerFrame.pack(fill=tk.BOTH, expand=1)
	headerFrame = tk.Canvas(outerFrame)
	headerFrame.pack(side=tk.TOP, fill=tk.X, expand=0)
	entriesCanvas = tk.Canvas(outerFrame)
	entriesCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
	entriesScrollbar = tk.Scrollbar(outerFrame, orient=tk.VERTICAL, command=entriesCanvas.yview)
	entriesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	entriesCanvas.configure(yscrollcommand=entriesScrollbar.set)
	entriesCanvas.bind('<Configure>', lambda event: entriesCanvas.configure(scrollregion=entriesCanvas.bbox('all')))
	entriesFrame = tk.Frame(entriesCanvas)
	entriesCanvas.create_window((0, 0), window=entriesFrame, anchor='nw')
	controlWindow = ControlWindow(entriesFrame)
	# Create grid field for headers:
	row = 0
	for column in range(len(HEADER_COLUMN_NAMES)):
		GridField.add(headerFrame, row, column, HEADER_COLUMN_WIDTHS[column], GridField.Type.Header, HEADER_COLUMN_NAMES[column])
	# Create grid field for entries:
	for i in range(controlWindow.getEntryCount()):
		row = i + 1
		column = 0
		for fieldType in MetaDataYoutube.SORTED_FIELD_TYPES:
			fieldSet = controlWindow.metaData.getSortedFieldSet(fieldType)
			if fieldSet != None:
				GridField.add(entriesFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.Combobox, controlWindow.getFieldStrVar(i, fieldType), fieldSet)
			else:
				GridField.add(entriesFrame, row, column, ENTRIES_COLUMN_WIDTHS[column], GridField.Type.TextEntry, controlWindow.getFieldStrVar(i, fieldType), controlWindow.fieldCallback, pasteClipboardToStrVar)
			column += 1

def main():
	try:
		createControlWindow(tk.Tk())
		tk.mainloop()
	except Exception:
		print(traceback.format_exc())
		input('Press enter to close traceback.')

if __name__ == "__main__":
	main()