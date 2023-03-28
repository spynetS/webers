from flagser import *
import os
from watcher import *

srcpath = "./"

def getProps(component:str):
    props = {}
    listenKey = True
    key = ""
    comps = ""
    # remove the name of the component
    # by spliting spaces and adding every one except the first to a str
    for i in (component.split(' ')[1:]):
        comps += i+" "

    ec = 1
    # for char in string if we find a equals we ad the key and the value
    value = False
    for c in comps:
        if c == '"':
            value = not value
        if c == " " and not value: 
            listenKey = True
            continue
        if c == "=":
            props[key] = comps.split("=")[ec].replace(" class","")
            ec+=1
            key = ""
            listenKey = False
            
        if listenKey:
            key += c
            

    return props  

# search for components
def componentsInHtml(file, path=""):
    if path != "":
        f = open(path, "r")
        file = f.read()
    comps = {}
    for line in file.split("\n"):
        if "import" in line:
            compname = line.split(" ")[1]
            comps[compname] = line.split(" ")[3].replace("\n", "").replace('"', "")

    components = []
    listenForCompName = False
    compName = ""
    comp = ""
    
    for c in file:
        if not c:
            break
        
        if(c == "<") :
            listenForCompName = True
            comp += c
            continue
        
        if(c == ">" or c == "/") :
            comp += "/>"
            splittet = compName.split(" ")
            if(splittet[0] in comps.keys()):
                components.append({"name":splittet[0], "props": getProps(compName), "component":compName, "path":comps[splittet[0]]})
            comp = ""
            listenForCompName = False
            compName = ""

        if listenForCompName:
            comp += c
            compName += c

    return components

def getComponent(component) -> str:
    file = ""
    with open(component["path"], "r") as f:
        file = f.read()
    
    for prop in component["props"]:
        file = file.replace("$"+prop,component["props"][prop].replace('"',""))
    return file

def replaceComponent(file="",path="", components=[]):
    if path != "":
        with open(path, "r") as f:
            file = f.read()
    
    tmp = ""
    for line in file.split("\n"):
        if "import" not in line: tmp+=line+"\n"

    file = tmp

    for component in components:
        file = file.replace("<"+component["component"]+"></"+component["name"]+">", component["file"]) 
        file = file.replace("<"+component["component"]+"/>", component["file"]) 
        for prop in component["props"]:
            file = file.replace("$"+prop,component["props"][prop].replace('"',""))

        
    return file

def setPath(args):
    global srcpath
    srcpath = args[0]


def getFiles():
    global srcpath
    f = []
    for path, subdirs, files in os.walk(srcpath):
        for name in files:
            f.append(os.path.join(path,name))
    return f

def compile(file="", path=""):
    global srcpath
    neededComps = componentsInHtml(file, path=path)
    for neededComp in neededComps:
        neededComp["file"] = compile(path=srcpath+neededComp["path"])

    return replaceComponent(path=path, file=file, components=neededComps) 

def compileAll(args):
    for file in getFiles():
        print("./out/"+os.path.basename(file))
        with open("./out/"+os.path.basename(file),"w") as f:
            pass
        #c = compile(path=file) 
        #print(c)
        #f.write(c)
        #f.close()


def start(args):
    w = watcher()
    w.start(edited=lambda args : compileAll())
    
manager = FlagManager([
    Flag("-p", "--path", "sets the src path from", setPath),
    Flag("-c", "", "auto update", compileAll),
    Flag("-start", "", "auto update", start),
])
manager.check()