import tkinter.ttk as ttk, tkinter as tk, tkinter.filedialog as filedialog
from sqlApi import DatabaseObj
from tkExtension import LabeledEntry, LabeledOptionMenu, Hovertip
import ttkthemes
import inspect, os

# Functions ===========================================

def is_num(arg):
    for c in arg:
        if c not in '1234567890.':
            return False
    return True

def showTable(num):
    global table, scrollBar
    table.destroy()
    scrollBar.destroy()

    obj = DatabaseObj(DBPATH[0])
    table = ttk.Treeview(treeviewFrame, columns=obj[obj.tables[num]]['columns'], show='headings', selectmode='browse')
    table.pack(fill='both', padx=(10, 0), pady=10, side='left', expand=True)

    scrollBar = ttk.Scrollbar(treeviewFrame, orient='vertical', command=table.yview)
    scrollBar.pack(side='right', fill='y', padx=(0, 10), pady=10)

    table.config(yscrollcommand=scrollBar.set)

    for column in table['columns']:
        table.column(column, width=120, minwidth=120)
        table.heading(column, text=column)

    for row in obj[obj.tables[num]]['values']:
        table.insert('', index='end', values=row)

    table['show'] = 'headings'

    SELECTED_TABLE[0] = num

def update():
    if table['columns']: showTable(SELECTED_TABLE[0])

    tableMenu.delete('0', 'end')
    for i, v in enumerate(DatabaseObj(DBPATH[0]).tables):
        tableMenu.add_command(label=v, command=lambda i=i: showTable(i))

def addRecord():
    obj = DatabaseObj(DBPATH[0])
    topLevel = tk.Toplevel()
    topLevel.title("Add Record")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    labeledEntryArray = [LabeledEntry(topLevel, text=column+':', width=280, font=("Segoe UI", 10))
                         for column in obj[obj.tables[SELECTED_TABLE[0]]]['columns']]
    for widget in labeledEntryArray: widget.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.add_record([x.get() for x in labeledEntryArray], obj.tables[SELECTED_TABLE[0]]),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def selectionChecker():
    if table.focus():
        buttonArray[1].state(['!disabled'])
        buttonArray[2].state(['!disabled'])
    else:
        buttonArray[1].state(['disabled'])
        buttonArray[2].state(['disabled'])
    root.after(1, selectionChecker)

def delRecord():
    obj = DatabaseObj(DBPATH[0])
    obj.delete_record(tuple(table.item(table.focus())['values']), obj.tables[SELECTED_TABLE[0]])
    update()

def modRecord():
    obj = DatabaseObj(DBPATH[0])
    topLevel = tk.Toplevel()
    topLevel.title("Modify Record")
    topLevel.config(padx=10, pady=10, bg="#DADADA")
    selectedItem = table.item(table.focus())['values']
    print(selectedItem)

    labeledEntryArray = [LabeledEntry(topLevel, text=column+':', width=280, font=("Segoe UI", 10))
                         for column in obj[obj.tables[SELECTED_TABLE[0]]]['columns']]

    for widget, arg in zip(labeledEntryArray, selectedItem):
        widget.pack(); widget.insert('0', arg)

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.replace_record(
                                                selectedItem,
                                                [int(x.get()) if is_num(x.get()) else x.get() for x in labeledEntryArray],
                                                obj.tables[SELECTED_TABLE[0]]
                                            ),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def changeDBPath():
    sel_path = filedialog.askopenfilename(defaultextension='.db', filetypes=(["Database File", '*.db'],))
    if sel_path:
        SELECTED_TABLE[0] = 0
        DBPATH[0] = sel_path
        buttonArray[0].state(['!disabled'])
        for button in buttonArray[3::]: button.state(['!disabled'])

        update()

