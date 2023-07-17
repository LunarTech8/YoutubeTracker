import tkinter as tk
from tkinter import ttk
from enum import Enum, auto

class GridField():
	class Type(Enum):
		Header = auto()
		Button = auto()
		Label = auto()
		DynamicLabel = auto()
		DigitEntry = auto()
		TextEntry = auto()
		Combobox = auto()

	def isFloatOrEmpty(text):
		return str(text) == '' or (text.lstrip('-').replace('.', '').isdigit() and text.count('.') <= 1)

	def isText(text):
		return text != None

	def add(root, row, column, width, type, arg1=None, arg2=None, arg3=None):
		if type == GridField.Type.DigitEntry:
			if arg2 != None:
				arg1.trace_add('write', arg2)
			vcmd = (root.register(GridField.isFloatOrEmpty), '%P')
			gridField = tk.Entry(root, justify='center', width=width, textvariable=arg1, validate='key', validatecommand=vcmd)
		elif type == GridField.Type.TextEntry:
			if arg2 != None:
				arg1.trace_add('write', arg2)
			vcmd = (root.register(GridField.isText), '%P')
			gridField = tk.Entry(root, justify='center', width=width, textvariable=arg1, validate='key', validatecommand=vcmd)
			if arg3 != None:
				gridField.bind("<Button-3>", lambda event, root=root, strVar=arg1: arg3(root, strVar))
		elif type == GridField.Type.Combobox:
			gridField = ttk.Combobox(root, justify='center', width=width-5, textvariable=arg1)
			gridField['values'] = arg2
		elif type == GridField.Type.Button:
			gridField = tk.Button(root, text=arg1, borderwidth=4, width=width-15, command=arg2)
		elif type == GridField.Type.Label:
			gridField = tk.Label(root, text=arg1, borderwidth=2, relief='sunken', width=width)
		elif type == GridField.Type.DynamicLabel:
			gridField = tk.Label(root, textvariable=arg1, borderwidth=2, relief='sunken', width=width)
		elif type == GridField.Type.Header:
			gridField = tk.Label(root, text=arg1, borderwidth=2, relief='groove', width=width)
		else:
			raise AttributeError('Invalid grid field type')
		gridField.grid(row=row, column=column)