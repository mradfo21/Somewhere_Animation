import os, sys, fnmatch, time
import maya.cmds as cmds
import maya.mel as mel
import someGlobals; reload(someGlobals)
import someCommons; reload(someCommons)

class gui():
    def setup(self):
        width, height, spacer = 500, 241, 2

        cmds.columnLayout('Data Explorer', adj=True, p='sme_tabMain')

        cmds.formLayout('sme_dataExplore_form', numberOfDivisions=100)

        cmds.frameLayout('sme_dataExplore_frameLayout', w=(width/2)-8, h=height+57, l='Data: 0')

        cmds.textScrollList('sme_dataFiles',
                            ann='Master object list to export from Maya. Double click an item to load the Attribute Editor for it.',
                            ams=False,
                            sc=lambda *args: self.check(),
                            dcc=lambda *args: self.check(),
                            hlc=someGlobals.color['highlight'],
                            nr=10
                            )

        cmds.setParent('..') # objects frame layout

        cmds.separator(h=2, st='none')

        cmds.rowColumnLayout('sme_dataExplore_buttonLayout', nc=3,
                             cs=[ (1, spacer), (2, spacer), (3, spacer) ],
                             cw=[ (1, ((width/2)/3)-5), (2, ((width/2)/3)-5), (3, ((width/2)/3)-5) ])

        cmds.button('sme_dataExplore_refreshButton', l='Refresh', c=lambda *args: self.refresh('sme_dataFiles'))
        cmds.button('sme_dataExplore_readOnly', l='Read-Only', en=False)
        cmds.button('sme_dataExplore_writeable', l='Writeable', en=False)

        cmds.setParent('..')

        cmds.frameLayout('sme_dataStats_frameLayout', w=(width/2)-8, h=height, l='Selected File Statistics')

        cmds.columnLayout()

        cmds.text('sme_dataExplore_date', al='left', l='Created On: ')

        cmds.separator(h=2, st='none')

        cmds.text('sme_dataExplore_time', al='left', l='Created At: ')

        cmds.rowColumnLayout(nc=1, cw=[ (1, (width/2)-5) ])

        cmds.separator(h=2, st='none'); cmds.separator(h=2, st='in'); cmds.separator(h=2, st='none')

        cmds.setParent('..')

        cmds.separator(h=2, st='none')

        cmds.text('sme_dataExplore_size', al='left', l='Size on Disk: ')

        cmds.setParent('..')

        cmds.setParent('..') # Data Export Form layout

        cmds.formLayout('sme_dataExplore_form', e=True,
                        af=[ ('sme_dataExplore_frameLayout', 'top', spacer),
                             ('sme_dataExplore_frameLayout', 'left', spacer),
                             ('sme_dataExplore_buttonLayout', 'left', spacer),
                             ('sme_dataStats_frameLayout', 'top', spacer)
                            ],

                        ac=[
                            ('sme_dataExplore_buttonLayout', 'top', spacer, 'sme_dataExplore_frameLayout'),
                            ('sme_dataStats_frameLayout', 'left', spacer, 'sme_dataExplore_frameLayout')
                            ]
                        )

    def check(self):
        maxData = cmds.textScrollList('sme_dataFiles', q=True, ni=True)
        maxSelected = cmds.textScrollList('sme_dataFiles', q=True, nsi=True)

        permission = False
        readColor = someGlobals.color['grey']
        writeColor = someGlobals.color['grey']

        fileDate = 'Created On: '
        fileTime = 'Created At: '
        fileSize = 'Size on Disk: 0 KB'

        if maxSelected > 0:
            selected = cmds.textScrollList('sme_dataFiles', q=True, si=True)[0]
            fullpath = someGlobals.globals['exportPath'] + selected

            permission = os.access(fullpath, os.W_OK)
            date, time, size = self.dataStats(fullpath)
            fileDate = 'Created On: ' + date
            fileTime = 'Created At: ' + time
            fileSize = 'Size on Disk: ' + size

            if permission == True:
                readColor = someGlobals.color['grey']
                writeColor = someGlobals.color['blue']
            else:
                readColor = someGlobals.color['blue']
                writeColor = someGlobals.color['grey']

        cmds.text('sme_dataExplore_date', e=True, l=fileDate)
        cmds.text('sme_dataExplore_time', e=True, l=fileTime)
        cmds.text('sme_dataExplore_size', e=True, l=fileSize)

        cmds.button('sme_dataExplore_readOnly', e=True, bgc=readColor)
        cmds.button('sme_dataExplore_writeable', e=True,  bgc=writeColor)

        cmds.frameLayout('sme_dataExplore_frameLayout', e=True, l='Export Data [ ' + str(maxData) + ':' + str(maxSelected) + ' ]')

    def refresh(self, listName):
        dataOnDisk = fnmatch.filter(os.listdir(someGlobals.globals['exportPath']), '*.fbx')
        listSelection = cmds.textScrollList(listName, q=True, si=True)
        listData = cmds.textScrollList(listName, q=True, ai=True)

        if len(dataOnDisk) > 0:
            for file in dataOnDisk:
                tok = file.split('\\')
                filename = tok[len(tok)-1]

                if listData != None:
                    if filename not in listData:
                        cmds.textScrollList(listName, e=True, a=filename)
                else:
                    cmds.textScrollList(listName, e=True, a=filename)

        self.check()

    def dataStats(self, file):
        import time

        stats = time.ctime(os.stat(file).st_mtime)

        tok = stats.split(' ')
        date = tok[0] + ' ' + tok[1] + ' ' + tok[2] + ' ' + tok[4]
        time = self.convertTime(tok[3])
        size = self.convert_size(float(os.stat(file)[6]))

        return date, str(time), str(size)

    def convertTime(self, timeValue):
      ampm = timeValue.split (":")
      if (len(ampm) == 0) or (len(ampm) > 3):
        return time

      hour = int(ampm[0]) % 24
      isam = (hour >= 0) and (hour < 12)

      if isam:
        ampm[0] = ('12' if (hour == 0) else "%02d" % (hour))
      else:
        ampm[0] = ('12' if (hour == 12) else "%02d" % (hour-12))

      return ':'.join (ampm) + ('am' if isam else 'pm')

    def convert_size(self, size_bytes):
        import math
        if size_bytes == 0:
            return "0B"

        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return "%s %s" % (s, size_name[i])