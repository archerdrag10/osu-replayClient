import sys
import urllib.parse
import urllib.request
import http.cookiejar
import re

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
    #print(str(data))
    startIndex = strData.index("beatmapListing")
    users = re.findall("/u/[0-9]+\\\\'>[A-Za-z0-9_ ]+", strData[startIndex:])
    replayURLs = re.findall('/web/osu-getreplay\.php\?c.[0-9]+\&m=0', strData)
    for i in range(0, numTopPlays):
        print("Downloading replay #" + str(i+1) + " (" + users[i][users[i].index(">")+1:] + ")")
        request = urllib.request.Request("https://osu.ppy.sh" + replayURLs[i])
        response = urllib.request.urlopen(request)
        with open("temp.b" + str(beatmapID) + "osr" + str(i+1) + ".osr", 'wb') as f:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                f.write(chunk)
def playbackReplays():
    print("Playing back...")

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
playbackReplays()
