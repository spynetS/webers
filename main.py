#!/bin/python
import pathlib
from PyTml import *
from flagser import *
import os
from watcher import watcher
from bs4 import BeautifulSoup as bs

srcpath = "./"
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
        if c == "/" and listenForCompName == True:
            splittet = compName.split(" ")
            if splittet[0] in comps.keys():
                components.append({"name":compName, "props": getProps(compName),"have_child":False, "component":compName, "path":comps[splittet[0]]})
                comp = ""
                listenForCompName = False
                compName = ""

        # we end listen and we add the component read to the components list
        if c == ">" and listenForCompName:
            comp += "/>"
            splittet = compName.split(" ")

            if(splittet[0] in comps.keys()):
                components.append({"name":splittet[0], "props": getProps(compName),"have_child":True, "component":compName, "path":comps[splittet[0]]})
                
            comp = ""
            listenForCompName = False
            compName = ""

        if listenForCompName:
            comp += c
            compName += c

    for component in components:
        # file = file.replace("<"+component["component"]+"></"+component["name"]+">", component["file"])
        if component["have_child"] == True:
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

def replacePropNameWithPropValue(file, prop_name, prop_value):
    #replace the $name with the name
    name = ""
    listen = False;
    new_file = ""
    for c in file:
        if c == "$":
            listen = True
        if listen and c == '"' or c == "<" or c == " " :
            if name == "$"+prop_name:
                #print("replace",prop_name, "with",prop_value)
                new_file+=prop_value
            else:
                new_file+=name
            name = ""
            listen = False
        if listen:
            name += c
        else:
            new_file += c
            #print(c,end="")
    return new_file


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

def setComponentProps(component_content,component):
    file = component_content
    for prop in component["props"]:
        prop_value = component["props"][prop].replace('"',"") # remove " from string
        file = replacePropNameWithPropValue(file,prop,prop_value)
    return file


def compiles(file="",path="./"):
    p = PyTml()
    content = p.compiles(file).replace("\n","")
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
        component_content = setComponentProps(getContent(compPath),neededComp)
        neededComp["file"] = compiles(component_content, compPath)
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
        f.write(bs(out, features="html.parser").prettify())
        #f.write(out)

def compileAll(args):
    if len(args) == 0 or args[0] == "all":
        files = getFiles()
        for file in files:
            p = PyTml()
            if ".html" in file:
                content = p.compiles(getContent(file)).replace("\n","")
                c = compiles(content, file)
                output(file, c)
            else:
                output(file, getContent(file))

    else:
        for file in args:
            c = compiles(getContent(file), file)
            output(file, c)

def start(args):
    # start the file watcher
    compileAll([])
    w = watcher()
    w.start(edited=lambda : compileAll(args), ignore=["./out"])

def setOutPath(args):
    global outpath
    outpath = args[0]

def generateExample(args):
    path = "src"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:

       # Create a new directory because it does not exist
       os.makedirs(path)
       print("The new directory is created!")
    
    with open("./src/index.html","w") as f:
        f.write("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>
                    <script src="https://cdn.tailwindcss.com"></script></head>
                <body>
                    <div>
                        <a href="index.html">Home</a>
                        <a href="Test.html">Test</a>
                    </div>
                    <Searchpage></Searchpage>
                </body>
                </html>
        """)
    with open("./src/Searchbar.html","w") as f:
        f.write("""
            <input type="text" placeholder=$placeholder ></input>
        """)
    with open("./src/Button.html","w") as f:
        f.write("""
            <button onclick=$onclick class="bg-blue-500 px-4 py-2 rounded-md shadow-lg" >$child</button>
        """)
    with open("./src/Searchpage.html","w") as f:
        f.write("""
       <div class="flex w-screen h-screen bg-blue-200 flex-col items-center gap-2 justify-center" >
            <h>Sök</h>
            <Searchbar placeholder="Har" ></Searchbar> 
            <Button onclick=alert(10) >Search</Button>
        </div>
       """)
    with open("./src/Test.html","w") as f:
        f.write("""
{
asd = ""
for i in range(10):
    asd += f"<h1>Hello this is a test page {i}</h1>"


}

        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
            <script src="https://cdn.tailwindcss.com"></script></head>
        <body>
            <div>
                <a href="index.html">Home</a>
                <a href="Test.html">Test</a>
            </div>
            {asd}
        </body>
        </html>
        """)

settings_manager = FlagManager([
    Flag("-p", "--path", "sets the src path from", setPath),
    Flag("-o", "--out-path", "sets the out path", setOutPath),
]);

manager = FlagManager([
    Flag("-c", "--compile", "compile a file or all with all keyword (-c all)", compileAll),
    Flag("start", "--start", "auto compiles", start),
    Flag("generate-example", "generate-example", "creates a exmaple", generateExample),
    
])
settings_manager.description = """Webers is a compiling tool that lets you use components inside html. With the use of PyTml we can script with python
inside the components aswell. To get a example run `webers generate-example`""" 
settings_manager.check()
manager.check()

import os
