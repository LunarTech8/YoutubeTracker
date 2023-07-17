import traceback
import tkinter as tk
from MetaDataYoutube import MetaDataYoutube
from GridField import GridField

# Configurables:
CONTROL_WINDOW_SIZE = (1010, 500)
CONTROL_WINDOW_GRID_COLUMN_NAMES = ('Watched:', 'Progress:', 'Length:', 'Category:', 'Name:', 'Link:')
CONTROL_WINDOW_GRID_COLUMN_WIDTHS = (8, 10, 10, 15, 50, 50)
assert len(CONTROL_WINDOW_GRID_COLUMN_NAMES) == len(CONTROL_WINDOW_GRID_COLUMN_WIDTHS)
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
	root.geometry(str(CONTROL_WINDOW_SIZE[0]) + 'x' + str(CONTROL_WINDOW_SIZE[1]))
	root.resizable(0, 1)
	# Set up scrollable main frame:
	outerFrame = tk.Frame(root)
	outerFrame.pack(fill=tk.BOTH, expand=1)
	outerCanvas = tk.Canvas(outerFrame)
	outerCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
	outerScrollbar = tk.Scrollbar(outerFrame, orient=tk.VERTICAL, command=outerCanvas.yview)
	outerScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	outerCanvas.configure(yscrollcommand=outerScrollbar.set)
	outerCanvas.bind('<Configure>', lambda event: outerCanvas.configure(scrollregion=outerCanvas.bbox('all')))
	mainFrame = tk.Frame(outerCanvas)
	outerCanvas.create_window((0, 0), window=mainFrame, anchor='nw')
	# Create grid field for entries:
	controlWindow = ControlWindow(mainFrame)
	row = 0
	for column in range(len(CONTROL_WINDOW_GRID_COLUMN_NAMES)):
		GridField.add(mainFrame, row, column, CONTROL_WINDOW_GRID_COLUMN_WIDTHS[column], GridField.Type.Header, CONTROL_WINDOW_GRID_COLUMN_NAMES[column])
	for i in range(controlWindow.getEntryCount()):
		row = i + 1
		column = 0
		for fieldType in MetaDataYoutube.Field:
			GridField.add(mainFrame, row, column, CONTROL_WINDOW_GRID_COLUMN_WIDTHS[column], GridField.Type.TextEntry, controlWindow.getFieldStrVar(i, fieldType), controlWindow.fieldCallback, pasteClipboardToStrVar)
			column += 1
		for fieldType in MetaDataYoutube.Field:
			GridField.add(mainFrame, row, column, CONTROL_WINDOW_GRID_COLUMN_WIDTHS[column], GridField.Type.TextEntry, controlWindow.getFieldStrVar(i, fieldType), controlWindow.fieldCallback, pasteClipboardToStrVar)
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