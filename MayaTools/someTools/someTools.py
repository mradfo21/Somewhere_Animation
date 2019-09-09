import os, sys
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)
import someCommons; reload(someCommons)
import someDataExplorer; reload(someDataExplorer)
import someExportCamera; reload(someExportCamera)
import someExportRig; reload(someExportRig)
import someExportMesh; reload(someExportMesh)

class gui():
    def setup(self):
        fps = cmds.currentUnit(q=True, t=True)

        if (fps == 'game'):
            fps =  1
        elif (fps == 'film'):
            fps = 2
        elif (fps == 'pal'):
            fps = 3
        elif (fps == 'ntsc'):
            fps = 4
        elif (fps == 'show'):
            fps = 5
        elif (fps == 'palf'):
            fps = 6
        elif (fps == 'ntscf'):
            fps = 7

        width, height, spacer = 500, 241, 2

        cmds.window(someGlobals.globals['gui'],
               title='Somewhere Tools v' + str(someGlobals.globals['version']) + ' - [ ' + someGlobals.globals['scene'] + ' ]',
               maximizeButton=False,
               minimizeButton=False,
               sizeable=False,
               resizeToFitChildren=True,
               menuBar=False,
               menuBarVisible=False,
               w=width,
               h=height
               )

        cmds.columnLayout('sme_main_columnLayout', adj=True)

        cmds.separator(h=2, st='none')

        cmds.textField('sme_exportPath',
                        aie=1,
                        tx=someCommons.pathConvert(someGlobals.globals['exportPath']),
                        cc=lambda *args: self.exportPath('sme_exportPath'),
                        ec=lambda *args: self.exportPath('sme_exportPath'),
                        ann='The root export path where your data will be written to.'
                        )

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=2,
                             cs=[ (1, spacer), (2, spacer) ],
                             cw=[ (1, (width/2)-5), (2, (width/2)-5) ]
                            )

        cmds.button('sme_exploreLocation_button',
                    l='Explore Location',
                    c=lambda *args: self.exploreLocation(someCommons.pathConvert(cmds.textField('sme_exportPath', q=True, tx=True))),
                    ann='If the export path is a valid directory (lit green) you can click this button to open a Windows Explorer window at this location.'
                    )

        cmds.button('sme_exportPathBrowse_button',
                    l='Browse',
                    c=lambda *args: self.browsePath('sme_exportPath', someCommons.pathConvert(cmds.textField('sme_exportPath', q=True, tx=True))),
                    ann='Browse to select a new export folder.'
                    )

        cmds.setParent('..')

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='in'); cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=5,
                             cs=[ (1, spacer), (2, spacer), (3, spacer), (4, spacer), (5, 32) ],
                             cw=[ (1, 60), (2, 50), (3, 60), (4, 50), (5, 125) ]
                             )

        cmds.text('sme_startFrame_label', l='Start Frame')
        cmds.floatField('sme_startFrame', v=someGlobals.globals['startFrame'], pre=2, s=1, cc=lambda *args: self.setFrameRange('start', cmds.floatField('sme_startFrame', q=True, v=True)))

        cmds.text('sme_endFrame_label', l='End Frame')
        cmds.floatField('sme_endFrame', v=someGlobals.globals['endFrame'], pre=2, s=1, cc=lambda *args: self.setFrameRange('end', cmds.floatField('sme_endFrame', q=True, v=True)))

        cmds.text('sme_totalFrames_label', fn='boldLabelFont', al='left', l='Total Frames: ' + str(someGlobals.globals['startFrame'] + someGlobals.globals['endFrame']))

        cmds.setParent('..')

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout(nc=3,
                             cs=[ (1, spacer), (2, 8), (3, 8) ],
                             cw=[ (1, 170), (2, 109), (3, 140) ]
                            )

        cmds.optionMenu('sme_sceneUnits', l='Scene Units', cc=lambda *args: self.setSceneData('units', cmds.optionMenu('sme_sceneUnits', q=True, v=True)))
        cmds.menuItem('sme_sceneUnits_mm', p='sme_sceneUnits', l='mm')
        cmds.menuItem('sme_sceneUnits_cm', p='sme_sceneUnits', l='cm')
        cmds.menuItem('sme_sceneUnits_m', p='sme_sceneUnits', l='m')
        cmds.menuItem('sme_sceneUnits_km', p='sme_sceneUnits', l='km' )
        cmds.menuItem('sme_sceneUnits_in', p='sme_sceneUnits', l='in')
        cmds.menuItem('sme_sceneUnits_ft', p='sme_sceneUnits', l='ft')
        cmds.menuItem('sme_sceneUits_yd', p='sme_sceneUnits', l='yd')
        cmds.menuItem('sme_sceneUnits_mi', p='sme_sceneUnits', l='mi')

        cmds.optionMenu('sme_frameRate', l='FPS', cc=lambda *args: self.setSceneData('fps', cmds.optionMenu('sme_frameRate', q=True, v=True)))
        cmds.menuItem('sme_fps_game', p='sme_frameRate', l='15 game')
        cmds.menuItem('sme_fps_film', p='sme_frameRate', l='24 film')
        cmds.menuItem('sme_fps_pal', p='sme_frameRate', l='25 pal')
        cmds.menuItem('sme_fps_ntsc', p='sme_frameRate', l='30 ntsc')
        cmds.menuItem('sme_fps_show', p='sme_frameRate', l='48 show')
        cmds.menuItem('sme_fps_palf', p='sme_frameRate', l='50 palf')
        cmds.menuItem('sme_fps_ntscf', p='sme_frameRate', l='60 ntscf')

        cmds.optionMenu('sme_dataType', l='Data Type', cc=lambda *args: self.check())
        cmds.menuItem('sme_dataType_igc', p='sme_dataType', l='IGC')
        cmds.menuItem('sme_dataType_gameplay', p='sme_dataType', l='Gameplay')

        cmds.optionMenu('sme_frameRate', e=True, sl=fps)
        cmds.optionMenu('sme_sceneUnits', e=True, v=someGlobals.globals['units'])

        cmds.setParent('..')

        cmds.columnLayout(adj=True)

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='out'); cmds.separator(h=2, st='none')

        cmds.progressBar('sme_progressBar')

        cmds.separator(h=1, st='none')

        cmds.setParent('..')

    # main tabLayout
        cmds.tabLayout('sme_tabMain', p='sme_main_columnLayout', sc=lambda *args: self.check(), imh=0, imw=0)
        cmds.setParent('..') # sme_tabMain

        cmds.setParent('..') # sme_main_columnLayout

        # setup the data explorer export tab and gui
        data = someDataExplorer.gui()
        data.setup()
        data.refresh('sme_dataFiles')

        # setup the camera export tab and gui
        camera = someExportCamera.gui()
        camera.setup()

        # setup the rig export tab and gui
        rig = someExportRig.gui()
        rig.setup()

        # setup the mesh export tab and gui
        mesh = someExportMesh.gui()
        mesh.setup()

        cmds.showWindow(someGlobals.globals['gui'])

        sel = cmds.ls(sl=True)

        if sel != None and len(sel) > 0:
            shape, type, parent = someCommons.shapeTypeParent(sel[0])

            tabSelect = 'Camera_Export'
            if type == 'joint' or type == 'transform':
                tabSelect = 'Rig_Export'
                rig = someExportRig.gui()
                rig.assign('sme_rigToSample')
            elif type == 'mesh':
                tabSelect = 'Mesh_Export'

            cmds.tabLayout('sme_tabMain', e=True, st=tabSelect)

        self.check()

    #
    # sanity checking the UI based on which tab you currently have selected
    def check(self):
        tab = cmds.tabLayout('sme_tabMain', q=True, st=True)

        framerate = cmds.optionMenu('sme_frameRate', q=True, v=True).split(' ')

        fps = { 'fps': (framerate[0], framerate[1]) }
        units = { 'units': cmds.optionMenu('sme_sceneUnits', q=True, v=True) }
        exportPath = { 'exportPath': cmds.textField('sme_exportPath', q=True, tx=True) }
        start = { 'startFrame': cmds.floatField('sme_startFrame', q=True, v=True) }
        end = { 'endFrame': cmds.floatField('sme_endFrame', q=True, v=True) }

        someGlobals.globals.update(fps)
        someGlobals.globals.update(units)
        someGlobals.globals.update(exportPath)
        someGlobals.globals.update(start)
        someGlobals.globals.update(end)

        frameRange = someGlobals.globals['startFrame'] + someGlobals.globals['endFrame']
        cmds.text('sme_totalFrames_label', e=True, l='Total Frames: ' + str(frameRange))

        exploreEnable = 1
        exploreColor = someGlobals.color['blue']
        exportColor = someGlobals.color['green']
        exploreLabel = 'Explore Export Path'
        exportCameraLabel = 'Bake and Export Camera'
        exportRigLabel = 'Bake and Export Rig'
        exportMeshLabel = 'Export Objects'

        refreshData = someDataExplorer.gui()
        guiCheck = ''

        if (tab == 'Data_Explorer'):
            guiCheck = someDataExplorer.gui()

        elif (tab == 'Camera_Export'):
            guiCheck = someExportCamera.gui()

        elif (tab == 'Rig_Export'):
            guiCheck = someExportRig.gui()

        elif (tab == 'Mesh_Export'):
            guiCheck = someExportMesh.gui()

        if (os.path.exists(someGlobals.globals['exportPath']) == False):
            exploreEnable = False
            cmds.textScrollList('sme_dataFiles', e=True, ra=True)

            cmds.button('sme_exploreLocation_button', e=True, en=exploreEnable, bgc=exploreColor, l=exploreLabel)
        else:
            refreshData.refresh('sme_dataFiles')

        guiCheck.check()

    #
    # set the time range min\max
    def setFrameRange(self, arg, value):
        if (arg == 'start'):
            globalValue = { 'startFrame': value }
            cmds.playbackOptions(e=True, min=value)
        elif (arg == 'end'):
            globalValue = { 'endFrame': value }
            cmds.playbackOptions(e=True, max=value)

        someGlobals.globals.update(globalValue)

        self.check()

    #
    # set the scene units and fps if the user changes it
    def setSceneData(self, arg, value):
        if (arg == 'fps'):
            value = value.split(' ')
            globalValue = { 'fps': value[1] }
            cmds.currentUnit(t=value[1])

        elif (arg == 'units'):
            globalValue = { 'units': value }
            cmds.currentUnit(l=value)

        someGlobals.globals.update(globalValue)

        self.check()

    #
    # file browser dialogue for selecting a path to export to
    def browsePath(self, fieldName, startPath):
        if (os.path.exists(startPath) == False):
            startPath = os.path.dirname(cmds.file(q=True, sn=True))

        exportPath = cmds.fileDialog2(ds=2, dir=startPath, cap='Somewhere Tools Export Path', fm=3)

        if (exportPath is not None):
            if (os.path.exists(exportPath[0]) and exportPath[0] != None):
                globalValue = { 'exportPath': exportPath[0] }
                someGlobals.globals.update(globalValue)

                cmds.textField(fieldName, e=True, tx=someCommons.pathConvert(exportPath[0]))

            else:
                someCommons.sprint('Invalid path. Keeping the current path set.')

        newData = someDataExplorer.gui()
        newData.refresh('sme_dataFiles')

        self.check()

    #
    # lets be consistent about the export path format in the event
    # the user wants to manually type it in
    def exportPath(self, fieldName):
        import re

        tx = cmds.textField(fieldName, q=True, tx=True)
        newPath = someGlobals.globals['scenePath']

        if len(tx) > 0:
            path = tx.split('\\')

            if len(path):
                newPath = path[0] + '/'

                for i in range(0, len(path)):
                    if i > 0:
                        cleanPath = re.sub('[^\w\-_\. ]', '', path[i])

                        if len(cleanPath):
                            newPath = newPath + cleanPath + '/'
        elif len(tx) < 1:
            newPath = someGlobals.globals['scenePath']

        globalValue = { 'exportPath': newPath }
        someGlobals.globals.update(globalValue)

        cmds.textField('sme_exportPath', e=True, tx=someCommons.pathConvert(newPath))

        self.check()

    #
    # lets launch windows explorer or osx finder so we can browse
    # the export path, if it exists
    def exploreLocation(self, path):
        import subprocess

        if os.path.exists(path):
            if (sys.platform == 'win32'):
                subprocess.Popen('explorer ' + path)
            elif (sys.platform == 'darwin'):
                subprocess.call(["open", "-R", path])

        self.check()