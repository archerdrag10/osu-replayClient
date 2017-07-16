import sys
import urllib.parse
import urllib.request
import http.cookiejar
import re
import lzma
import zipfile
import glob
import pygame
import pygame.gfxdraw

replays=[]

def decodeULEB128(f):
    retstring=""
    bitstring=list("0000000")
    total = 0
    while(retstring=="" or int.from_bytes(byte, 'little')>=128):
        byte=f.read(1)
        for i in range(0,7):
            if(int.from_bytes(byte, 'little')&2**i):
                bitstring[len(bitstring)-1-i]='1'
        retstring="".join(bitstring)+retstring
    return int(retstring, 2)

def readString(f):
    stringexists = int.from_bytes(f.read(1), 'little')==11
    bytelength=decodeULEB128(f) if stringexists else 0
    return f.read(bytelength).decode("utf-8") if stringexists else ""

class replayInstance:
    def __init__(self, filename, username):
        self.modlist=[]
        self.timedatalist=[]
        self.cursordatalist=[]
        self.keydatalist=[]
        
        print("Unpacking replay for " + username + ".")
        
        with open(filename, "rb") as f:
            self.gamemode=int.from_bytes(f.read(1), 'little')
            self.gameversion=int.from_bytes(f.read(4), 'little')
            self.beatmapmd5=readString(f)
            self.playername=readString(f)
            self.replaymd5=readString(f)
            self.numberof300s=int.from_bytes(f.read(2), 'little')
            self.numberof100s=int.from_bytes(f.read(2), 'little')
            self.numberof50s=int.from_bytes(f.read(2), 'little')
            self.numberofgekis=int.from_bytes(f.read(2), 'little')
            self.numberofkatus=int.from_bytes(f.read(2), 'little')
            self.numberofmisses=int.from_bytes(f.read(2), 'little')
            self.totalscore=int.from_bytes(f.read(4), 'little')
            self.greatestcombo=int.from_bytes(f.read(2), 'little')
            self.ss=int.from_bytes(f.read(1), 'little')
            modsused=int.from_bytes(f.read(4), 'little')
            self.lifebargraph=readString(f)
            self.timestamp=int.from_bytes(f.read(8), 'little')
            self.bytelengthofreplaydata=int.from_bytes(f.read(4), 'little')
            replaydata=lzma.decompress(f.read(self.bytelengthofreplaydata)).decode().split(',')

        if self.gamemode == 0:
            ###also what if mod number is greater than 32765
            if modsused>=16384:
                self.modlist.append("PF")
                modsused-=16384
            if modsused>=4096:
                self.modlist.append("SO")
                modsused-=4096
            if modsused>=1024:
                self.modlist.append("FL")
                modsused-=1024
            if modsused>=576:
                self.modlist.append("NC")
                modsused-=576
            if modsused>=256:
                self.modlist.append("HT")
                modsused-=256
            if modsused>=64:
                self.modlist.append("DT")
                modsused-=64
            if modsused>=32:
                self.modlist.append("SD")
                modsused-=32
            if modsused>=16:
                self.modlist.append("HR")
                modsused-=16
            if modsused>=8:
                self.modlist.append("HD")
                modsused-=8
            if modsused>=2:
                self.modlist.append("EZ")
                modsused-=2
            if modsused>=1:
                self.modlist.append("NF")
                modsused-=1
        for event in replaydata:
            splitdata = event.split('|')
            if int(splitdata[0]) == -12345 or int(splitdata[3]) > 36:
                    break
            self.timedatalist.append(int(splitdata[0]))
            self.cursordatalist.append((float(splitdata[1]), float(splitdata[2])))
            self.keydatalist.append(int(splitdata[3]))

def loadLocalReplays(beatmapID):
    print("Looking for local replays with beatmap ID " + str(beatmapID) + "...")
    
