import traceback
import tkinter as tk
from MetaDataYoutube import MetaDataYoutube
from GridField import GridField

# Configurables:
CONTROL_WINDOW_COLUMN_WIDTH = 100
# Global variables:
controlWindow = None

class ControlWindow:
	def __init__(self, root):
		self.metaData = MetaDataYoutube()
		self.fieldStrVars = {}
		self.feedbackStrVar = tk.StringVar(root, 'No field data entered')
		for fieldType in MetaDataYoutube.Field:
			self.fieldStrVars[fieldType] = tk.StringVar(root, self.metaData.getDefaultFieldValue(fieldType))

	def getIdxByName(self):
		return self.metaData.getIdxByName(self.getFieldStrVar(MetaDataYoutube.Field.NAME).get())

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
		entryIdx = self.metaData.getIdxByField(fieldType, fieldValue)
		if entryIdx != None:
			entry = self.metaData.getEntryByIdx(entryIdx)
			for fieldType in MetaDataYoutube.Field:
				self.getFieldStrVar(fieldType).set(entry[fieldType.value])

	def fieldCallback(self, name, index, mode):
		for fieldType in MetaDataYoutube.Field:
			fieldStrVars = self.getFieldStrVar(fieldType)
			if str(fieldStrVars) == name:
				if self.metaData.isValidFieldValue(fieldType, fieldStrVars.get()):
					self.getFeedbackStrVar().set(self.metaData.getFieldTypeName(fieldType) + ' field valid')
					self.loadFieldsByField(fieldType, fieldStrVars.get())
				else:
					self.getFeedbackStrVar().set(self.metaData.getFieldTypeName(fieldType) + ' field invalid')
				break

def pasteClipboardToStrVar(root, strVar):
	strVar.set(root.clipboard_get())

def addVideo():
	global controlWindow
	# Check validity:
	hasInvalidFields = False
	for fieldType in MetaDataYoutube.Field:
		fieldStrVars = controlWindow.getFieldStrVar(fieldType)
		if controlWindow.metaData.isValidFieldValue(fieldType, fieldStrVars.get()) == False:
			fieldStrVars.set(controlWindow.metaData.getDefaultFieldValue(fieldType))
			hasInvalidFields = True
	if hasInvalidFields:
		controlWindow.getFeedbackStrVar().set('Invalid fields have been reset')
		return
	# Add video:
	if controlWindow.getIdxByName() == None:
		controlWindow.metaData.addEntry(controlWindow.getFields())
		controlWindow.metaData.writeMetaData()
		controlWindow.getFeedbackStrVar().set('New entry added')
	else:
		controlWindow.metaData.updateEntry(controlWindow.getIdxByName(), controlWindow.getFields())
		controlWindow.metaData.writeMetaData()
		controlWindow.getFeedbackStrVar().set('Entry updated')

def createControlWindow(root):
	global controlWindow
	root.title('Update youtube list')
	root.resizable(1, 1)
	mainFrame = tk.Frame(root)
	mainFrame.pack(fill=tk.BOTH, expand=1)
	controlWindow = ControlWindow(mainFrame)
	row = 0
	column = 0
	GridField.add(mainFrame, row, column, CONTROL_WINDOW_COLUMN_WIDTH, GridField.Type.Header, 'Enter video data:')
	row += 1
	for fieldType in MetaDataYoutube.Field:
		fieldSet = controlWindow.metaData.getSortedFieldSet(fieldType)
		if fieldSet != None:
			GridField.add(mainFrame, row, column, CONTROL_WINDOW_COLUMN_WIDTH, GridField.Type.Combobox, controlWindow.getFieldStrVar(fieldType), fieldSet)
		else:
			GridField.add(mainFrame, row, column, CONTROL_WINDOW_COLUMN_WIDTH, GridField.Type.TextEntry, controlWindow.getFieldStrVar(fieldType), controlWindow.fieldCallback, pasteClipboardToStrVar)
		row += 1
	GridField.add(mainFrame, row, column, CONTROL_WINDOW_COLUMN_WIDTH, GridField.Type.Button, 'Add/Update video', addVideo)
	row += 1
	GridField.add(mainFrame, row, column, CONTROL_WINDOW_COLUMN_WIDTH, GridField.Type.DynamicLabel, controlWindow.getFeedbackStrVar())

def main():
	try:
		createControlWindow(tk.Tk())
		tk.mainloop()
	except Exception:
		print(traceback.format_exc())
		input('Press enter to close traceback.')

if __name__ == "__main__":
	main()