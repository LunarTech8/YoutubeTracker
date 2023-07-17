from enum import Enum

def isFloat(text):
	return text.lstrip('-').replace('.', '').isdigit()and text.count('.') <= 1

class MetaDataYoutube:
	FILE_NAME = 'MetaDataYoutube.txt'
	FIELD_SEPARATOR = ' | '

	class Field(Enum):
		NAME = 0
		LENGTH = 1
		LINK = 2

	def isValidFieldValue(self, fieldType, fieldValue):
		if fieldValue == None or fieldValue == '' or MetaDataYoutube.FIELD_SEPARATOR in fieldValue:
			return False
		match fieldType:
			case self.Field.NAME:
				return True
			case self.Field.LENGTH:
				return fieldValue.count(':') > 0 and fieldValue.replace(':', '').isdigit()
			case self.Field.LINK:
				return ' ' not in fieldValue and fieldValue.startswith('https://')
			case _:
				return False

	def isLoadableFieldType(self, fieldType):
		match fieldType:
			case self.Field.NAME:
				return True
			case self.Field.LENGTH:
				return False
			case self.Field.LINK:
				return True
			case _:
				return False

	def getDefaultFieldValue(self, fieldType):
		match fieldType:
			case self.Field.LINK:
				return 'https://www.example.com'
			case self.Field.LENGTH:
				return '0:00'
			case _:
				return ''

	def __init__(self):
		self.metaData = []
		self.fieldSets = {}
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

	def getSortedFieldSet(self, fieldType):
		if fieldType in self.fieldSets:
			return sorted(self.fieldSets[fieldType])
		else:
			return None

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

	def getEntryCount(self):
		return len(self.metaData)

	def checkFields(self, fields):
		for fieldType in self.Field:
			if self.isValidFieldValue(fieldType, fields[fieldType.value]) == False:
				raise ValueError('Invalid formating for ' + self.getFieldTypeName(fieldType) + ' (' + fields[fieldType.value] + ')')
			elif fieldType in self.fieldSets:
				self.fieldSets.get(fieldType).add(fields[fieldType.value])

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