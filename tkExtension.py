import tkinter.ttk as ttk
from idlelib .tooltip import Hovertip

class LabeledWidget(ttk.Frame):
    def __init__(self,
                 master,
                 text,
                 widget,
                 padding=(0,0,5,0),
                 font=('TkDefaultFont', 10),
                 width=200,
                 height=40,
                 config=None):

        super().__init__(master, width=width, height=height, padding=padding)
        if config is None: config = {}
        self.pack_propagate(False)

        self.label = ttk.Label(self, text=text, font=font)
        self.entry = widget(self, **config)

        self.label.pack(side='left')
        self.entry.pack(side='right')

    def entry_config(self, **kwargs):self.entry.config(**kwargs)
    def label_config(self, **kwargs):self.label.config(**kwargs)
    def get(self): return self.entry.get()
    def insert(self, index, arg): self.entry.insert(index, arg)
    def delete(self, first, last): self.entry.delete(first, last)
    def replace(self, first, last, arg):
        self.entry.delete(first, last)
        self.entry.insert(first, arg)

class LabeledEntry(LabeledWidget):
    def __init__(self,
                 master,
                 text,
                 padding=(0,0,5,0),
                 font=('TkDefaultFont', 10),
                 width=200,
                 height=40,
                 config=None):

        """A mega widget formed from a label and an entry widget. Most useful in form applications."""

        super().__init__(master, text, ttk.Entry, font=font, width=width, height=height, padding=padding, config=config)

class LabeledOptionMenu(LabeledWidget):
    def __init__(self,
                 master,
                 text,
                 variable,
                 values,
                 padding=(0,0,5,0),
                 font=('TkDefaultFont', 10),
                 width=200,
                 height=40,
                 config=None):

        """A mega widget formed from a label and an optionmenu widget. Most useful in form applications."""

        super().__init__(master, text, ttk.Frame, font=font, width=width, height=height, padding=padding, config=config)

        self.entry = ttk.OptionMenu(self, variable, None, *values)
        self.entry.pack_forget()
        self.entry.pack(side='right')