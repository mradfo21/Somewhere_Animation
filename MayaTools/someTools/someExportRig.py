import re
import os, sys
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)
import someCommons; reload(someCommons)

class gui():
    def setup(self):
        width, height, spacer = 500, 241, 2

        cmds.columnLayout('Rig Export', adj=True, p='sme_tabMain')

        cmds.separator(h=1, st='none')

        cmds.rowColumnLayout(nc=4,
                             cs=[ (1, spacer), (2, spacer), (3, spacer), (4, spacer) ],
                             cw=[ (1, 90), (2, 235), (3, 20), (4, 120) ])

        cmds.text('sme_rigFilename_label', al='right', l='Rig Filename', ann='Name of Rig Data to be written to disk.')
        cmds.textField('sme_rigFilename',
                       aie=1,
                       cc=lambda *args: self.check(),
                       ec=lambda *args: self.check(),
                       tx=someGlobals.rig['filename'],
                       ann='Name of Rig Data to be written to disk.'
                       )
        cmds.text('sme_rigFilenameExt', al='left', l='.fbx')
        cmds.text('sme_rigDataExists_label', al='left', l=' - Data Exists!')

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='in'); cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=2,
                             cs=[ (1, spacer), (2, spacer) ],
                             cw=[ (1, 50), (2, width-114) ])

        cmds.text('sme_rigName_label', al='right', l='Name', ann='This is the unique name that will be assigned to your Baked Rig.')
        cmds.textField('sme_rigName',
                       aie=1,
                       cc=lambda *args: self.updateName('sme_rigName'),
                       ec=lambda *args: self.updateName('sme_rigName'),
                       tx=someGlobals.rig['name'],
                       ann='This is the unique name that will be assigned to your Baked Rig.'
                       )

        cmds.setParent('..')

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=3,
                             cs=[ (1, spacer), (2, spacer), (3, spacer) ],
                             cw=[ (1, 50), (2, width-114), (3, 50) ])

        cmds.button('sme_selectRigToExport_button', l='Rig', ann='Click this button to select the current Export Rig that is assigned.')
        cmds.textField('sme_rigToSample',
                       aie=1,
                       cc=lambda *args: self.check(),
                       ec=lambda *args: self.check(),
                       #tx='|Soldier_Rig_MASTER:Explorer_Model|Soldier_Rig_MASTER:Rig|Soldier_Rig_MASTER:Group|Soldier_Rig_MASTER:Main|Soldier_Rig_MASTER:DeformationSystem|Soldier_Rig_MASTER:Root_M',
                       ann='This is the unique name that will be assigned to your Baked Rig.'
                       )
        cmds.button('sme_assignRigData_button', l='Assign', c=lambda *args: self.assign('sme_rigToSample'), ann='Assign a new selected export rig for baking and export.')

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='out'); cmds.separator(h=2, st='none')

        cmds.button('sme_rigBake_button', l='Bake and Export Rig')

        cmds.setParent('..') # Rig Export layout

    def check(self):
        cmds.text('sme_startFrame_label', e=True, en=1)
        cmds.floatField('sme_startFrame', e=True, en=1)
        cmds.text('sme_endFrame_label', e=True, en=1)
        cmds.floatField('sme_endFrame', e=True, en=1)
        cmds.text('sme_totalFrames_label', e=True, en=1, l='Total Frames: ' + str(someGlobals.globals['startFrame'] + someGlobals.globals['endFrame']))
        cmds.optionMenu('sme_frameRate', e=True, en=1)

        filename = re.sub('[^\w\-_\. ]', '', cmds.textField('sme_rigFilename', q=True, tx=True)).replace(' ', '')
        cmds.textField('sme_rigFilename', e=True, tx=filename)

        dataExists = ''
        if os.path.isfile(someGlobals.globals['exportPath'] + filename + '.fbx'):
            dataExists = ' - Data Exists!'

        cmds.text('sme_rigDataExists_label', e=True, l=dataExists)

        name = re.sub('[^\w\-_\.\ ]', '', cmds.textField('sme_rigName', q=True, tx=True)).replace(' ', '')
        cmds.textField('sme_rigName', e=True, tx=name)

        rig = cmds.textField('sme_rigToSample', q=True, tx=True).replace(' ', '')
        cmds.textField('sme_rigToSample', e=True, tx=rig)

        selectEnable = 0
        selectCommand = lambda *args: cmds.select(rig, r=True)
        selectColor = someGlobals.color['red']
        if cmds.objExists(rig):
            selectEnable = 1
            selectCommand = lambda *args: cmds.select(rig, r=True)
            selectColor = someGlobals.color['blue']

        bakeEnable = 1
        bakeColor = someGlobals.color['green']
        bakeLabel = 'Bake and Export Rig'
        bakeCommand = lambda *args: self.batch()
        if len(filename) < 1 or len(name) < 1 or cmds.objExists(rig) == False:
            bakeEnable = 0
            bakeColor = someGlobals.color['red']
            bakeLabel = 'Errors Found in Rig Export Parameters'
            bakeCommand = ''

        if (os.path.exists(someGlobals.globals['exportPath']) == False):
            bakeEnable = 0
            bakeColor = someGlobals.color['red']
            bakeCommand = ''
            bakeLabel = 'Invalid Export Path'

        # lets update our globals
        rigFilename = { 'filename': filename }
        rigName = { 'name': name }
        rigNode = { 'node': rig }
        someGlobals.rig.update(rigFilename)
        someGlobals.rig.update(rigName)
        someGlobals.rig.update(rigNode)

        cmds.button('sme_selectRigToExport_button', e=True, en=selectEnable, bgc=selectColor, c=selectCommand)
        cmds.button('sme_rigBake_button', e=True, en=bakeEnable, bgc=bakeColor, l=bakeLabel, c=bakeCommand)

    def assign(self, field):
        sel = cmds.ls(sl=True, fl=True, l=True)
        assign = [ cmds.textField(field, q=True, tx=True) ]

        if sel != None and len(sel) > 0:
            parents = cmds.listRelatives(sel[0], ap=True, type='transform')
            children = cmds.listRelatives(sel[0], ad=True, type='transform')

            hierarchy = []
            if parents != None and children != None:
                hierarchy = parents + children
            elif parents != None and children == None:
                hierarchy = parents
            elif parents == None and children != None:
                hierarchy = children

            for item in hierarchy:
                if someGlobals.rig['default'] in item and cmds.nodeType(item) == 'transform':
                    child = cmds.listRelatives(item, c=True, type='joint')

                    if child != None and someGlobals.rig['rootDefault'] in child[0]:
                        fullPath = cmds.ls(child[0], l=True)[0]
                        assign.append(fullPath)
                        break

            if len(assign) > 1 and assign[0] != assign[1]:
                tok1 = assign[1].split('|')

                filename = someGlobals.globals['scene'] + '_Rig_'
                foundName = cmds.textField('sme_rigName', q=True, tx=True)
                if tok1 != None:
                    tok2 = tok1[1].split(':')

                    if tok2 != None:
                        try:
                            foundName = tok2[1]
                        except:
                            foundName = ""

                filename = filename + foundName
                cmds.textField('sme_rigName', e=True, tx=foundName)
                cmds.textField('sme_rigFilename', e=True, tx=filename)
                cmds.textField(field, e=True, tx=assign[1])

                rigFilename = { 'filename': filename }
                rigName = { 'name': foundName }
                someGlobals.rig.update(rigFilename)
                someGlobals.rig.update(rigName)
            elif len(assign) > 1 and assign[0] == assign[1]:
                someCommons.sprint('This rig is already assigned.')
            else:
                someCommons.sprint('No valid rig found within the hierarchy of ' + sel[0])

        else:
            someCommons.sprint('Please select a valid joint or joint under the hierarchy that contains ' + someGlobals.rig['default'] + ' ...')

        self.check()

    def updateName(self, fieldName):
        name = cmds.textField(fieldName, q=True, tx=True)
        filename = someGlobals.globals['scene'] + '_Rig_' + name

        cmds.textField('sme_rigFilename', e=True, tx=filename)

        rigFilename = { 'filename': filename }
        rigName = { 'name': name }
        someGlobals.rig.update(rigFilename)
        someGlobals.rig.update(rigName)

        self.check()

    def buildSkeleton(self, sampleRig):
        name = someGlobals.rig['name']
        sampleRigBones = cmds.listRelatives(sampleRig, f=True)

        tok = sampleRig.split(':')
        rootJoint = name + '_' + tok[len(tok)-1]
        # made this change so it'll just export bone names as is, remove this line to use the name field
        name = ""
        rootJoint = tok[len(tok)-1]

        if cmds.objExists(rootJoint) == False:
            cmds.select(cl=True)
            rootJoint = cmds.joint(n=rootJoint)
            cmds.parentConstraint(sampleRig, rootJoint, w=1)
            cmds.scaleConstraint(sampleRig, rootJoint, w=1)

        if sampleRigBones != None:
            for bone in sampleRigBones:
                cmds.select(cl=True)

                tok = bone.split(':')
                childJoint = name + tok[len(tok)-1]

                if cmds.objExists(childJoint) == False:
                    childJoint = cmds.joint(n=childJoint)
                    cmds.parent(childJoint, rootJoint)

                cmds.parentConstraint(bone, childJoint, w=1, mo=0)
                cmds.scaleConstraint(bone, childJoint, w=1, mo=0)

                boneChildren = cmds.listRelatives(bone, f=True)

                if boneChildren != None:
                    self.recurseRig(name, childJoint, boneChildren)

        return rootJoint

    def recurseRig(self, name, parentJoint, children):
        for bone in children:
            cmds.select(cl=True)

            tok = bone.split(':')
            childJoint = name + tok[len(tok)-1]

            if cmds.objExists(childJoint) == False:
                childJoint = cmds.joint(n=childJoint)
                cmds.parent(childJoint, parentJoint)

            cmds.parentConstraint(bone, childJoint, w=1, mo=0)
            cmds.scaleConstraint(bone, childJoint, w=1, mo=0)

            boneChildren = cmds.listRelatives(bone, f=True)

            if boneChildren != None:
                self.recurseRig(name, childJoint, boneChildren)

    def bake(self, rootJoint):
        cmds.bakeResults(rootJoint,
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

        hierarchy = cmds.listRelatives(rootJoint, ad=True)

        if hierarchy != None:
            for node in hierarchy:
                ## FEATURE REQUEST: filter out if something is a group, then reparent the joints to the joint above and remove the group
                if cmds.nodeType(node) == 'parentConstraint' or cmds.nodeType(node) == 'scaleConstraint':
                    cmds.delete(node)

    def export(self, obj):
        import FBXWrapper as fbx
        import pymel.core as pm

        file = someGlobals.globals['exportPath'] + someGlobals.rig['filename'] + '.fbx'
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
            fbx.FBXProperty('Export|IncludeGrp|CameraGrp|Camera -v false')
            fbx.FBXProperty('Export|AdvOptGrp|Collada|FrameRate -v ' + someGlobals.globals['fps'][0])
            fbx.FBXProperty('Export|AdvOptGrp|Fbx|AsciiFbx -v "ASCII"')

            pm.FBXExport("-f", file, "-s")

    def batch(self):
        rootJoint = self.buildSkeleton(someGlobals.rig['node'])

        if cmds.objExists(rootJoint):
            self.bake(rootJoint)
            self.export(rootJoint)

        else:
            someCommons.sprint('Skeleton failed to be built.')

        self.check()