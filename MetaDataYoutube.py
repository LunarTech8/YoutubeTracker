from enum import Enum
from datetime import datetime
from GridField import GridField

class MetaDataYoutube:
	class Field(Enum):
		NAME = 0
		LINK = 1
		CATEGORY = 2
		PROGRESS = 3
		LENGTH = 4
		WATCHED = 5
		ADD_TIME = 6

	ENCODING = 'utf-8'
	FILE_NAME = 'MetaDataYoutube.txt'
	FIELD_SEPARATOR = ' --- '
	SORTED_FIELD_TYPES = (Field.PROGRESS, Field.LENGTH, Field.CATEGORY, Field.NAME, Field.LINK, Field.WATCHED)
	MAX_TIME_SEPARATORS = 2
	MAX_TIME_PART_DURATION = 59

	@staticmethod
	def isTime(text, noLeadingZero=False):
		if noLeadingZero and text.startswith('0'):
			return False
		noMaxValue = (text.count(':') == MetaDataYoutube.MAX_TIME_SEPARATORS)
		for timePart in text.split(':', MetaDataYoutube.MAX_TIME_SEPARATORS):
			if (timePart == '' or (timePart.isdigit() and (noMaxValue or (int(timePart) <= MetaDataYoutube.MAX_TIME_PART_DURATION and len(timePart) <= MetaDataYoutube.MAX_TIME_SEPARATORS)))) == False:
				return False
			noMaxValue = False
		return True

	@staticmethod
	def timeToSeconds(time):
		assert MetaDataYoutube.isTime(time), f'Invalid time "{time}"'
		parts = time.split(':', MetaDataYoutube.MAX_TIME_SEPARATORS)
		while len(parts) < MetaDataYoutube.MAX_TIME_SEPARATORS + 1:
			parts.insert(0, '0')
		hours, minutes, seconds = map(int, parts)
		return (hours * 60 + minutes) * 60 + seconds

	@staticmethod
	def isDatetime(text):
		if text.count('-') != 2 or text.count(':') != MetaDataYoutube.MAX_TIME_SEPARATORS or text.count(' ') != 1 or text.count('.') != 1:
			return False
		text = text.replace(':', '-').replace(' ', '-').replace('.', '-')
		for timePart in text.split('-'):
			if timePart.isdigit() == False:
				return False
		return True

	@staticmethod
	def isValidFieldValue(fieldType, fieldValue):
		if fieldValue == None or MetaDataYoutube.FIELD_SEPARATOR in fieldValue:
			return False
		match fieldType:
			case MetaDataYoutube.Field.NAME:
				return fieldValue != '' and fieldValue.isspace() == False
			case MetaDataYoutube.Field.LINK:
				return ' ' not in fieldValue and fieldValue.startswith('https://www.youtube.com/watch?v=') and fieldValue != MetaDataYoutube.getDefaultFieldValue(MetaDataYoutube.Field.LINK)
			case MetaDataYoutube.Field.CATEGORY:
				return ' ' not in fieldValue
			case MetaDataYoutube.Field.PROGRESS:
				return MetaDataYoutube.isTime(fieldValue)
			case MetaDataYoutube.Field.LENGTH:
				return MetaDataYoutube.isTime(fieldValue, True)
			case MetaDataYoutube.Field.WATCHED:
				return MetaDataYoutube.getIntVarValue(MetaDataYoutube.Field.WATCHED, fieldValue) is not None
			case MetaDataYoutube.Field.ADD_TIME:
				return MetaDataYoutube.isDatetime(fieldValue)
			case _:
				return False

	@staticmethod
	def isLoadableFieldType(fieldType):
		match fieldType:
			case MetaDataYoutube.Field.NAME:
				return True
			case MetaDataYoutube.Field.LINK:
				return True
			case _:
				return False

	@staticmethod
	def getDefaultFieldValue(fieldType):
		match fieldType:
			case MetaDataYoutube.Field.LINK:
				return 'https://www.example.com'
			case MetaDataYoutube.Field.CATEGORY:
				return 'LetsPlay'
			case MetaDataYoutube.Field.PROGRESS:
				return '0:00'
			case MetaDataYoutube.Field.LENGTH:
				return '0:00'
			case MetaDataYoutube.Field.WATCHED:
				return 'False'
			case MetaDataYoutube.Field.ADD_TIME:
				return '2000-01-01 0:00:00.0'
			case _:
				return ''

	@staticmethod
	def getDefaultFieldSets():
		fieldSets = {}
		fieldSets[MetaDataYoutube.Field.CATEGORY] = {MetaDataYoutube.getDefaultFieldValue(MetaDataYoutube.Field.CATEGORY)}
		return fieldSets

	@staticmethod
	def getIntVarValue(fieldType, strVarValue):
		match fieldType:
			case MetaDataYoutube.Field.WATCHED:
				if strVarValue == str(True):
					return int(True)
				elif strVarValue == str(False):
					return int(False)
				else:
					return None
			case _:
				return None

	@staticmethod
	def getStrVarValue(fieldType, intVarValue):
		match fieldType:
			case MetaDataYoutube.Field.WATCHED:
				return str(bool(intVarValue))
			case _:
				return None

	def getGridFieldData(self, fieldType):
		match fieldType:
			case MetaDataYoutube.Field.CATEGORY:
				return (GridField.Type.Combobox, 'getFieldStrVar', sorted(self.fieldSets[fieldType]), None)
			case MetaDataYoutube.Field.WATCHED:
				return (GridField.Type.Checkbutton, 'getFieldIntVar', 'fieldCallbackWithFieldType', 'Finished')
			case _:
				return (GridField.Type.TextEntry, 'getFieldStrVar', 'fieldCallback', 'pasteClipboardToStrVar')

	def __init__(self):
		self.metaData = []
		self.fieldSets = MetaDataYoutube.getDefaultFieldSets()
		self.readMetaData()

	def getFieldTypeName(self, fieldType):
		return fieldType.name.capitalize().replace('_', ' ')

	def getLinkByIdx(self, idx):
		return self.metaData[idx][MetaDataYoutube.Field.LINK.value]

	def getInfoTextByIdx(self, idx):
		infoText = self.metaData[idx][MetaDataYoutube.Field.NAME.value] + '\n'
		infoText += 'MetaData: '
		fields = []
		for fieldType in MetaDataYoutube.Field:
			if fieldType != MetaDataYoutube.Field.NAME:
				fields.append(self.metaData[idx][fieldType.value])
		infoText += MetaDataYoutube.FIELD_SEPARATOR.join(fields)
		return infoText

	def getFieldByIdx(self, fieldType, idx):
		return self.metaData[idx][fieldType.value]

	def getEntryByIdx(self, idx):
		return self.metaData[idx]

	def getIdxByField(self, fieldType, fieldValue):
		if MetaDataYoutube.isLoadableFieldType(fieldType):
			for idx in range(self.getEntryCount()):
				if self.metaData[idx][fieldType.value] == fieldValue:
					return idx
		return None

	def getIdxByName(self, name):
		if name != '':
			for idx in range(self.getEntryCount()):
				if self.metaData[idx][MetaDataYoutube.Field.NAME.value] == name:
					return idx
		return None

	def getEntryCount(self):
		return len(self.metaData)

	def setFieldByIdx(self, fieldType, idx, fieldValue):
		self.checkField(fieldType, fieldValue)
		self.metaData[idx][fieldType.value] = fieldValue

	def checkField(self, fieldType, fieldValue):
		if MetaDataYoutube.isValidFieldValue(fieldType, fieldValue) == False:
			raise ValueError('Invalid formating for ' + self.getFieldTypeName(fieldType) + ' (' + fieldValue + ')')
		elif fieldType in self.fieldSets:
			self.fieldSets.get(fieldType).add(fieldValue)

	def checkFields(self, fields):
		for fieldType in MetaDataYoutube.Field:
			self.checkField(fieldType, fields[fieldType.value])

	def addEntry(self, fields):
		fields[MetaDataYoutube.Field.ADD_TIME.value] = str(datetime.now())
		self.checkFields(fields)
		self.metaData.append(fields)

	def updateEntry(self, idx, fields):
		fields[MetaDataYoutube.Field.ADD_TIME.value] = str(datetime.now())
		self.checkFields(fields)
		for fieldType in MetaDataYoutube.Field:
			self.metaData[idx][fieldType.value] = fields[fieldType.value]

	def removeEntry(self, idx):
		self.metaData.pop(idx)

	def readMetaData(self):
		metaDataFile = open(MetaDataYoutube.FILE_NAME, 'r', encoding=MetaDataYoutube.ENCODING)
		lines = metaDataFile.readlines()
		self.metaData = []
		for line in lines:
			fields = line.strip().split(MetaDataYoutube.FIELD_SEPARATOR)
			self.checkFields(fields)
			self.metaData.append(fields)

	def writeMetaData(self):
		metaDataFormated = []
		for fields in self.metaData:
			metaDataFormated.append(MetaDataYoutube.FIELD_SEPARATOR.join(fields))
		with open(MetaDataYoutube.FILE_NAME, 'w', encoding=MetaDataYoutube.ENCODING)as metaDataFile:
			metaDataFile.write('\n'.join(metaDataFormated))