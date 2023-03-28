from flagser import *
import os

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
def componentsInHtml(path):
    with open(path, "r") as f:
        components = []
        listenForCompName = False
        compName = ""
        comp = ""
        
        while True:
            c = f.read(1)
            if not c:
                break
            
            if(c == "<") :
                listenForCompName = True
                comp += c
                continue
            
            if(c == ">" or c == "/") :
                comp += "/>"
                splittet = compName.split(" ")
                components.append({"name":splittet[0], "props": getProps(compName), "component":compName})
                comp = ""
                listenForCompName = False
                compName = ""

            if listenForCompName:
                comp += c
                compName += c

        return components

def getComponent(path, component) -> str:
    file = ""
    with open(path, "r") as f:
        file = f.read()
    
    for prop in component["props"]:
        file = file.replace("$"+prop,component["props"][prop].replace('"',""))
    return file


def replaceComponent(path, components):
    file = ""
    with open(path, "r") as f:
        file = f.read()

    for component in components:
        #print("<"+component["component"]+"><"+component["name"]+"/>")
        file = file.replace("<"+component["component"]+"></"+component["name"]+">", component["file"]) 
        file = file.replace("<"+component["component"]+"/>", component["file"]) 

        
    print(file)

manager = FlagManager([
    
])
def getFiles():
    f = []
    for path, subdirs, files in os.walk("./"):
        for name in files:
            if name.split(".")[1] == "html":
                f.append(os.path.join(path,name))
    return f

# component = manager.args[1]
# page = manager.args[2]
# components = []
# for comp in componentsInHtml(page):
#     #print(componentsInHtml(page)[comp])
#     if "Navbar" in comp["name"]:
#         comp["file"] = (getComponent(component, comp))
#         #print(comp["component"])
#         components.append(comp)

# replaceComponent(page, components)