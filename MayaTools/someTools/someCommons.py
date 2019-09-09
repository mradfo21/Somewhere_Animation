import os, sys
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)

def pathConvert(path):
    path = os.path.abspath(path)
    return os.path.join(path, '')

def sprint(value):
    sys.stdout.write(value + '\n')

# parent should always return the object you're passing, the reason for this is
# we want the shape node parent which we should assume is the object but this is
# not always the case. Some objects do not have shape nodes, ex.. Joints
# therefore we need to handle things a bit differently for consistency
def shapeTypeParent(object):
    shape = None
    type = None
    parent = None

    if cmds.nodeType(object) == 'transform':
        parent = object
        type = 'transform'
        getShape = cmds.listRelatives(object, ad=True, f=True, s=True)

        if getShape != None:
            type = cmds.nodeType(getShape[0])
    else:
        type = cmds.nodeType(object)
        objectParent = cmds.listRelatives(object, ad=True, f=True, p=True)

        if objectParent == None:
            parent = object
        elif objectParent != None:# and objectParent[0] != object:
            getShape = cmds.listRelatives(objectParent[0], ad=True, f=True, s=True)

            if getShape != None:
                parent = objectParent[0]
            else:
                parent = object

    return shape, type, parent

# take a list of objects and return only the objects of a specific type
# this will also filter out the potential for component selection
def getTypeFromList(objects, objectType):
    output = []

    for i in range(0,len(objects)):
        shape, type, parent = shapeTypeParent(objects[i])

        if type == objectType:
            object = parent.split('.')

            try:
                output.index(object[0])
            except ValueError:
                output.append(object[0])
                pass

    return output

def sniffTransform(mode, needle, haystack):
    export = ''

    for object in haystack:
        shape, type, parent = shapeTypeParent(object)

        if mode == 'matchType' and type == needle:
            export = object
            break
        elif mode == 'matchName' and needle in object:
            export = object
        elif mode == 'matchRig' and needle in object and cmds.nodeType(object) == 'transform':
            rels = cmds.listRelatives(object, c=True)

            if rels != None and cmds.nodeType(rels[0]) == 'joint':
                export = rels[0]
                break

    return export
