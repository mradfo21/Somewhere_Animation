import re
import os, sys
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)
import someCommons; reload(someCommons)

class gui():
    def setup(self):
        width, height, spacer = 500, 241, 2

        cmds.columnLayout('Mesh Export', adj=True, p='sme_tabMain')

        cmds.separator(h=1, st='none')

        cmds.rowColumnLayout(nc=4,
                             cs=[ (1, spacer), (2, spacer), (3, spacer), (4, spacer) ],
                             cw=[ (1, 90), (2, 235), (3, 20), (4, 120) ])

        cmds.text('sme_meshFilename_label', al='right', l='Mesh Filename', ann='Name of Mesh Data to be written to disk.')
        cmds.textField('sme_meshFilename',
                       aie=True,
                       cc=lambda *args: self.check(),
                       ec=lambda *args: self.check(),
                       tx=someGlobals.mesh['filename'],
                       ann='Name of Mesh Data to be written to disk.'
                       )
        cmds.text('sme_meshFilenameExt', al='left', l='.fbx')
        cmds.text('sme_meshDataExists_label', al='left', l=' - Data Exists!')

        cmds.setParent('..')

        cmds.rowColumnLayout(nc=1,
                             cs=[ (1, 95) ],
                             cw=[ (1, 160) ])

        cmds.checkBox('sme_linkSelection', l='Link List Selection to World', v=True, cc=lambda *args: self.check(), ann='Selected objects in the Mesh List will be selected in the world.')

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='in'); cmds.separator(h=2, st='none')

        cmds.formLayout('sme_meshExport_form', numberOfDivisions=100)

        cmds.frameLayout('sme_meshExport_frameLayout', w=width-8, h=height, l='Objects: 0')

        cmds.textScrollList('sme_meshExportObjects',
                            ann='Master object list to export from Maya. Double click an item to load the Attribute Editor for it.',
                            ams=True,
                            sc=lambda *args: self.check(),
                            dcc=lambda *args: self.check(),
                            hlc=someGlobals.color['highlight'],
                            nr=10
                            )

        cmds.setParent('..') # objects frame layout

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout('sme_meshExport_buttonLayout', nc=3,
                             cs=[ (1, spacer), (2, spacer), (3, spacer) ],
                             cw=[ (1, (width/3)-5), (2, (width/3)-5), (3, (width/3)-5) ])

        cmds.button('sme_meshExport_addButton', l='Add Meshes', c=lambda *args: self.add('sme_meshExportObjects'))
        cmds.button('sme_meshExport_removeButton', l='Remove Selected', c=lambda *args: self.remove('sme_meshExportObjects'))
        cmds.button('sme_meshExport_clearButton', l='Clear List', c=lambda *args: self.clear('sme_meshExportObjects'))

        cmds.setParent('..')

        cmds.setParent('..') # Mesh Export Form layout

        cmds.separator(h=2, st='none')

        cmds.button('sme_meshExport_shapesButton', l='Clean Meshes', c=lambda *args: self.check())

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='out'); cmds.separator(h=2, st='none')

        cmds.button('sme_meshExport_button', l='Export Objects')

        cmds.setParent('..') # Mesh Export Layout

        cmds.formLayout('sme_meshExport_form', e=True,
                        af=[ ('sme_meshExport_frameLayout', 'top', spacer), ('sme_meshExport_frameLayout', 'left', spacer), ('sme_meshExport_buttonLayout', 'left', spacer) ],
                        ac=[ ('sme_meshExport_buttonLayout', 'top', spacer, 'sme_meshExport_frameLayout') ]
                        )

    def check(self):
        cmds.text('sme_startFrame_label', e=True, en=0)
        cmds.floatField('sme_startFrame', e=True, en=0)
        cmds.text('sme_endFrame_label', e=True, en=0)
        cmds.floatField('sme_endFrame', e=True, en=0)
        cmds.text('sme_totalFrames_label', e=True, en=0, l='Total Frames: ' + str(someGlobals.globals['startFrame'] + someGlobals.globals['endFrame']))
        cmds.optionMenu('sme_frameRate', e=True, en=0)

        filename = re.sub('[^\w\-_\. ]', '', cmds.textField('sme_meshFilename', q=True, tx=True)).replace(' ', '')
        cmds.textField('sme_meshFilename', e=True, tx=filename)

        dataExists = ''
        if os.path.isfile(someGlobals.globals['exportPath'] + filename + '.fbx'):
            dataExists = ' - Data Exists!'

        cmds.text('sme_meshDataExists_label', e=True, l=dataExists)

        shapes = []

        objects = cmds.textScrollList('sme_meshExportObjects', q=True, ai=True)
        selected = cmds.textScrollList('sme_meshExportObjects', q=True, si=True)
        maxObjects = cmds.textScrollList('sme_meshExportObjects', q=True, ni=True)
        maxSelected = cmds.textScrollList('sme_meshExportObjects', q=True, nsi=True)

        clearEnable = 0
        clearColor = (0.4, 0.4, 0.4)
        clearLabel = 'Clear List'
        clearCommand = ''

        exportEnable = 1
        exportColor = someGlobals.color['green']
        exportLabel = 'Export Objects as FBX'
        exportCommand = lambda *args: self.export('sme_meshExportObjects')
        if maxObjects > 0:
            shapes = self.getAllShapes(objects)
            clearEnable = 1
            clearColor = someGlobals.color['blue']
            clearCommand = lambda *args: self.clear('sme_meshExportObjects')
        elif maxObjects < 1:
            exportEnable = 0
            exportColor = someGlobals.color['red']
            clearColor = someGlobals.color['red']
            removeColor = someGlobals.color['red']
            removeLabel = 'No Objects Found'
            clearLabel = 'No Objects Found'
            exportLabel = 'Object List is Empty'
            deleteShapesLabel = 'Object List is Empty'
            exportCommand = ''

        removeEnable = 0
        removeColor = (0.4, 0.4, 0.4)
        removeLabel = 'Remove Selected'
        removeCommand = ''
        if maxSelected > 0:
            if cmds.checkBox('sme_linkSelection', q=True, v=True) == True:
                cmds.select(selected, r=True)

            removeEnable = 1
            removeColor = someGlobals.color['blue']
            removeCommand = lambda *args: self.remove('sme_meshExportObjects')

        deleteShapesEnable = False
        deleteShapesLabel = 'Everything Looks Good!'
        deleteShapesColor = [ 0.45, 0.45, 0.45]
        deleteShapesCommand = ''
        if len(shapes) > 0:
            deleteShapesLabel = 'Clean Meshes'
            deleteShapesEnable = True
            deleteShapesColor = someGlobals.color['blue']
            deleteShapesCommand = lambda *args: self.deleteShapeDupes(shapes)

        if maxObjects < 1:
            deleteShapesLabel = 'Object List is Empty'

        if len(filename) < 1:
            exportEnable = 0
            exportColor = someGlobals.color['red']
            exportLabel = 'Mesh Export Filename is Invalid'
            exportCommand = ''

        if (os.path.exists(someGlobals.globals['exportPath']) == False):
            exportEnable = 0
            exportColor = someGlobals.color['red']
            exportLabel = 'Invalid Export Path'

        cmds.frameLayout('sme_meshExport_frameLayout', e=True, l='Export Objects [ ' + str(maxObjects) + ':' + str(maxSelected) + ' ]')
        cmds.button('sme_meshExport_removeButton', e=True, en=removeEnable, bgc=removeColor, l=removeLabel, c=removeCommand)
        cmds.button('sme_meshExport_clearButton', e=True, en=clearEnable, bgc=clearColor, l=clearLabel, c=clearCommand)

        cmds.button('sme_meshExport_shapesButton', e=True, en=deleteShapesEnable, bgc=deleteShapesColor, l=deleteShapesLabel, c=deleteShapesCommand)
        cmds.button('sme_meshExport_button', e=True, en=exportEnable, bgc=exportColor, l=exportLabel, c=exportCommand)

        # lets update our globals
        meshFilename = { 'filename': filename }
        someGlobals.rig.update(meshFilename)

    def add(self, listName):
        #worldSelection = someCommons.getTypeFromList(cmds.ls(sl=True, fl=True, l=True), 'mesh')
        worldSelection = cmds.ls(sl=True, ap=True, dag=True)
        listSelection = cmds.textScrollList(listName, q=True, si=True)
        listObjects = cmds.textScrollList(listName, q=True, ai=True)

        if worldSelection == None or len(worldSelection) < 1:
            someCommons.sprint('No Polygon Mesh Objects selected!')
        else:
            polys = self.getPolygons(worldSelection)

            if len(polys) > 0:
                for items in polys:
                    if listObjects != None:
                        if items not in listObjects:
                            cmds.textScrollList(listName, e=True, a=items)
                    else:
                        cmds.textScrollList(listName, e=True, a=items)

        self.check()

    def getPolygons(self, objects):
        output = []

        children = cmds.listRelatives(objects, ad=True, f=True)
        parents = cmds.listRelatives(children, ap=True, f=True)

        if children == None:
            children = []

        if parents == None:
            parents = []

        everything = parents + children

        if len(everything) > 0:
            for node in everything:
                shape, type, parent = someCommons.shapeTypeParent(node)

                if type == 'mesh' and parent not in output:
                    output.append(parent)

        return output

    def getAllShapes(self, objects):
        badShapes = []

        for node in objects:
            sniff = cmds.listRelatives(node, s=True, f=True)

            if sniff != None:
                for shape in sniff:
                    if cmds.getAttr(shape + '.intermediateObject'):
                        badShapes.append(shape)

        return badShapes

    def deleteShapeDupes(self, shapes):
        cmds.progressBar('sme_progressBar', e=True, max=len(shapes), bp=True)

        for shape in shapes:
            if cmds.objExists(shape):
                cmds.delete(shape)

            cmds.progressBar('sme_progressBar', e=True, s=1)

        cmds.progressBar('sme_progressBar', e=True, ep=True)

        self.check()

    def remove(self, listName):
        listSelection = cmds.textScrollList(listName, q=True, si=True)

        if listSelection != None:
            cmds.textScrollList(listName, e=True, ri=listSelection)

        self.check()

    def clear(self, listName):
        cmds.textScrollList(listName, e=True, ra=True)

        self.check()

    def exportValidate(self, objects):
        output = []

        for item in objects:
            if cmds.objExists(item):
                output.append(item)

        return output

    def export(self, listName):
        objects = cmds.textScrollList(listName, q=True, ai=True)

        if objects != None:
            validateObjects = self.exportValidate(objects)

            if validateObjects != None:
                import FBXWrapper as fbx
                import pymel.core as pm

                file = someGlobals.globals['exportPath'] + someGlobals.mesh['filename'] + '.fbx'
                confirm = 'Yes'

                if (os.path.isfile(file)):
                    confirm = cmds.confirmDialog(
                                                 title='Data Exists on Disk',
                                                 message='Overwrite existing data on disk?',
                                                 button=['Yes','No'],
                                                 defaultButton='Yes',
                                                 cancelButton='No',
                                                 dismissString='No'
                                                )

                if confirm == 'Yes':
                    cmds.select(validateObjects, r=True)

                    fbx.FBXProperty('Export|IncludeGrp|Geometry|SmoothingGroups" -v true')
                    fbx.FBXProperty('Export|IncludeGrp|Geometry|expHardEdges" -v false')
                    fbx.FBXProperty('Export|IncludeGrp|Geometry|TangentsandBinormals" -v true')
                    fbx.FBXProperty('Export|IncludeGrp|Geometry|SmoothMesh" -v true')
                    fbx.FBXProperty('Export|IncludeGrp|Animation" -v false')
                    fbx.FBXProperty('Export|IncludeGrp|CameraGrp|Camera" -v false')
                    fbx.FBXProperty('Export|AdvOptGrp|Fbx|AsciiFbx" -v "ASCII"')

                    pm.FBXExport("-f", file, "-s")
            else:
                someCommons.sprint('No valid mesh objects to export.')
        else:
            someCommons.sprint('Nothing to export.')

        self.check()
