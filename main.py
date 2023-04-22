#!/bin/python
import pathlib
from dj2 import *
from flagser import *
import os
from watcher import *

srcpath = "./src"
outpath = "./out/"

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
            props[key] = comps.split("=")[ec].replace(" "+comps.split("=")[ec].split(" ")[-1],"")
            ec+=1
            key = ""
            listenKey = False

        if listenKey:
            key += c

    return props
# search for components
def componentsInHtml(file=""):
    files = getFiles()
    # get the components that was imported
    comps = {}
    for _file in files:
        extention = pathlib.Path(_file).suffix
        if extention == ".html":
            compname = os.path.basename(_file).replace(extention,"")
            comps[compname] = _file

    components = []
    listenForCompName = False
    compName = ""
    comp = ""

    for c in file:
        if not c:
            break
        # we begin to listen for compname
        if(c == "<") :
            listenForCompName = True
            comp += c
            continue
        # we end listen and we add the component read to the components list
        if(c == ">") :
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

    for component in components:
        # file = file.replace("<"+component["component"]+"></"+component["name"]+">", component["file"])
        definition = "<"+component["component"]+">" 
        endDefinition = "</"+component["name"]+">"

        start = file.find(definition) + len(definition)
        end = file.find(endDefinition)

        child = file[start : end]

        props = component["props"]
        props["child"] = child
        component["props"] = props


    return components

def getComponent(component) -> str:
    file = ""
    with open(component["path"], "r") as f:
        file = f.read()

    for prop in component["props"]:
        file = file.replace("$"+prop,component["props"][prop].replace('"',""))
    return file

def replaceComponent(file="", components=[]):
    # replaces the component definitions with he compiled
    for component in components:
        # replace the componenet definition with the component contenet
        file = file.replace("<"+component["component"]+">", component["file"])
        file = file.replace("<"+component["component"]+"/>", component["file"])
        file = file.replace("</"+component["name"]+">", "")

        # remove the child prop from the file
        try:
            file = file.replace(component["props"]["child"], "")
        except:
            pass


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

# return the content of a file
def getContent(path):
    with open(path,"r") as f:
        return f.read()

def compiles(file="",path="./"):
    p = PyTml()
    content = p.compiles(file)
    # gather the components need to compile this file
    neededComps = componentsInHtml(file=content)
    #print(path, neededComps)
    # for every component compule that file
    for neededComp in neededComps:
        compPath = neededComp["path"].replace("./","/")
        srcpath = os.path.dirname(path)
        if "./" in compPath:
            # removes last subfolder to go up a folder
            srcpath = os.path.dirname(srcpath)
            compPath = compPath.replace("./","/")
        compPath = neededComp["path"]
        neededComp["file"] = compiles(getContent(compPath), compPath)
        #print(path, neededComp["file"])
    # replace the compoents in my file with the compiled components
    return replaceComponent(file=content, components=neededComps)

def output(filename, out):

    # create the path if it does not exist
    outputdir = os.path.dirname(outpath)
    if not os.path.exists(outputdir):
        pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)

    # if the output path is a file write to that file
    if os.path.basename(outpath) :
        name = outpath#os.path.basename(outpath)
    else:
        name = outpath+os.path.basename(filename)

    with open(name,"w") as f:
        f.write(out)

def compileAll(args):
    if args[0] == "all":
        files = getFiles()
        for file in files:
            p = PyTml()
            content = p.compiles(getContent(file))
            c = compiles(content, file)
            output(file, c)
    else:
        for file in args:
            c = compiles(getContent(file), file)
            output(file, c)

def start(args):
    # start the file watcher
    w = watcher()
    w.start(edited=lambda : compileAll(["all"]), ignore=["./out"])

def setOutPath(args):
    global outpath
    outpath = args[0]

manager = FlagManager([
    Flag("-p", "--path", "sets the src path from", setPath),
    Flag("-o", "--out-path", "sets the out path", setOutPath),
    Flag("-c", "--compile", "compile a file or all with all keyword (-c all)", compileAll),
    Flag("start", "--start", "auto compiles", start),
])
manager.check()

import os
