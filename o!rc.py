#import urllib
#import urllib.request
#import base64
import lzma
import json
import pygame
import pygame.gfxdraw
import pygame.freetype
#import http
import zipfile
import glob
import atexit
import os
import shutil
import signal
import sys
import string
import requests#######
import eyed3
from eyed3 import mp3
#import pydub
#import pydub.utils
#from pydub.utils import mediainfo#############

BLACK = (0,0,0)
WHITE = (255,255,255)
BRIGHTCOLORS = [(255,0,255), (255,128,0), (255,255,255), (0,255,0), (255,0,0), (0,255,255), (255,255,0), (64,64,255), (128,255,0)]
DIMCOLORS = [(128,0,128), (128,64,0), (128,128,128), (0,128,0), (128,0,0), (0,128,128), (128,128,0), (32,32,128), (64, 128, 0)]

#even finer cursor trails?

#sliders


#if a key is pressed and another key is pressed during that key press it should be registered but isnt


#delete shit at end

#figure out key presses and subsequetly hit on the circles 300/100 etc and display that info

#maybe remove files at beginning

#make sure file exists before removing it

#if we can ever download osr file we can get audio offset from osu file

APIKEY="<YOUR-API-KEY-HERE>"
mode="0"    #(0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania)
mapid="555797"#"345189"#"129891"#
numberofreplays=10
speedmultiplier=1
replaylist = []
beatmapxl=[-1]*1000000
beatmapyl=[-1]*1000000####length?
currentcircles=[]
circlelist=[]
breaklist=[]
beatmapuniversaloffset=0
beatmapapproachrate=0.0
#keypresswindowlist=[]

def getMSfromAR(ar):##################################decimals....
    if ar>9:
        return 450
    elif ar>8:
        return 600
    elif ar>7:
        return 750
    elif ar>6:
        return 900
    elif ar>5:
        return 1050
    elif ar>4:
        return 1200
    elif ar>3:
        return 1320
    elif ar>2:
        return 1440
    elif ar>1:
        return 1560
    elif ar>0:
        return 1680
    else:
        return 1800
"""

Retrieving files

"""
#can we do this with urllib and cookies?
payload = {"username": "tumnut", "password": "uhbygvtfc", "redirect": "index.php", "sid": "", "login": "Login"}

