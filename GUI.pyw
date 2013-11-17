import wx
import os.path as op
import os
import pyBinder as pb

FRAME_OPACITY=200
DEFAULT_IMAGE_NAME='Folder.jpg'

def fProcessTracks(lFileNames, wFrame):
    '''????????? ?????? ??????'''

    #???? ? ?????? ?????? mp3-????...
    for sSongLocation in lFileNames:
        if op.splitext(sSongLocation)[-1].lower()=='.mp3': break

    #...? ???????? ??? ???? ??????? ???????
    wFrame.fSetGauge('Getting song info...', 20)
    tSongInfo= pb.fGetSongInfo(sSongLocation)

    sImageLocation=op.join(op.dirname(sSongLocation), DEFAULT_IMAGE_NAME)

    wFrame.fSetGauge('Creating Last.FM request...', 40)
    sLfmQuery=pb.fCreateLfmRequest(tSongInfo)

    wFrame.fSetGauge('Getting data from Last.FM...', 60)
    sLfmResult=pb.fQueryLfm(sLfmQuery)

    wFrame.fSetGauge('Analysing Last.FM request...', 80)
    sImgUrl=pb.fUnparseImgUrl(sLfmResult, pb.SIZE_300X300)

    wFrame.fSetGauge('Downloading image...', 90)
    pb.fDownload(sImgUrl, sImageLocation)

    wFrame.fSetGauge('Almost ready.', 100)
    wFrame.fSetImage(sImageLocation)

    #????????? ???? mp3-?????? ? ?????? ?????????? ????????
    #(??????????????, ??? ??? ????? ?? ?????? ???????)
    nGaugeStep=int(100/len(lFileNames))
    nGaugeValue=0
    for sFileName in lFileNames:
        if op.isfile(sFileName) and (op.splitext(sFileName)[-1].lower() == '.mp3'):
            nGaugeValue+=nGaugeStep
            wFrame.fSetGauge(op.basename(sFileName), nGaugeValue)
            pb.fBindArtwork(sFileName, sImageLocation)
    #??????.
    wFrame.fSetGauge('Ready', 100)

class CDropTarget(wx.FileDropTarget):
    '''????? ??? Drag and Drop'''

    def __init__(self, wTargetWidget):
        wx.FileDropTarget.__init__(self)
        self.window=wTargetWidget
        self.wFrame=self.window.GetParent()

    def OnDropFiles(self, x, y, lDroppedContent):
        #??????? ????????? ?????!
        lFileNames=[]
        for sPath in lDroppedContent:
            if op.isdir(sPath):
                lInnerFileNames=[op.join(sPath, sFileName) for sFileName in os.listdir(sPath)]
                fProcessTracks(lInnerFileNames, self.wFrame)
            if op.isfile(sPath):
                lFileNames.append(sPath)
        if lFileNames!=[]:
            fProcessTracks(lFileNames, self.wFrame)

class CDropFrame(wx.Frame):
    '''?????? ??????????'''

    def __init__(self, nSize):
        wx.Frame.__init__(self, None, title='pyBinder',
            style=wx.STAY_ON_TOP|wx.FRAME_TOOL_WINDOW|wx.CLOSE_BOX|wx.CAPTION|wx.SYSTEM_MENU)

        #??? ?????? size - ??? ?????? ???? ?????? ? ??????????,
        #??????? ??? ???????? ??????????? ?????? ?????? clientSize ?????? size
        self.SetClientSize((nSize,)*2)
        self.nSize=nSize

        #wPanel ????????? Drag'????? ???????
        self.wPanel=wx.Panel(self,pos=(0,0), size=(nSize,)*2)
        self.wPanel.SetBackgroundColour('#FFFFFF')
        wDropTarget=CDropTarget(self.wPanel)
        self.wPanel.SetDropTarget(wDropTarget)

        #???????? ??? ???????.
        #????? ?????????? ?? ??????? ??????? ???????? fProcessTracks()
        self.wBgFrame=wx.StaticBitmap(self.wPanel)
        self.fSetImage('Backgrounds\\Background2.jpg')

        #????????? ???? ProgressBar
        self.wText=wx.StaticText(self.wBgFrame, -1, 'Drop some mp3 files here...', (0,(nSize/2)-15), (nSize,35), wx.ALIGN_CENTER)
        self.wText.SetBackgroundColour('#000000')
        self.wText.SetForegroundColour('#FFFFFF')

        self.wGauge=wx.Gauge(self.wText, -1, 100, (5,20), (nSize-10,10))
        self.wGauge.SetValue(0)

        #??????????? ?????? ? ?????? ?????? ???? ??????
        tScreenSize=wx.ScreenDC().GetSize()
        tFrameSize=self.GetSize()
        self.SetPosition(tuple(tScreenSize-tFrameSize))

        #?????? ???????????? ??? ?????
        self.SetTransparent(FRAME_OPACITY)
        #??????!
        self.Show()

    #????????? ???????? ???????????
    def fSetImage(self, sImgSrc):
        wImage=wx.Image(sImgSrc)
        wImage.Rescale(self.nSize, self.nSize)
        wImage=wImage.ConvertToBitmap()
        self.wBgFrame.SetBitmap(wImage)
    #?????????? ?????? ? ??????-????
    def fSetGauge(self, sMessage, nValue):
        self.wText.SetLabel(sMessage)
        #?????? ?????????? ???? ?????????? ?????? ??? ????????? =\
        self.wText.SetSize((self.nSize,35))
        self.wGauge.SetValue(nValue)

if __name__=='__main__':
    aApp=wx.PySimpleApp()
    wDropFrame=CDropFrame(180)
    aApp.MainLoop()