def getTopReplays(username, password, beatmapID, numTopPlays):
    print("Logging into osu.ppy.sh as " + username)
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    urllib.request.install_opener(opener)
    payload = urllib.parse.urlencode({"username": username,
                                      "password": password,
                                      "redirect": "index.php",
                                      "sid": "",
                                      "login": "Login"}).encode("utf-8")
    request = urllib.request.Request("https://osu.ppy.sh/forum/ucp.php?mode=login", payload)
    response = urllib.request.urlopen(request)
    request = urllib.request.Request("https://osu.ppy.sh/b/" + str(beatmapID) + "&m=0")
    response = urllib.request.urlopen(request)
    strData = str(response.read())
    startIndex = strData.index("beatmapDownloadButton")
    dlext = re.findall("/d/[0-9]+", strData[startIndex:])
    request = urllib.request.Request("https://osu.ppy.sh" + dlext[0])
    response = urllib.request.urlopen(request)
    filename = "temp.b" + str(beatmapID) + ".osz"
    with open(filename, 'wb') as f:
        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            f.write(chunk)
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall("temp.b" + str(beatmapID) + "unzip")
    zip_ref.close()

    mp3Path = glob.glob("temp.b" + str(beatmapID) + "unzip/*.mp3")[0]
    file = open(mp3Path, "rb")
    byte = file.read(500)
    binary = str(bin(int.from_bytes(byte, 'big')))[2:].zfill(4000)
    try:
        s=re.search("111111111111", binary).start()
    except:
        print("Cannot read from mp3 file. Exiting...")
        exit
    rate_bits=binary[s+20:s+22]
    if rate_bits == "00":
        sampling_rate=44100
    elif rate_bits == "01":
        sampling_rate=48000
    elif rate_bits == "10":
        sampling_rate=32000
    elif rate_bits == "11":
        print("Cannot read from mp3 file. Exiting...")
        exit

    startIndex = strData.index("beatmapListing")
    users = re.findall("/u/[0-9]+\\\\'>[A-Za-z0-9_ ]+", strData[startIndex:])
    replayURLs = re.findall('/web/osu-getreplay\.php\?c.[0-9]+\&m=0', strData)
    for i in range(0, numTopPlays):
        filename = "temp.b" + str(beatmapID) + "osr" + str(i+1) + ".osr"
        username = users[i][users[i].index(">")+1:]
        print("Downloading replay #" + str(i+1) + " (" + username + ")")
        request = urllib.request.Request("https://osu.ppy.sh" + replayURLs[i])
        response = urllib.request.urlopen(request)
        with open(filename, 'wb') as f:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                f.write(chunk)
        replays.append(replayInstance(filename, username))

beatmapID = sys.maxsize
while beatmapID < 1 or beatmapID > 2000000:
    tempinput = input("Which beatmap ID do you want to watch? ")
    beatmapID = int(tempinput) if tempinput.isdigit() else -1
whichplays = sys.maxsize
print(" 1 - Only top plays\n 2 - Top plays and local plays\n 3 - Only local plays")
while whichplays < 1 or whichplays > 3:
    tempinput = input("What type of replays do you want to view? ")
    whichplays = int(tempinput) if tempinput.isdigit() else -1
if whichplays == 1 or whichplays == 2:
    username = input("Username for osu.ppy.sh: ")
    password = input("Password for osu.ppy.sh: ")
    numTopPlays = sys.maxsize
    while numTopPlays < 1 or numTopPlays > 50:
        tempinput = input("How many top plays do you want to see? ")
        numTopPlays = int(tempinput) if tempinput.isdigit() else -1
    getTopReplays(username, password, beatmapID, numTopPlays)
if whichplays == 2 or whichplays == 3:
    loadLocalReplays(beatmapID)

print("Playing back...")
WIDTH=1366
HEIGHT=768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.mixer.init(44100)
pygame.mixer.music.load(glob.glob("temp.b" + str(beatmapID) + "unzip/*.mp3")[0])
pygame.mixer.music.set_volume(0.3)
pygame.display.set_caption('o!rc: %s'  % (str(beatmapID)))
clock = pygame.time.Clock()
background=pygame.image.load(glob.glob("temp.b" + str(beatmapID) + "unzip/*.jpg")[0])
darkoverlay = pygame.Surface(background.get_size()).convert_alpha()
darkoverlay.fill((0, 0, 0, 235))
background.blit(darkoverlay, (0, 0))
elapsedtime=0
taillength=50
pygame.mixer.music.play()
while True:
    elapsedtime += clock.tick_busy_loop()
    screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
    pygame.gfxdraw.aacircle(screen, int(elapsedtime/1000), 50, 5, (255,255,255))
    pygame.gfxdraw.filled_circle(screen, int(elapsedtime/1000), 50, 5, (255,255,255))
    #if not pygame.mixer.get_busy():
    #    pygame.mixer.music.play()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
            #pygame.display.set_caption('o!rc taillength=%d' % (taillength))
    pygame.display.flip()