with requests.Session() as s:
    p = s.post('https://osu.ppy.sh/forum/ucp.php?mode=login', data=payload)
    print("Retrieving avatars...")
    html=s.post('https://osu.ppy.sh/b/'+mapid+'&m='+mode).text
    currentpoundindex=0
    currentindex=html.index('Top 50 Scoreboard', 0)
    userid=0
    for osr in range(0,numberofreplays):
        html=s.post('https://osu.ppy.sh/b/'+mapid+'&m='+mode).text
        currentindex=html.index('<a href=\'/u/', currentindex)+1
        currentpoundindex=html.index(">", currentindex)
        userid=int(html[currentindex+11:currentpoundindex-1])
        html=s.post('https://osu.ppy.sh'+html[currentindex+8:currentpoundindex-1]).text
        currentindex2=0
        currentpoundindex2=0
        currentperiodindex=0
        currentindex2=html.index('<div class="avatar-holder"><img src="//a.ppy.sh/', currentindex2)+1+37#check if this exists
        currentperiodindex=html.index(".", currentindex2)
        currentpoundindex2=html.index("\"", currentindex2)
        local_filename = "temp."+html[currentperiodindex+8:currentpoundindex2]
        r = s.get('https:'+html[currentindex2-1:currentpoundindex2], stream=True)#######################
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
        

    print("Done retrieving avatars.")
    #'<a href=\'/u/'
    #'avatar-holder'

    #p=s.post('https://osu.ppy.sh/u/tumnut')#b/'+mapid)
    #print(p.text)
    
    local_filename = "temp."+mapid+"osu.txt"
    beatmapsetidstr=""
    r=s.get('https://osu.ppy.sh/osu/'+mapid)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    print("Reading from the .osu file.")
    f = open(local_filename, encoding="utf8")
    readinghitobjs=False
    readingbreaks=False
    linecount=0
    while True:################have a list of currently in the elapsedtime circles that should be in the queue to be put on the screen so we can extrend the length of time they are on there
        text = f.readline()
        linecount+=1
        if text=="":
            break
        if 'BeatmapSetID:' in text:
            beatmapsetidstr=text[13:]
        if 'AudioLeadIn:' in text:
            beatmapuniversaloffset=int(text[13:])
        if 'ApproachRate:' in text:
            beatmapapproachrate=float(text[13:])
        elif '[Events]' in text:
            readingbreaks=True
        elif '[HitObjects]' in text:
            readingbreaks=False
            readinghitobjs=True
        elif readingbreaks:
            data=text.split(',')
            #print(data)
            if data[0]=='2':
                breaklist.append((int(data[1]), int(data[2])))
        elif readinghitobjs:
            data=text.split(',')
            circlelist.append((int(data[2])-getMSfromAR(beatmapapproachrate)+beatmapuniversaloffset, 350, 25+int(data[0]), int(data[1])))
            """for i in range(-32,32):
                if not circlelist[len(circlelist)-1][0]+i in keypresswindowlist:
                    keypresswindowlist.append(circlelist[len(circlelist)-1][0]+i)"""
    f.close()
    i=len(circlelist)-1
    x=-9999
    y=-9999
    count=0
    while i >= 0:
        if circlelist[i][2]!=x or circlelist[i][3]!=y:########what if first few circles are stacked
            #print("unstacking")
            x=circlelist[i][2]
            y=circlelist[i][3]
            iplaceholder=i
            j=1
            while count>0:
                circlelist[i+j]=(circlelist[i+j][0], circlelist[i+j][1], circlelist[i+j][2]-2*count, circlelist[i+j][3]-2*count)
                count-=1
                j+=1
                #change xy vals
            i-=1;
        else:
            count+=1
            i-=1
    print("Done reading from the .osu file.")
    print("Downloading replays...")#######################will get the users highest score if they have one in top 1k or some shit atm
    html=s.post('https://osu.ppy.sh/b/'+mapid+'&m='+mode).text
    currentpoundindex=0
    currentindex=0
    for osr in range(0,numberofreplays):
        local_filename = "temp."+mapid+"osr"+str(osr)+".osr"
        currentindex=html.index("/web/osu-getreplay.php?", currentindex)+1
        currentpoundindex=html.index("'", currentindex)
        r = s.get('https://osu.ppy.sh'+html[currentindex-1:currentpoundindex], stream=True)#######################
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
    print("Done downloading replays.")
    print("Downloading mp3...")
    local_filename = "temp."+mapid+"osz.zip"
    currentindex=html.index("/d/")
    currentpoundindex=html.index("\"", currentindex)
    r = s.get('https://osu.ppy.sh' + html[currentindex:currentpoundindex], stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    zip_ref = zipfile.ZipFile(local_filename, 'r')
    zip_ref.extractall("temp."+mapid+"unzip")
    zip_ref.close()
    print("Done downloading mp3.")
#check sampling rate and make sure we can play it on mixer at full speed

def terminate(signum, frame):
    if os.path.exists("temp."+mapid+"osu.txt"):
        os.remove("temp."+mapid+"osu.txt")
    if os.path.exists("temp."+mapid+"osr.osr"):
        os.remove("temp."+mapid+"osr.osr")
    if os.path.exists("temp."+mapid+"osz.zip"):
        os.remove("temp."+mapid+"osz.zip")
    if pygame.mixer.get_init():
            pygame.mixer.quit()
    if os.path.exists("temp."+mapid+"unzip"):
        shutil.rmtree("temp."+mapid+"unzip")
    sys.exit()
signal.signal(signal.SIGINT, terminate)
signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGABRT, terminate)
signal.signal(signal.SIGFPE, terminate)
signal.signal(signal.SIGILL, terminate)
signal.signal(signal.SIGSEGV, terminate)
def decodeuleb128(f):
    retstring=""
    bitstring=list("0000000")
    total = 0
    while(retstring=="" or int.from_bytes(byte, byteorder='little')>=128):
        byte=f.read(1)
        for i in range(0,7):
            if(int.from_bytes(byte, byteorder='little')&2**i):
                bitstring[len(bitstring)-1-i]='1'
        retstring="".join(bitstring)+retstring
    return int(retstring, 2)

