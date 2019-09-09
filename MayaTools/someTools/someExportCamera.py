import re
import os, sys
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)
import someCommons; reload(someCommons)

class gui():
    def setup(self):
        width, height, spacer = 500, 241, 2

        cmds.columnLayout('Camera Export', adj=True, p='sme_tabMain')

        cmds.separator(h=1, st='none')

        cmds.rowColumnLayout(nc=4,
                             cs=[ (1, spacer), (2, spacer), (3, spacer), (4, spacer) ],
                             cw=[ (1, 90), (2, 235), (3, 20), (4, 120) ])

        cmds.text('sme_cameraFilename_label', al='right', l='Camera Filename', ann='Name of Camera Data to be written to disk.')
        cmds.textField('sme_cameraFilename',
                       aie=1,
                       cc=lambda *args: self.check(),
                       ec=lambda *args: self.check(),
                       tx=someGlobals.camera['filename'],
                       ann='Name of Camera Data to be written to disk.'
                       )
        cmds.text('sme_cameraFilenameExt', al='left', l='.fbx')
        cmds.text('sme_cameraDataExists_label', al='left', l=' - Data Exists!')

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='in'); cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=2,
                             cs=[ (1, spacer), (2, spacer) ],
                             cw=[ (1, 50), (2, width-114) ])

        cmds.text('sme_cameraName_label', al='right', l='Name', ann='This is the unique name that will be assigned to your Baked Camera.')
        cmds.textField('sme_cameraName',
                       aie=1,
                       cc=lambda *args: self.updateName('sme_cameraName'),
                       ec=lambda *args: self.updateName('sme_cameraName'),
                       tx=someGlobals.camera['name'],
                       ann='This is the unique name that will be assigned to your Baked Camera.'
                       )

        cmds.setParent('..')

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=3,
                             cs=[ (1, spacer), (2, spacer), (3, spacer) ],
                             cw=[ (1, 50), (2, width-114), (3, 50) ])

        cmds.button('sme_selectCameraToExport_button', l='Camera', ann='Click this button to select the current Export Camera that is assigned.')
        cmds.textField('sme_cameraToSample',
                       aie=1,
                       cc=lambda *args: self.check(),
                       ec=lambda *args: self.check(),
                       ann='This is the unique name that will be assigned to your Baked Camera.'
                       )
        cmds.button('sme_assignCameraData_button', l='Assign', c=lambda *args: self.assign('sme_cameraToSample'), ann='Assign a new selected export camera for baking and export.')

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='out'); cmds.separator(h=2, st='none')

        cmds.button('sme_cameraBake_button', l='Bake and Export Camera')

        cmds.setParent('..') # Camera Export layout

        defaultCamera = cmds.ls(someGlobals.camera['default'], l=True)
        if defaultCamera != None and len(defaultCamera) > 0:
            cmds.textField('sme_cameraToSample', e=True, tx=defaultCamera[0])
        else:
            someCommons.sprint(someGlobals.camera['default'] + ' was not found in the scene. Please manually assign a Camera.')

        self.check()

    def check(self):
        cmds.text('sme_startFrame_label', e=True, en=1)
        cmds.floatField('sme_startFrame', e=True, en=1)
        cmds.text('sme_endFrame_label', e=True, en=1)
        cmds.floatField('sme_endFrame', e=True, en=1)
        cmds.text('sme_totalFrames_label', e=True, en=1, l='Total Frames: ' + str(someGlobals.globals['startFrame'] + someGlobals.globals['endFrame']))
        cmds.optionMenu('sme_frameRate', e=True, en=1)

        filename = re.sub('[^\w\-_\. ]', '', cmds.textField('sme_cameraFilename', q=True, tx=True)).replace(' ', '')
        cmds.textField('sme_cameraFilename', e=True, tx=filename)

        dataExists = ''
        if os.path.isfile(someGlobals.globals['exportPath'] + filename + '.fbx'):
            dataExists = ' - Data Exists!'

        cmds.text('sme_cameraDataExists_label', e=True, l=dataExists)

        name = re.sub('[^\w\-_\. ]', '', cmds.textField('sme_cameraName', q=True, tx=True)).replace(' ', '')
        cmds.textField('sme_cameraName', e=True, tx=name)

        camera = cmds.textField('sme_cameraToSample', q=True, tx=True).replace(' ', '')
        cmds.textField('sme_cameraToSample', e=True, tx=camera)

        selectEnable = 0
        selectCommand = lambda *args: cmds.select(camera, r=True)
        selectColor = someGlobals.color['red']
        if cmds.objExists(camera):
            selectEnable = 1
            selectCommand = lambda *args: cmds.select(camera, r=True)
            selectColor = someGlobals.color['blue']

        bakeEnable = 1
        bakeColor = someGlobals.color['green']
        bakeLabel = 'Bake and Export Camera'
        bakeCommand = lambda *args: self.batch()
        if len(filename) < 1 or len(name) < 1 or cmds.objExists(camera) == False:
            bakeEnable = 0
            bakeColor = someGlobals.color['red']
            bakeLabel = 'Errors Found in Camera Export Parameters'
            bakeCommand = ''

        if (os.path.exists(someGlobals.globals['exportPath']) == False):
            bakeEnable = 0
            bakeColor = someGlobals.color['red']
            bakeCommand = ''
            bakeLabel = 'Invalid Export Path'

        # lets update our globals
        cameraFilename = { 'filename': filename }
        cameraName = { 'name': name }
        cameraNode = { 'node': camera }
        someGlobals.camera.update(cameraFilename)
        someGlobals.camera.update(cameraName)
        someGlobals.camera.update(cameraNode)

        cmds.button('sme_selectCameraToExport_button', e=True, en=selectEnable, bgc=selectColor, c=selectCommand)
        cmds.button('sme_cameraBake_button', e=True, en=bakeEnable, bgc=bakeColor, l=bakeLabel, c=bakeCommand)

    def assign(self, field):
        sel = someCommons.getTypeFromList(cmds.ls(sl=True, fl=True, l=True), 'camera')

        if len(sel) > 0 and cmds.objExists(sel[0]):
            cmds.textField(field, e=True, tx=sel[0])

        self.check()

    def updateName(self, fieldName):
        name = cmds.textField(fieldName, q=True, tx=True)
        cameraName = { 'name': name }
        someGlobals.camera.update(cameraName)

        self.check()

    def bake(self):
        cameraName = someGlobals.camera['name']
        cameraSample = someGlobals.camera['node']

        if cmds.objExists(cameraName):
            cmds.delete(cameraName)

        # duplicate our camera to be sampled, parent it to the world
        cameraBake = cmds.duplicate(cameraSample, rr=True, ic=True, n=cameraName)[0]
        cmds.parent(cameraBake, w=True)
        cameraBake = cmds.ls(cameraBake, l=True)[0]

        relatives = cmds.listRelatives(cameraBake, f=True)

        if relatives != None and len(relatives):
            for node in relatives:
                if (cmds.nodeType(node) != 'camera'):
                    cmds.delete(node)

        parentConstraint = cmds.parentConstraint(cameraSample, cameraBake, mo=True, weight=1)[0]
        scaleConstraint = cmds.scaleConstraint(cameraSample, cameraBake, mo=True, weight=1)[0]

        cmds.bakeResults(cameraBake,
                        simulation=True,
                        t=(someGlobals.globals['startFrame'], someGlobals.globals['endFrame']),
                        hierarchy='below',
                        sampleBy=1.0,
                        oversamplingRate=1,
                        disableImplicitControl=True,
                        preserveOutsideKeys=False,
                        sparseAnimCurveBake=False,
                        removeBakedAttributeFromLayer=False,
                        removeBakedAnimFromLayer=False,
                        bakeOnOverrideLayer=False,
                        minimizeRotation=True,
                        controlPoints=False,
                        shape=True
                        )

        cmds.delete(parentConstraint, scaleConstraint)

        return cameraBake

    def export(self, obj):
        import FBXWrapper as fbx
        import pymel.core as pm

        file = someGlobals.globals['exportPath'] + someGlobals.camera['filename'] + '.fbx'
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
            cmds.select(obj, r=True)

            fbx.FBXProperty('Export|IncludeGrp|Animation -v true')
            fbx.FBXProperty('Export|IncludeGrp|CameraGrp|Camera -v true')
            fbx.FBXProperty('Export|AdvOptGrp|Collada|FrameRate -v ' + someGlobals.globals['fps'][0])
            fbx.FBXProperty('Export|AdvOptGrp|Fbx|AsciiFbx -v "ASCII"')

            pm.FBXExport("-f", file, "-s")

    def batch(self):
        if cmds.objExists(someGlobals.camera['node']):
            camera = self.bake()

            if cmds.objExists(camera):
                self.export(camera)
            else:
                someCommons.sprint(camera + ' could not found. Something went wrong with the Baking?')
        else:
            someCommons.sprint('The assigned Camera is missing. Cannot bake and export.')

        self.check()
