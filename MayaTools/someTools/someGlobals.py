import maya.cmds as cmds
import maya.mel as mel
import sys, os

globals = {
           'version': 1.5,
           'gui': 'someToolsGUI',
           'scriptRoot': cmds.internalVar(usd=True) + 'someTools/',
           'scene': os.path.basename(cmds.file(q=True, sn=True)[:-3]),
           'scenePath': os.path.dirname(cmds.file(q=True, sn=True)),
           'exportPath': os.path.dirname(cmds.file(q=True, sn=True)),
           'startFrame': cmds.playbackOptions(q=True, min=True),
           'endFrame': cmds.playbackOptions(q=True, max=True),
           'units': cmds.currentUnit(q=True, l=True),
           'fps': (0, ''),
        }

camera = {
          'default': 'RenderCam',
          'filename': globals['scene'] + '_Camera',
          'name': globals['scene'] + '_Camera',
          'node': ''
         }

rig = {
       'default': 'DeformationSystem',
       'rootDefault': 'Root_M',
       'filename': globals['scene'] + '_Rig',
       'name': '',
       'node': ''
      }

mesh = {
        'filename': globals['scene'] + '_Mesh'
       }

color = {
         'green': [ 0.33, 1.0, 0.33 ],
         'blue': [ 0.5, 0.75, 0.8 ],
         'red': [ 1.0, 0.4, 0.4 ],
         'highlight': [ 0.3, 0.4, 0.6 ],
         'grey': [ 0.33, 0.33, 0.33 ]
        }