class replayinstance:
    def __init__(self, filename):
        self.xyl=[]
        self.kl=[]
        self.replaynumber=(int)(filename[filename.index(".osr")-1])
        self.modlist=[]
        self.color = BRIGHTCOLORS[self.replaynumber%9]##############
        self.dimcolor = DIMCOLORS[self.replaynumber%9]################
#########################
        print("Reading from "+filename+".")
        with open(filename, "rb") as f:
            self.gamemode=int.from_bytes(f.read(1), byteorder='little')
            self.gameversion=int.from_bytes(f.read(4), byteorder='little')
            ####
            stringexists = int.from_bytes(f.read(1), byteorder='little')==11
            bytelength=decodeuleb128(f) if stringexists else 0
            self.beatmapmd5=f.read(bytelength).decode("utf-8") if stringexists else ""
            ####
            stringexists = int.from_bytes(f.read(1), byteorder='little')==11
            bytelength=decodeuleb128(f) if stringexists else 0
            self.playername=f.read(bytelength).decode("utf-8") if stringexists else ""
            ####
            stringexists = int.from_bytes(f.read(1), byteorder='little')==11
            bytelength=decodeuleb128(f) if stringexists else 0
            self.replaymd5=f.read(bytelength).decode("utf-8") if stringexists else ""
            ####
            self.numberof300s=int.from_bytes(f.read(2), byteorder='little')
            self.numberof100s=int.from_bytes(f.read(2), byteorder='little')
            self.numberof50s=int.from_bytes(f.read(2), byteorder='little')
            self.numberofgekis=int.from_bytes(f.read(2), byteorder='little')
            self.numberofkatus=int.from_bytes(f.read(2), byteorder='little')
            self.numberofmisses=int.from_bytes(f.read(2), byteorder='little')
            self.totalscore=int.from_bytes(f.read(4), byteorder='little')
            self.greatestcombo=int.from_bytes(f.read(2), byteorder='little')
            self.fc=int.from_bytes(f.read(1), byteorder='little')
            self.modsused=int.from_bytes(f.read(4), byteorder='little')
            ####
            stringexists = int.from_bytes(f.read(1), byteorder='little')==11
            bytelength=decodeuleb128(f) if stringexists else 0
            self.lifebargraph=f.read(bytelength).decode("utf-8") if stringexists else ""
            ###
            self.timestamp=int.from_bytes(f.read(8), byteorder='little')
            self.bytelengthofreplaydata=int.from_bytes(f.read(4), byteorder='little')
            self.inputdata=lzma.decompress(f.read(self.bytelengthofreplaydata)).decode().split(',')
            s=requests.Session().get("https://osu.ppy.sh/api/get_user?k="+APIKEY+"&u="+self.playername+"&type=string").text#.index("user_id")
            uidindex=s.index("user_id", 0)
            qindex=s.index("\"", uidindex+12)
            #print(s[uidindex+10:qindex])
            #print(requests.Session().get("https://osu.ppy.sh/api/get_user?k="+APIKEY+"&u="+self.playername+"&type=string").text.index("user_id"))
            self.userid=s[uidindex+10:qindex]#json.load(requests.Session().get("https://osu.ppy.sh/api/get_user?k="+APIKEY+"&u="+self.playername+"&type=string").json()[0])["user-id"]
            #print(requests.Session().get("https://osu.ppy.sh/api/get_user?k="+APIKEY+"&u="+self.playername+"&type=string").json())
            self.avatarpath=glob.glob("temp."+self.userid+"_*")[0]##########################################################################################################
            ##########figuring out mods ASSUMING MODE IS "0"

        ###also what if mod number is greater than 32765
        if self.modsused>=16384:
            self.modlist.append("PF")
            self.modsused-=16384
        if self.modsused>=4096:
            self.modlist.append("SO")
            self.modsused-=4096
        if self.modsused>=1024:
            self.modlist.append("FL")
            self.modsused-=1024
        if self.modsused>=576:
            self.modlist.append("NC")
            self.modsused-=576
        if self.modsused>=256:
            self.modlist.append("HT")
            self.modsused-=256
        if self.modsused>=64:
            self.modlist.append("DT")
            self.modsused-=64
        if self.modsused>=32:
            self.modlist.append("SD")
            self.modsused-=32
        if self.modsused>=16:
            self.modlist.append("HR")
            self.modsused-=16
        if self.modsused>=8:
            self.modlist.append("HD")
            self.modsused-=8
        if self.modsused>=2:
            self.modlist.append("EZ")
            self.modsused-=2
        if self.modsused>=1:
            self.modlist.append("NF")
            self.modsused-=1
            print("Finished processing replay for " + username + ".")

        
        count=0
        for event in self.inputdata:
            count+=1
            data=event.split('|')
                #if beatmapuniversaloffset==0:
                    #beatmapuniversaloffset=int(data[0])
            ms=(int(data[0]))#####does this always end with -12345
            if ms == 12345 or ms == -12345:#########always 12345???
                break
            if ms >= 0:
                ms=ms*speedmultiplier
                while ms > 0:
                    ms-=1
                    if "HR" in self.modlist:
                        self.xyl.append((50+int(float(data[1])*2),768+int(-1*float(data[2])*2)))###could we ever use floats?
                    else:
                        if(float(data[1]) > 20000.0):
                            #print("AHHH")
                            self.xyl.append((50+int(float(data[1])/25),int(float(data[2])/25)))#why the fuck does this work///why is this needed?///crystal- worldwide choppers  
                        else:
                            self.xyl.append((50+int(float(data[1])*2),int(float(data[2])*2)))
                    self.kl.append(int(data[3]))
            if ms <= -1000:##what number should be here
                self.xyl.clear()
                self.kl.clear()

        self.k2keytimings=[]
        refractoryperiod=0####100 is reasonable (>300bpm streaming) but 75 is safe (>330bpm streaming) (this is one key so im gonna opt for 300bpm bc noone can singel tap 300bpm streams (aka600bpm))
