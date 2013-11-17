import urllib as ul
import httplib as hl
from BeautifulSoup import BeautifulStoneSoup as bs
from mutagen.mp3 import MP3
from mutagen import id3 as mu
import os.path as op

FRONT_COVER = 3

ARTWORK_TAG = u'APIC:'
MIME_PNG = 'image/png'
MIME_JPEG = 'image/jpeg'

SIZE_34X34=b'small'
SIZE_64X64=b'medium'
SIZE_174X174=b'large'
SIZE_300X300=b'extralarge'
SIZE_RAW=b'mega'

ERROR_MSG=b'FAYUUUL!'

sApiKey = b'c8e1cd060b177d97acd579faa5a4ef5e'
sLfmUrl='ws.audioscrobbler.com'

def fDownload(sSource, sTarget):
    '''
    Downloads file from Internet.
    sSource - source file URL
    sTarget - target file name
    '''
    if sSource != ERROR_MSG:
        fSourceImg = ul.urlopen(sSource)
        try:
            fTargetImg = open(sTarget, "wb")
        # A silly workaround for image filw write permissions
        # Happens a lot, so needs to be solved
        except IOError:
            from random import randint
            import os.path
            nFileSuffix = randint(100,500)
            fTargetImg = open( \
                os.path.splitext(sTarget)[0] + \
                '_' + str(nFileSuffix) + \
                os.path.splitext(sTarget)[1],\
                 "wb")
        sData = fSourceImg.read()
        fTargetImg.write(sData)
        fTargetImg.close()
        fSourceImg.close()

def fBindArtwork(sTrackAddr, sImgAddr, sArtAppend=u'frontcover'):
    '''
    Writes image data to mp3 file as APIC id3 frame.
    sTrackAddr - audio file address;
    sImgAddr - PNG/JPEG image file address;
    '''
    #Open an Mp3 file
    muTrack=MP3(sTrackAddr)
    #Open picture file
    fPicture=file(sImgAddr, 'rb')
    sPic=fPicture.read()

    #Cheching image format
    if op.splitext(sImgAddr)[-1].lower()=='png': sMimeType=MIME_PNG
    elif (op.splitext(sImgAddr)[-1].lower()=='jpg'
        or op.splitext(sImgAddr)[-1].lower()=='jpeg'
        or op.splitext(sImgAddr)[-1].lower()=='jpe'): sMimeType=MIME_JPEG
    else: sMimeType=''

    #Creating a temporary APIC instance
    sArtworkTag=ARTWORK_TAG+sArtAppend
    muPic=mu.APIC(encoding=3, mime=MIME_JPEG, type=FRONT_COVER,
        desc=u'Album front cover', data=0)
    muTrack.tags[sArtworkTag]=muPic

    #Write image data to mp3 file
    muTrack.tags[sArtworkTag].data=sPic
    muTrack.save(v1=2)

    fPicture.close()

def fGetSongInfo(sSongLocation):
    '''Gets Artist and Album data from an mp3 file.
    Returns a string (Artist, Album) tuple
    sSongLocation - location of the file'''
    muTrack=MP3(sSongLocation)
    sAlbum = muTrack.tags['TALB'].text
    sArtist = muTrack.tags['TPE1'].text
    return sArtist, sAlbum

def fCreateLfmRequest((lArtist, lAlbum)):
    '''
    Returns Last.FM API request
    '''
    print (lArtist, lAlbum)
    sArtist=''.join(lArtist).encode('cp1251')
    sAlbum=''.join(lAlbum).encode('cp1251')

    sArtistTmp=ul.quote_plus(sArtist)
    sAlbumTmp=ul.quote_plus(sAlbum)

    dParams={"api_key" : sApiKey, 'artist' : sArtistTmp, 'album' : sAlbumTmp, 'method' : 'album.getinfo'}
    return ul.unquote(ul.urlencode(dParams))

def fQueryLfm(sLfmRequest):
    '''
    Returns an XML result from Last.FM
    '''
    cCon=hl.HTTPConnection(sLfmUrl)

    cCon.request('GET', '/2.0/?'+sLfmRequest)   #????? ? ?????? ????????? =)
    cResult = cCon.getresponse()
    return cResult.read()
    cCon.close()

def fUnparseImgUrl(sSrc, sSizeId):
    '''
    Gets an image URL from Last.FM querry result; returns URL of image ("large", 300x300).
    '''
    bsSoup=bs(sSrc)
    if bsSoup.find('image', size=sSizeId)==None: return ERROR_MSG
    else:
        try:
            return bsSoup.find('image', size=sSizeId).text
        except:
            return ERROR_MSG
