#!/usr/bin/env python3
from html.parser import HTMLParser
import os
from bs4 import BeautifulSoup as bs

# 1. first we check which components we need
# 2. we compile them and save the data (recursive)
# 3. we go though the file and replaced the component
#    definition with the compiled data

# 1.0  We go though the file we want to compile
# 2.0  If we find a component
# 2.1  we add a new component to a list that holds the
#      component definition and the compiled component
# 3.0  We have gone though the whole file and all components
#      are saved to the list.
# 4.0  we loop though the saved components and replace the
#      definitions with the compiled

# 1 We go though the file and add all tags as components
# 2 if the componeonts can be compiled we compile them and
#   set there values to the compiled value

components = ["card"]

class Component:
    def __init__(self, name="",srcpath="", props=[], definition="",end_definition=""):
        self.name = name
        self.srcpath = srcpath
        self.props = props
        self.definition = definition
        self.end_definition = end_definition

    def get_child(self):
        asd = ""
        for name,value in self.props:
            if name=="child":
                if value != None:
                    asd += value
        return asd

    def get_string(self):
        return self.definition+self.get_child()+self.end_definition

    def __str__(self):
        return str(self.__dict__)

    def set_end_definition(self,definition):
        self.end_definition = "" if definition == self.definition else definition


    def add_child_content(self,content):
        i = 0
        for name,value in self.props:
            if name == "child":
                self.props[i] = ("child",value+content)
                return 0
            i+=1
        self.props.append(("child",content))

def get_content(file):
    with open(file,"r") as f:
        return( bs(f.read(), features="html.parser").prettify())

    
class Webers(HTMLParser):
    def __init__(self, srcpath="./",output="./out"):
        self.srcpath    = srcpath
        self.output     = output
        self.components = []
        self.current_compile = ""

        self.fetch_project_components() #all components in the project

        self.current_components = []
        self.finished_components = []

        super().__init__()

    def get_string_from_file(self,file,x,y):
        lines = get_content(file).split("\n")
        count = 0
        for line in lines:
            count += 1
            if count == y:
                return(line)

    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag,attrs)

        (y,x) = self.getpos()
        definition = self.get_string_from_file(self.current_compile,x,y)

        found = False
        for comp in self.components:
            if comp.name.lower() == tag:
                #print("Component found, add component with src")
                comp.definition = definition
                comp.props = attrs
                self.current_components.append(comp)
                found = True
        if not found:
            #print("Add component ",tag)
            self.current_components.append(Component(name=tag,props=attrs,definition=definition))

        for i in range(len(self.current_components)-1):
            privius = self.current_components[i]
            newst = self.current_components[len(self.current_components)-1]
            privius.add_child_content(newst.definition)

    def printComps(self):
        for comp in self.current_components:
            print(comp)
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        (y,x) = self.getpos()
        end_definition = self.get_string_from_file(self.current_compile,x,y)
        #print("END TAG:",end_definition,x,y)
        #self.printComps()
        close_component = self.current_components.pop()
        close_component.set_end_definition(end_definition)
        for comp in self.current_components:
            comp.add_child_content(close_component.end_definition)
        self.finished_components.append(close_component)



    def handle_data(self, data):
        #print("Encountered some data  :", data)
        if len(self.current_components) > 0:
            print("adds",data)
            for comp in self.current_components:
                pass
                #print(comp.name)
                #comp.add_child_content(data)

    def fetch_project_components(self):
        f = []
        for path, subdirs, files in os.walk(self.srcpath):
            for name in files:
                if ".html" in name and name not in self.current_compile:
                    f.append(Component(name=name.replace(".html",""),
                                       srcpath=os.path.join(path,name)))
        self.components = f
        return f

    def compile(self, file):
        # add the components above as children to the ones under
        self.current_compile = file
        cont = get_content(self.current_compile)
        #print(cont)
        parser.feed(cont)
        #comp = self.finished_components.pop()
        #print(comp)
        for i in range(len(self.finished_components)-1):
            #print(bs(self.finished_components[i].get_string(), features="html.parser").prettify())
            print(self.finished_components[i].props)
parser = Webers()
parser.compile("./test/index.html")