##################^^^^^^^^^^^^^^^^^^^^do we really even need this
        canaccept=True


        for i in range(0,len(self.kl)):
            """if self.kl[i]>=10 and canaccept:
                self.k2keytimings.append(i)
                canaccept=False
            elif self.kl[i]<10 and not canaccept"""
            #print(self.kl[i])
            if refractoryperiod>0:
                refractoryperiod+=1
            elif self.kl[i]>=10 and refractoryperiod==0:
                canadd=True;
                #if we are in a break, dont add to the key count
                for breakinstance in breaklist:
                    if i>breakinstance[0] and i<breakinstance[1]:
                        canadd=False
                if i<circlelist[0][0]-40:
                    canadd=False
                if canadd:
                    #if i < 1000:
                        #print("key logged as pressed at " + str(i) + ".")
                        #if(self.playername == "Totori"):
                            #print(self.inputdata)
                    self.k2keytimings.append(i)
                    refractoryperiod+=1
            if self.kl[i]<10 and refractoryperiod>=50:
                #if i < 1000:
                    #print("key logged as released, refrectory period now 0");
                refractoryperiod=0
        #print(len(self.k2keytimings))
        self.k2list=[]
        k2keycount=0
        #print(self.k2keytimings)
        for i in range(1,len(self.k2keytimings)):
            self.k2keytimings[len(self.k2keytimings)-i]-=self.k2keytimings[len(self.k2keytimings)-i-1]
        #print(self.k2keytimings[1])
        #print(circlelist[0][0])
        for keytiming in self.k2keytimings:
            while keytiming>1:######1 or 0??
                self.k2list.append(k2keycount)
                keytiming-=1
            k2keycount+=1
        self.k1keytimings=[]
        refractoryperiod=0####100 is reasonable (>300bpm streaming) but 75 is safe (>330bpm streaming) (this is one key so im gonna opt for 300bpm bc noone can singel tap 300bpm streams (aka600bpm))
