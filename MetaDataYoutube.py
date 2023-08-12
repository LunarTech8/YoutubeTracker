from enum import Enum

class MetaDataYoutube:
	class Field(Enum):
		NAME = 0
		LINK = 1
		CATEGORY = 2
		PROGRESS = 3
		LENGTH = 4
		WATCHED = 5

	FILE_NAME = 'MetaDataYoutube.txt'
	FIELD_SEPARATOR = ' --- '
	SORTED_FIELD_TYPES = (Field.PROGRESS, Field.LENGTH, Field.CATEGORY, Field.NAME, Field.LINK, Field.WATCHED)

	def isTime(text, noLeadingZero=False):
		if noLeadingZero and text.startswith('0'):
			return False
		noMaxValue = (text.count(':') == 2)
		for timePart in text.split(':', 2):
			if (timePart == '' or (timePart.isdigit() and (noMaxValue or (int(timePart) <= 60 and len(timePart) <= 2)))) == False:
				return False
			noMaxValue = False
		return True

	def isValidFieldValue(self, fieldType, fieldValue):
		if fieldValue == None or MetaDataYoutube.FIELD_SEPARATOR in fieldValue:
			return False
		match fieldType:
			case self.Field.NAME:
				return True
			case self.Field.LINK:
				return ' ' not in fieldValue and fieldValue.startswith('https://') and fieldValue != self.getDefaultFieldValue(self.Field.LINK)
			case self.Field.CATEGORY:
				return ' ' not in fieldValue
			case self.Field.PROGRESS:
				return MetaDataYoutube.isTime(fieldValue)
			case self.Field.LENGTH:
				return MetaDataYoutube.isTime(fieldValue, True)
			case self.Field.WATCHED:
				return fieldValue in self.getSortedFieldSet(self.Field.WATCHED)
			case _:
				return False

	def isLoadableFieldType(self, fieldType):
		match fieldType:
			case self.Field.NAME:
				return True
			case self.Field.LINK:
				return True
			case _:
				return False

	def getDefaultFieldValue(self, fieldType):
		match fieldType:
			case self.Field.LINK:
				return 'https://www.example.com'
			case self.Field.CATEGORY:
				return 'LetsPlay'
			case self.Field.PROGRESS:
				return '0:00'
			case self.Field.LENGTH:
				return '0:00'
			case self.Field.WATCHED:
				return 'False'
			case _:
				return ''

	def getDefaultFieldSets(self):
		fieldSets = {}
		fieldSets[self.Field.CATEGORY] = {self.getDefaultFieldValue(self.Field.CATEGORY)}
		fieldSets[self.Field.WATCHED] = set(self.getSortedFieldSet(self.Field.WATCHED))
		return fieldSets

	def getSortedFieldSet(self, fieldType):
		if fieldType == self.Field.WATCHED:
			return ['True', 'False']
		elif fieldType in self.fieldSets:
			return sorted(self.fieldSets[fieldType])
		else:
			return None

	def __init__(self):
		self.metaData = []
		self.fieldSets = self.getDefaultFieldSets()
		self.readMetaData()

	def getFieldTypeName(self, fieldType):
		return fieldType.name.capitalize().replace('_', ' ')

	def getLinkByIdx(self, idx):
		return self.metaData[idx][self.Field.LINK.value]

	def getInfoTextByIdx(self, idx):
		infoText = self.metaData[idx][self.Field.NAME.value] + '\n'
		infoText += 'MetaData: '
		fields = []
		for fieldType in self.Field:
			if fieldType != self.Field.NAME:
				fields.append(self.metaData[idx][fieldType.value])
		infoText += MetaDataYoutube.FIELD_SEPARATOR.join(fields)
		return infoText

	def getFieldByIdx(self, fieldType, idx):
		return self.metaData[idx][fieldType.value]

	def getEntryByIdx(self, idx):
		return self.metaData[idx]

	def getIdxByField(self, fieldType, fieldValue):
		if self.isLoadableFieldType(fieldType):
			for idx in range(self.getEntryCount()):
				if self.metaData[idx][fieldType.value] == fieldValue:
					return idx
		return None

	def getIdxByName(self, name):
		if name != '':
			for idx in range(self.getEntryCount()):
				if self.metaData[idx][self.Field.NAME.value] == name:
					return idx
		return None

	def getEntryCount(self):
		return len(self.metaData)

	def setFieldByIdx(self, fieldType, idx, fieldValue):
		self.checkField(fieldType, fieldValue)
		self.metaData[idx][fieldType.value] = fieldValue

	def checkField(self, fieldType, fieldValue):
		if self.isValidFieldValue(fieldType, fieldValue) == False:
			raise ValueError('Invalid formating for ' + self.getFieldTypeName(fieldType) + ' (' + fieldValue + ')')
		elif fieldType in self.fieldSets:
			self.fieldSets.get(fieldType).add(fieldValue)

	def checkFields(self, fields):
		for fieldType in self.Field:
			self.checkField(fieldType, fields[fieldType.value])

	def addEntry(self, fields):
		self.checkFields(fields)
		self.metaData.append(fields)

	def updateEntry(self, idx, fields):
		self.checkFields(fields)
		for fieldType in self.Field:
			self.metaData[idx][fieldType.value] = fields[fieldType.value]

	def readMetaData(self):
		metaDataFile = open(MetaDataYoutube.FILE_NAME, 'r')
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
		with open(MetaDataYoutube.FILE_NAME, 'w')as metaDataFile:
			metaDataFile.write('\n'.join(metaDataFormated))