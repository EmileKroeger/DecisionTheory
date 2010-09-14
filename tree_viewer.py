import Tkinter

from Tkinter import *

INDENT = "    "

class NodeList:
    def __init__(self):
        self.list = []

    def append(self, item):
        self.list.append(item)

    def unroll(self, viewer, depth=0):
        for item in self.list:
            if isinstance(item, str):
                viewer.append_line(INDENT * depth + item)
            else:
                item.unroll(viewer, depth)

class ExpandableNode:
    def __init__(self, title):
        self.title = title
        self.expanded = False
        self.nodelist = NodeList()

    def toggle(self):
        self.expanded = not self.expanded

    def append(self, item):
        self.nodelist.append(item)

    def unroll(self, viewer, depth=0):
        if self.expanded:
            line = INDENT * depth + "[-] " + self.title
            viewer.append_line_callback(line, self.toggle)
            self.nodelist.unroll(viewer, depth + 1)
        else:
            line = INDENT * depth + "[-] " + self.title
            viewer.append_line_callback(line, self.toggle)

class NodeBuilder:
    def __init__(self):
        self.root = NodeList()
        self.current = [self.root]

    def add(self, line):
        self.current[-1].append(line)

    def enter(self, title):
        expandable = ExpandableNode(title)
        self.current[-1].append(expandable)
        self.current.append(expandable)

    def exit(self):
        self.current = self.current[:-1]

class TreeViewer:
    def __init__(self, rootnode):
        self.root = None
        self.callbacks = {}
        self.rootnode = rootnode

    def append_line_callback(self, line, callback):
        self.append_line(line)
        self.callbacks[self.listbox.size() - 1] = callback

    def append_line(self, line):
        self.listbox.insert(END, line)

    def handle_click(self, event):
        selection = self.listbox.curselection()
        if len(selection) == 1:
            index = int(selection[0])
            if index in self.callbacks:
                self.callbacks[index]()
                self.rebuild_list()
                

    def rebuild_list(self):
        self.callbacks = {}
        self.listbox.delete(0, self.listbox.size())
        self.rootnode.unroll(self)

    def build_listbox(self):
        lb = Listbox(self.root)

        self.yScroll  =  Scrollbar(self.root, orient=VERTICAL)
        self.yScroll.grid(row=0, column=1, sticky=N+S )

        self.xScroll  =  Scrollbar(self.root, orient=HORIZONTAL)
        self.xScroll.grid(row=1, column=0, sticky=E+W)

        self.listbox = Listbox(self.root,
             xscrollcommand=self.xScroll.set,
             yscrollcommand=self.yScroll.set)
        self.listbox.grid(row=0, column=0, sticky=N+S+E+W)
        self.xScroll["command"]  =  self.listbox.xview
        self.yScroll["command"]  =  self.listbox.yview

        self.listbox.bind("<Double-Button-1>", self.handle_click)

        self.rebuild_list()
        
    def run(self):
        self.root = Tk()

        #self.root.grid(sticky=N+S+E+W)

        top=self.root.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.build_listbox()

        self.root.mainloop()

if __name__ == "__main__":
    builder = NodeBuilder()
    builder.add("one")
    builder.add("two")
    builder.enter("3")
    builder.add("4")
    builder.enter("3df")
    builder.add("dfd4")
    builder.add("5df")
    builder.add("6")
    builder.exit()
    builder.add("df5")
    builder.add("6df")
    builder.exit()
    builder.enter("df3")
    builder.add("4")
    builder.add("5f")
    builder.add("6")
    builder.exit()
    builder.add("last")
    tv = TreeViewer(builder.root)
    tv.run()