##################^^^^^^^^^^^^^^^^^^^^do we really even need this
        canaccept=True


        for i in range(0,len(self.kl)):
            """if self.kl[i]>=10 and canaccept:
                self.k2keytimings.append(i)
                canaccept=False
            elif self.kl[i]<10 and not canaccept"""
            #print(self.kl[i])
            tempkli=self.kl[i]
            if tempkli>=10:
                tempkli-=10

            
            if refractoryperiod>0:
                refractoryperiod+=1
            elif tempkli>=5 and refractoryperiod==0:
                canadd=True;
                #if we are in a break, dont add to the key count
                for breakinstance in breaklist:
                    if i>breakinstance[0] and i<breakinstance[1]:
                        canadd=False
                if i<circlelist[0][0]-40:
                    canadd=False
                if canadd:
                    #if i < 1000:
                        #print("key logged as pressed at " + str(i) + ".")
                        #if(self.playername == "Totori"):
                            #print(self.inputdata)
                    self.k1keytimings.append(i)
                    refractoryperiod+=1
            if self.kl[i]<5 and refractoryperiod>=50:
                #if i < 1000:
                    #print("key logged as released, refrectory period now 0");
                refractoryperiod=0
        #print(len(self.k2keytimings))
        self.k1list=[]
        k1keycount=0
        #print(self.k2keytimings)
        for i in range(1,len(self.k1keytimings)):
            self.k1keytimings[len(self.k1keytimings)-i]-=self.k1keytimings[len(self.k1keytimings)-i-1]
        #print(self.k1keytimings[1])
        #print(circlelist[0][0])
        for keytiming in self.k1keytimings:
            while keytiming>1:######1 or 0??
                self.k1list.append(k1keycount)
                keytiming-=1
            k1keycount+=1
        print("Done reading from "+filename+".")

"""

Creating Replays

"""

for play in range(0,numberofreplays):#######personal files
    replaylist.append(replayinstance("temp."+mapid+"osr"+str(play)+".osr"))
"""

Setting up PyGame

"""
WIDTH=1366
HEIGHT=768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.freetype.init()
f=pygame.freetype.Font("Aller_Lt.ttf",33-numberofreplays/2)#make this variable size


def exitActions():
    if os.path.exists("temp."+mapid+"osu.txt"):
        os.remove("temp."+mapid+"osu.txt")
    if os.path.exists("temp."+mapid+"osr.osr"):
        os.remove("temp."+mapid+"osr.osr")
    if os.path.exists("temp."+mapid+"osz.zip"):
        os.remove("temp."+mapid+"osz.zip")
    if pygame.mixer.get_init():
            pygame.mixer.quit()
    if os.path.exists("temp."+mapid+"unzip"):
        shutil.rmtree("temp."+mapid+"unzip")
atexit.register(exitActions)