def addColumn():
    obj = DatabaseObj(DBPATH[0])
    table_name = obj.tables[SELECTED_TABLE[0]]
    print(obj.schema(table_name))
    var = tk.StringVar()

    topLevel = tk.Toplevel()
    topLevel.title("Add Column")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    columnName = LabeledEntry(topLevel, text="Name:", font=('Segoe UI', 10))
    columnName.pack()
    columnType = LabeledOptionMenu(topLevel, "Type:", var, ['Integer', 'Real', 'Text', 'Blob'], font=('Segoe UI', 10))
    columnType.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.add_column(table_name, columnName.get(), var.get()),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def renameColumn():
    obj = DatabaseObj(DBPATH[0])
    table_name = obj.tables[SELECTED_TABLE[0]]

    topLevel = tk.Toplevel()
    topLevel.title("Rename Column")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    columnName = LabeledEntry(topLevel, text="Column:", font=('Segoe UI', 10))
    columnName.pack()

    columnRename = LabeledEntry(topLevel, text="New Name:", font=('Segoe UI', 10))
    columnRename.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.rename_column(table_name, columnName.get(), columnRename.get()),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def deleteColumn():
    obj = DatabaseObj(DBPATH[0])
    table_name = obj.tables[SELECTED_TABLE[0]]

    topLevel = tk.Toplevel()
    topLevel.title("Delete Column")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    columnName = LabeledEntry(topLevel, text="Column:", font=('Segoe UI', 10))
    columnName.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.delete_column(table_name, columnName.get()),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def deleteTable():
    obj = DatabaseObj(DBPATH[0])

    topLevel = tk.Toplevel()
    topLevel.title("Delete Table")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    tableName = LabeledEntry(topLevel, text="Table:", font=('Segoe UI', 10))
    tableName.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.drop_table(tableName),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def renameTable():
    obj = DatabaseObj(DBPATH[0])

    topLevel = tk.Toplevel()
    topLevel.title("Delete Table")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    tableName = LabeledEntry(topLevel, text="Table:", font=('Segoe UI', 10))
    tableName.pack()

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4),
                           command=lambda: [obj.delete_table(tableName),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

def parseColumnCode(arg):
    splitArg = arg.split('-')
    arr = []
    for tuple in splitArg:
        arr.append(tuple.strip('()'))
    return arr

def addTable():
    obj = DatabaseObj(DBPATH[0])

    topLevel = tk.Toplevel()
    topLevel.title("Add Table")
    topLevel.config(padx=10, pady=10, bg="#DADADA")

    tableName = LabeledEntry(topLevel, text="Table:", font=('Segoe UI', 10), config={"width":30})
    tableName.pack(fill='x')

    colData = LabeledEntry(topLevel, text="Column Data:", font=('Segoe UI', 10), config={"width":30})
    colData.pack(fill='x')

    Hovertip(colData, text="Format: (name dtype)-(name2 dtype2)...", hover_delay=500)

    submitBtn = ttk.Button(topLevel, text="Submit", padding=(10, 4), width=50,
                           command=lambda: [obj.add_table(tableName.get(), parseColumnCode(colData.get())),
                                            update()])
    submitBtn.pack(fill='x')
    topLevel.mainloop()

# Constants ===========================================

SELECTED_TABLE = [0]
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
DBPATH = [PATH+r'\testingdb\testingdb.db']

# GUI =================================================

root = ttkthemes.ThemedTk(theme='scidblue')
root.title("DB Manager")
root.state("zoomed")
root['bg'] = '#DADADA'
root.resizable(0, 0)

style = ttk.Style()
style.configure('.', font=('Segoe UI', 10))

topMenu = tk.Menu(root, type='menubar', font='Gadugi 8')
root['menu'] = topMenu

tableMenu = tk.Menu(root, font='Gadugi 8')

topMenu.add_command(label="Open DB", font='Gadugi 8', command=changeDBPath)
topMenu.add_cascade(label="Tables", menu=tableMenu)

buttonArrayFrame = ttk.Frame(root, padding=(10, 10, 10, 0), style='Card.TFrame')
buttonArrayFrame.pack(side='left', fill='y', pady=10, padx=(10, 0))

treeviewFrame = ttk.Frame(root); treeviewFrame.pack_propagate(0)
treeviewFrame.pack(side='right', fill='both', expand=True)

table = ttk.Treeview(treeviewFrame, columns=[''], show='headings')
table.pack(fill='both', padx=(10, 0), pady=10, side='left', expand=True)

scrollBar = ttk.Scrollbar(treeviewFrame, orient='vertical', command=table.yview)
scrollBar.pack(side='right', fill='y', padx=(0, 10), pady=10)

table.config(yscrollcommand=scrollBar.set)

buttonArray = [ttk.Button(buttonArrayFrame, text=x, padding=(5, 5), width=15, style='Accent.TButton',
               command=command, state='disabled')
               for x, command in
               zip(['Add Record', 'Modify Record', 'Delete Record', 'Rename Table', 'Delete Table',
                    'Create Table', 'Create Column', 'Rename Column', 'Delete Column'],
               [addRecord, modRecord, delRecord, renameTable, deleteTable, addTable, addColumn, renameColumn, deleteColumn])]

for i, button in enumerate(buttonArray):
    if i % 3 == 0 and i:
        ttk.Separator(buttonArrayFrame, orient='horizontal').pack(pady=(0, 10), fill='x')
    button.pack(pady=(0, 10))

selectionChecker()
root.mainloop()
