import maya.cmds as cmds
import maya.mel as mel
import sys, os

# attempt to load the tools
def someLauncher():
    root = cmds.internalVar(usd=True) + 'someTools/'

    errors = []
    scripts = [
               'someGlobals.py',
               'someCommons.py',
               'someExportCamera.py',
               'someExportRig.py',
               'someExportMesh.py',
               'someDataExplorer.py',
               'FBXWrapper.py',
               'someTools.py'
              ]

    for script in scripts:
        filename = root + script

        if (os.path.isfile(filename) == False):
            errors.append(script)

    if (len(errors) > 0):
        sys.stdout.write('-- [ Somewhere Tools Errors ] ------------\n')
        sys.stdout.write('The below scripts should live at this path > ' + os.path.abspath(root) + '\n')
        print(errors);
        sys.stdout.write('** Somewhere Tools has launch errors! Please check script editor for details ... **\n')
    else:
        import someGlobals; reload(someGlobals)
        import someTools; reload(someTools)

        if (cmds.window(someGlobals.globals['gui'], ex=True)):
            cmds.deleteUI(someGlobals.globals['gui'])

        tools = someTools.gui()
        tools.setup()

# check to make sure the file has been saved or loaded, ...can't be a enw file.
if len(os.path.basename(cmds.file(q=True, sn=True)[:-3])):
    someLauncher()
else:
    sys.stdout.write('Scene has not been saved. Please load a scene or save the current one and try again.')