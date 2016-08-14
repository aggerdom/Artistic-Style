from sys import version_info
from functools import partial

if version_info.major == 2:
    import Tkinter as tk
    import tkFileDialog as filedialog
    # import tkMessageBox as messagebox
    # import tkColorChooser as colorchooser
    # import tkCommonDialog as commondialog
    # import tkFont as font
elif version_info.major >= 3:
    import tkinter as tk
    # from tkinter import messagebox
    from tkinter import filedialog
    # from tkinter import colorchooser
    # from tkinter import commondialog
    # from tkinter import font
from collections import OrderedDict, namedtuple


class FileChooser(tk.Frame):
    def __init__(self, master, label="FileChooser", op=filedialog.askopenfilename):
        tk.Frame.__init__(self, master=master)
        self.master = master
        self.label = tk.Label(self, text=label)
        self.entry_var = tk.StringVar(self.master)
        self.entry = tk.Entry(self, textvariable=self.entry_var, text='Entry')
        self.choice_button = tk.Button(self, text='^', command=self.on_button)
        self.label.pack(side='left', anchor='e')
        self.entry.pack(side='left', fill='x', expand='true')
        self.choice_button.pack(side='left')
        self.op = op

    def on_button(self):
        chosen = self.op()
        if chosen != '':
            self.entry.delete(0, tk.END)
            self.entry.insert(0, chosen)

    def get(self):
        return self.entry_var.get()


class ControlPanelBase(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self, None)


class ControlPanel(tk.Frame):
    def __init__(self):
        self.base = ControlPanelBase()
        tk.Frame.__init__(self, master=self.base)
        self._realroot = self.nametowidget('.')
        self._realroot.withdraw()
        self._params = {}
        self._params_internal = []
        self._need_packed = []
        self._add_pack(self, expand=True, fill='x', anchor='nw')
        self._menubar = tk.Menu(self.base)
        self.base.config(menu=self._menubar)

    def add_folder_chooser(self, paramname,  text=None , op=filedialog.askdirectory  ):
        if text is None:
            text = paramname
        chooser = FileChooser(self, label=text, op=op)
        self._params[paramname] = chooser.get
        self._add_pack(chooser, side='top', anchor='nw', expand=True, fill='x')

    def add_filepath_chooser(self, paramname, label=None, op=filedialog.asksaveasfilename):
        if label is None:
            label = paramname
        chooser = FileChooser(self, label, op=op)
        self._add_pack(chooser, side='top', expand=True, fill='x')
        self._params[paramname] = chooser.get

    def add_checkbox(self, paramname, text=None, default=False, help=None):
        choice = tk.BooleanVar(self)
        cbox = tk.Checkbutton(self, text=text, variable=choice)
        self._add_pack(cbox, side='top', expand=True, fill='x')
        self._params[paramname] = choice.get

    def add_entry(self, paramname, text=None, entrytype=str):
        if text is None:
            text = paramname
        var = tk.StringVar()
        entryframe = tk.Frame(self)
        label = tk.Label(entryframe, text=text)
        entry = tk.Entry(entryframe, textvariable=var)
        self._add_pack(entryframe, side='top', expand=True, fill='x')
        self._add_pack(label, side='left')
        self._add_pack(entry, side='left', fill='x', expand=True)
        self._params[paramname] = var.get

    def add_button_box(self, paramname, choices):
        raise NotImplementedError

    def add_menu_command(self):
        raise NotImplementedError

    def _add_pack(self, w, *args, **kwargs):
        self._need_packed.append((w, args, kwargs))

    def _do_pack(self):
        for w, args, kwargs in self._need_packed:
            w.pack(*args, **kwargs)

    def destroy(self):
        super(ControlPanel, self).destroy()  # destroy this panel
        self._realroot.destroy()  # destroy the root Tk instance

    def mainloop(self, n=0):
        self.okbutton = tk.Button(self, bg='green1',
                                  text='Ok!', command=self.destroy)
        self._add_pack(self.okbutton)
        self._do_pack()
        self.base.mainloop()
        return {k: getter() for k, getter in self._params.items()}

def demo():
    panel = ControlPanel()
    panel.add_checkbox('Foo', "Drop Non-FullSize")
    panel.add_entry("SomeEntry")
    panel.add_filepath_chooser("filechoice1", "Choose a file")
    panel.add_folder_chooser('folderchoice', 'choose a folder', op=partial(filedialog.askdirectory, initialdir='./', title="Select what folder to save the image segments to"))
    choices = panel.mainloop()
    print(choices)