#Fukagyaku Replace
#try:
#    pygame.mixer.init(mp3.Mp3AudioFile(glob.glob("temp."+mapid+"unzip/*.mp3")[0]).info.sample_freq)#####
#except:
#    print("48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n48000\n")
pygame.mixer.init(48000)
pygame.mixer.music.load(glob.glob("temp."+mapid+"unzip/*.mp3")[0])
#pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.3)
pygame.display.set_caption('o!rc')
screen.fill(BLACK)
clock = pygame.time.Clock()
elapsedtime=0#beatmapuniversaloffset
taillength=100
mixerswitch=0
buttondim=HEIGHT/numberofreplays
prevxy=[]
"""
target = open("tempopppp44p.txt", 'w')
lastloc=1
print(circlelist[0][0])
xd=""
count=0
clis=[]
for a in circlelist:
    if a[0]!=6731:
        clis.append(a[0])
        lastloc=6732
        continue
    placehold=a[0]
    #print(placehold)
    while placehold>lastloc:
        3xd=xd+" "
        #print(" ", end="")
        placehold = placehold-1
    lastloc=a[0]+1
    #xd=xd+"1\n"
    #print("1")
for i in range(6732, len(replaylist[2].kl)):
    count=count+1
    if replaylist[2].kl[i]>=10:
        xd=xd+"^"
        #replaylist[2].kl[i]-=10
    #elif replaylist[2].kl[i]>=5:
        #xd=xd+"^"
        #replaylist[2].kl[i]-=5
    else:
        xd=xd+"_"
    if i in clis:
        xd=xd+"\n"

    
target.write(xd)
target.close()
"""
while True:###elapsedtime<len(replay.xl):############change this to equivalent of elapsedtime<len(replay.xl)
#######
    if(elapsedtime >= beatmapuniversaloffset and not pygame.mixer.get_busy() and mixerswitch==0):
        mixerswitch=1
        pygame.mixer.music.play()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #exitActions()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
            elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_c:
                quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # scroll up
                taillength += 10
            elif event.button == 5: # scroll down
                taillength = max(0, taillength - 10)
            pygame.display.set_caption('o!rc taillength=%d' % (taillength))
    timepassed=clock.tick_busy_loop()
    elapsedtime+=timepassed##/100#####################
    i=0
    while i<len(currentcircles):
        if(currentcircles[i]):
            currentcircles[i]=(currentcircles[i][0]-timepassed, currentcircles[i][1], currentcircles[i][2])
        i+=1
    i=0
    while i<len(circlelist):
        if circlelist[i][0]<= elapsedtime:
            currentcircles.append((circlelist[i][1], circlelist[i][2], circlelist[i][3]));
            circlelist.pop(i)
            i-=1
        i+=1
    i=0
    while i<len(currentcircles):
        if currentcircles[i][0]<=0:
            currentcircles.pop(i)
            i-=1
        i+=1;
    screen.fill(BLACK)
    for circle in currentcircles:
        if elapsedtime>=0 and circle[1] > -1:
            pygame.gfxdraw.aacircle(screen, circle[1]*2, circle[2]*2, 50, WHITE)
    avgx=0
    avgy=0
    for replay in replaylist:
        k=replay.kl[elapsedtime]
        if k>=10:
            screen.fill(replay.color, (WIDTH-buttondim, buttondim*replay.replaynumber, buttondim, buttondim))
            k-=10
        if k>=5:
            screen.fill(replay.color, (WIDTH-2*buttondim, buttondim*replay.replaynumber, buttondim, buttondim))
            k-=5
        screen.blit(pygame.transform.scale(pygame.image.load(replay.avatarpath), (int(buttondim), int(buttondim))), (WIDTH-3*buttondim, buttondim*replay.replaynumber))
        avgx+=replay.xyl[elapsedtime][0]
        avgy+=replay.xyl[elapsedtime][1]
        prevxy.append((avgx,avgy))
        #print(str(replay.xyl[elapsedtime][0]) + " " + str(replay.xyl[elapsedtime][1]));
        pygame.gfxdraw.filled_circle(screen, replay.xyl[elapsedtime][0], replay.xyl[elapsedtime][1], 5, replay.color)
        for linenumber in range(1,taillength+1):
            if elapsedtime-linenumber>=0 and replay.kl[elapsedtime-linenumber+1] >= 5 and elapsedtime>len(replay.xyl)/1000:
                pygame.gfxdraw.line(screen, replay.xyl[elapsedtime-linenumber+1][0], replay.xyl[elapsedtime-linenumber+1][1], replay.xyl[elapsedtime-linenumber][0], replay.xyl[elapsedtime-linenumber][1], replay.color)
        f.render_to(screen, (WIDTH-2*buttondim+buttondim/3-numberofreplays*1.3, (buttondim*replay.replaynumber)+buttondim/4), str(replay.k1list[elapsedtime]), replay.dimcolor)
        f.render_to(screen, (WIDTH-2*buttondim+buttondim+buttondim/3-numberofreplays*1.3, (buttondim*replay.replaynumber)+buttondim/4), str(replay.k2list[elapsedtime]), replay.dimcolor)
        #f.render_to(screen, (WIDTH-2*buttondim+buttondim/3-numberofreplays*1.5, (buttondim*replay.replaynumber)+buttondim/4), str(elapsedtime), replay.dimcolor)
#### Average
    """
    pygame.gfxdraw.filled_circle(screen, (int)(avgx/numberofreplays), (int)(avgy/numberofreplays), 5, (255,255,255))
    for linenumber in range(1,taillength+1):
        if elapsedtime-linenumber>=0 and elapsedtime>len(replaylist[1].xyl)/1000:
            pygame.gfxdraw.line(screen, (int)(prevxy[elapsedtime-linenumber+1][0]/numberofreplays), (int)(prevxy[elapsedtime-linenumber+1][1]/numberofreplays), (int)(prevxy[elapsedtime-linenumber][0]/numberofreplays), (int)(prevxy[elapsedtime-linenumber][1]/numberofreplays), (255,255,255))
    """
    pygame.display.flip()
pygame.quit()
sys.exit()
