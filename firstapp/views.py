from django.shortcuts import render
from django.http import HttpResponseNotFound
from . import models
from .models import Summoner, Matchlist
from .models import Programmer
from .models import Deneme
from .models import Company

from requests.utils import requote_uri
import requests
import json
from firstapp.secrets import *
from datetime import datetime
# Create your views here.

CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

BASE_URL_SUMMONER = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'
#server accountid begin end queue champion
BASE_URL_MATCHLIST = 'https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?beginIndex={}&endIndex={}&queue={}&champion={}'
BASE_URL_PROFILEICON = 'http://raw.communitydragon.org/10.16/game/assets/ux/summonericons/profileicon{}.png'
BASE_URL_MATCH = 'https://{}.api.riotgames.com/lol/match/v4/matches/{}'
HEADER = {'X-Riot-Token': '{}'.format(RIOT_API_KEY)}


def home(request):
    data = {
        "title": "Homepage",
    }
    xd = Matchlist.objects.all().order_by('gameid')
    print(xd)
    return render(request, 'base.html', data)


def search_sum(request):
    print(CGREENBG + CBLACK+"##################  BEGINNING OF SEARCH SUMMONER  #########################"+CEND)
    summoner_name = request.POST.get('search_sum_input')  # SUMMONER NAME
    server_input = request.POST.get('serverselector')  # SERVER
    summoner = getSummonerWithSummonerName(summoner_name,server_input)
    if summoner == "SUMMONER NOT FOUND":
        return render(request,"firstapp/summonerNotFound.html")
    FINAL_PROFIL_ICON_URL = BASE_URL_PROFILEICON.format(summoner['profileIconId'])
    print(CBLACK+CGREENBG+"##################END OF SEARCH SUMMONER#########################"+CEND)

    data = {
        "title": summoner_name,
        'summoner_name': summoner_name,
        'summoner_id': summoner['id'],
        'account_id': summoner['accountId'],
        'puu_id': summoner['puuid'],
        'profile_icon_id': summoner['profileIconId'],
        'profile_icon_img': FINAL_PROFIL_ICON_URL,
        'summoner_level': summoner['summonerLevel'],
        'summoner_server': server_input,
    }
    
    return render(request, 'firstapp/sumSearch.html', data)

def getSummonerWithSummonerName(summonerName,server):
    FINAL_URL_SUMMONER = BASE_URL_SUMMONER.format(server,requote_uri(summonerName))
    summoner = json.loads(requests.get(FINAL_URL_SUMMONER, headers=HEADER).text)
    if 'accountId' not in summoner:
        return "SUMMONER NOT FOUND"

    s = Summoner.objects.filter(accountId=summoner['accountId'], server=server)
    if s.exists():#Look at the revision date and if its different change the data
        print("IT EXISTS")
        if s.get().revisionDate == summoner['revisionDate']:
            print("REVISION DATES ARE SAME")
        elif s.get().revisionDate != summoner['revisionDate']:
            s.get().revisionDate = summoner['revisionDate']
            s.get().summonerLevel = summoner['summonerLevel']
            s.get().summonerName = summoner['name']
            s.save()
    elif not s.exists():#create Summoner Object
        Summoner.objects.create(summonerName=summonerName,accountId=summoner['accountId'],summonerId=summoner['id'],puuid=summoner['puuid'],profileIconId=summoner['profileIconId'],revisionDate=summoner['revisionDate'],summonerLevel=summoner['summonerLevel'],server=server)
        print("ITS CREATED")

    ts = summoner['revisionDate'] / 1000
    dt_object = datetime.fromtimestamp(ts)

    return summoner

def getLastMatchIdWithAccountId(accountId,server):
    FINAL_URL_MATCHLIST = BASE_URL_MATCHLIST.format(server,accountId,0,"","","")
    m = json.loads(requests.get(FINAL_URL_MATCHLIST,headers=HEADER).text)
    if 'matches' not in m:
        return "NoMatch"

    lastmatchid = m['matches'][0]['gameId']
    return lastmatchid

def getMatchListWithAccountId(accountId, server,beginIndex="",queue=""):
    #server accountid begin end queue champion
    FINAL_URL_MATCHLIST = BASE_URL_MATCHLIST.format(server,accountId,beginIndex,"",queue,"")
    matchlist = json.loads(requests.get(FINAL_URL_MATCHLIST, headers=HEADER).text)

    if 'matches' not in matchlist:
        return "NoMatch"

    for x in matchlist['matches']:
        a = Matchlist.objects.filter(platformid=x['platformId'],gameid=x['gameId'])
        if not a.exists():
            Matchlist.objects.create(platformid=x['platformId'],gameid=x['gameId'],championid=x['champion'],queue=x['queue'],season=x['season'],timestamp=x['timestamp'],role=x['role'],lane=x['lane'])
            print("match created")
        elif a.exists():
            print("match exists")
    
    if matchlist["endIndex"] != matchlist['totalGames']:        
        if beginIndex=="":
            beginIndex=0
        beginIndex+=100    
        getMatchListWithAccountId(accountId,server,beginIndex)
    
    print(FINAL_URL_MATCHLIST)
    
    return matchlist

def matchlist(request):
    server = request.POST.get("matchlist_input_summonerserver")
    accountid = request.POST.get("matchlist_input_accountid")

    matchlist = getMatchListWithAccountId(accountId=accountid,server=server)
    if matchlist == "NoMatch":
        data={
            "title": "Summoner Search",
        }
        return render(request,"firstapp/matchNotFound.html",data)
    #matchlist = json.loads(requests.get(FINAL_URL_MATCHLIST, headers=HEADER).text)

    return render(request, 'firstapp/matchlist.html')


def search_match(request):
    server = request.POST.get('search_match_input_summonerserver')
    accountid = request.POST.get('search_match_input_accountid')

    sicon = requests.get(
        'http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/summoner.json')
    summonericons = json.loads(sicon.text)

    lastmatchid=getLastMatchIdWithAccountId(accountid,server)
    matchjson = matchInfosByMatchId(lastmatchid,server) 

    print(CRED + str(matchjson) + CEND)
    
    FINAL_URL_MATCHLIST = BASE_URL_MATCHLIST.format(server, accountid,"","","","")
    m = json.loads(requests.get(FINAL_URL_MATCHLIST, headers=HEADER).text)

    matchlist_matches = m['matches']
    matchlist_first_champion = matchlist_matches[0]['champion']
    matchlist_first_gameid = matchlist_matches[0]['gameId']
    print(matchlist_first_gameid)

    championsInGame = []
    championresponse = requests.get("http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json")
    championRawData = json.loads(championresponse.text)
    championIdToName = {}

    for key,champion in championRawData['data'].items():
        championIdToName[int(champion['key'])] = champion['name']

    summonerspells = {}
    for a in summonericons['data']:
        summonerspells[str(summonericons['data'][a]['key'])] = a

    spiel = requests.get(BASE_URL_MATCH.format(server, lastmatchid), headers=HEADER).json()
    spiel_length_min = (spiel['gameDuration']-spiel['gameDuration'] % 60) / 60
    spiel_length_sec = spiel['gameDuration'] % 60
    spiel_length = "{}:{}".format(int(spiel_length_min), spiel_length_sec)
    print('GAME LENGTH:', spiel_length)

    if spiel['teams'][0]['win'] == "Win":
        leftwins = True
    else:
        leftwins = False

    leftteam = spiel['teams'][0]
    rightteam = spiel['teams'][1]

    left_bans = []
    right_bans = []
    for x in range(5):
        if(leftteam['bans'][x]['championId'] == -1):
            left_bans.append("NoBan")
        else:
            left_bans.append(
                championIdToName[leftteam['bans'][x]['championId']])
        print("appended")
        if(rightteam['bans'][x]['championId'] == -1):
            right_bans.append("NoBan")
        else:
            right_bans.append(
                championIdToName[rightteam['bans'][x]['championId']])

    print("problem1")
    player = []
    for x in range(10):
        if spiel['participants'][x]['teamId'] == 100:
            killParticipation = (spiel['participants'][x]['stats']
                                 ['kills'] + spiel['participants'][x]['stats']['deaths'])
        player.append({
            'spell1url': summonerspells[str(spiel['participants'][x]['spell1Id'])],
            'spell2url': summonerspells[str(spiel['participants'][x]['spell2Id'])],
            'teamId': spiel['participants'][x]['teamId'],
            'championId': spiel['participants'][x]['championId'],
            'champLevel': spiel['participants'][x]['stats']['champLevel'],
            'item_0': spiel['participants'][x]['stats']['item0'],
            'item_1': spiel['participants'][x]['stats']['item1'],
            'item_2': spiel['participants'][x]['stats']['item2'],
            'item_3': spiel['participants'][x]['stats']['item3'],
            'item_4': spiel['participants'][x]['stats']['item4'],
            'item_5': spiel['participants'][x]['stats']['item5'],
            'item_6': spiel['participants'][x]['stats']['item6'],
            'summonerName': spiel['participantIdentities'][x]['player']['summonerName'],
            'kills': spiel['participants'][x]['stats']['kills'],
            'deaths': spiel['participants'][x]['stats']['deaths'],
            'assists': spiel['participants'][x]['stats']['assists'],
            'totalDamageDealt': spiel['participants'][x]['stats']['totalDamageDealt'],
            'goldEarned': spiel['participants'][x]['stats']['goldEarned'],
            'summonerName': spiel['participantIdentities'][x]['player']['summonerName'],
            'killParticipation': killParticipation,
        })
        print(player[x])

    player1 = {
        'spell1url': summonerspells[str(spiel['participants'][0]['spell1Id'])],
        'spell2url': summonerspells[str(spiel['participants'][0]['spell2Id'])],
        'teamId': spiel['participants'][0]['teamId'],
        'championId': spiel['participants'][0]['championId'],
        'champLevel': spiel['participants'][0]['stats']['champLevel'],
        'item_0': spiel['participants'][0]['stats']['item0'],
        'item_6': spiel['participants'][0]['stats']['item6'],
        'summonerName': spiel['participantIdentities'][0]['player']['summonerName'],

    }
    player2 = {

    }
    player3 = {}
    player4 = {}
    player5 = {}
    player6 = {}
    player7 = {}
    player8 = {}
    player9 = {}
    playerinfo = {
        'p1': player1,
        'p2': player2,
        'p3': player3,
        'p4': player4,
        'p5': player5,
        'p6': player6,
        'p7': player7,
        'p8': player8,
        'p9': player9,

    }

    spieler0infos = {
        'spell_id1': spiel['participants'][0]['spell1Id'],
        'spell_id2': spiel['participants'][0]['spell2Id'],
        'item0': spiel['participants'][0]['stats']['item0'],
        'item1': spiel['participants'][0]['stats']['item1'],
        'item2': spiel['participants'][0]['stats']['item2'],
        'item3': spiel['participants'][0]['stats']['item3'],
        'item4': spiel['participants'][0]['stats']['item4'],
        'item5': spiel['participants'][0]['stats']['item5'],
        'item6': spiel['participants'][0]['stats']['item6'],
        'kills': spiel['participants'][0]['stats']['kills'],
        'deaths': spiel['participants'][0]['stats']['deaths'],
        'assists': spiel['participants'][0]['stats']['assists'],
        'totalDamageDealt': spiel['participants'][0]['stats']['totalDamageDealt'],
        'goldEarned': spiel['participants'][0]['stats']['goldEarned'],
        'summonerName': spiel['participantIdentities'][0]['player']['summonerName'],
    }

    left_total_kda = {
        'kills': 0,
        'deaths': 0,
        'assists': 0,
    }
    right_total_kda = {
        'kills': 0,
        'deaths': 0,
        'assists': 0,
    }

    for x in range(5):
        left_total_kda['kills'] += spiel['participants'][x]['stats']['kills']
        left_total_kda['deaths'] += spiel['participants'][x]['stats']['deaths']
        left_total_kda['assists'] += spiel['participants'][x]['stats']['assists']
        right_total_kda['kills'] += spiel['participants'][x +
                                                          5]['stats']['kills']
        right_total_kda['deaths'] += spiel['participants'][x +
                                                           5]['stats']['deaths']
        right_total_kda['assists'] += spiel['participants'][x +
                                                            5]['stats']['assists']

    print(left_total_kda)
    print(right_total_kda)

    spielinfos = {

        'playerinfo': playerinfo,
        'left_total_kda': left_total_kda,
        'right_total_kda': right_total_kda,
        'spieler0': spieler0infos,
        'left_first_blood': leftteam['firstBlood'],
        'right_first_blood': rightteam['firstBlood'],
        'left_first_baron': leftteam['firstBaron'],
        'right_first_baron': rightteam['firstBaron'],
        'left_first_tower': leftteam['firstTower'],
        'right_first_tower': rightteam['firstTower'],
        'left_first_inhib': leftteam['firstInhibitor'],
        'right_first_inhib': rightteam['firstInhibitor'],
        'left_first_dragon': leftteam['firstDragon'],
        'right_first_dragon': rightteam['firstDragon'],
        'left_first_rift': leftteam['firstRiftHerald'],
        'right_first_rift': rightteam['firstRiftHerald'],
        'left_tower_kills': leftteam['towerKills'],
        'left_inhib_kills': leftteam['inhibitorKills'],
        'left_baron_kills': leftteam['baronKills'],
        'left_dragon_kills': leftteam['dragonKills'],
        'left_rift_kills': leftteam['riftHeraldKills'],
        'left_bans': left_bans,
        # 'left_bans': leftteam['bans'],
        'right_tower_kills': rightteam['towerKills'],
        'right_bans': right_bans,
        # 'right_bans': rightteam['bans'],
        'right_inhib_kills': rightteam['inhibitorKills'],
        'right_baron_kills': rightteam['baronKills'],
        'right_dragon_kills': rightteam['dragonKills'],
        'right_rift_kills': rightteam['riftHeraldKills'],
    }

    print(spielinfos['left_first_baron'])
    print(spiel['teams'][0]['bans'])
    print(spielinfos)

    mychamp = championIdToName[matchlist_first_champion]
    for x in range(10):
        if championIdToName[spiel['participants'][x]['championId']] == 'Master Yi':
            championsInGame.append('MasterYi')
        elif championIdToName[spiel['participants'][x]['championId']] == 'Kha\'Zix':
            championsInGame.append('Khazix')
        elif championIdToName[spiel['participants'][x]['championId']] == 'Jarvan IV':
            championsInGame.append('JarvanIV')
        elif championIdToName[spiel['participants'][x]['championId']] == 'Lillia':
            championsInGame.append('Lillia')
        elif championIdToName[spiel['participants'][x]['championId']] == 'Kai\'Sa':
            championsInGame.append('Kaisa')
        else:
            championsInGame.append(
                championIdToName[spiel['participants'][x]['championId']])

    teamloop = []
    for tl in range(5):
        teamloop.append(championsInGame[(tl)])
        teamloop.append(championsInGame[(tl+5)])
        print(teamloop)

    print(spiel)

    content = {
        'title': "Last Match",
        'summonerspells': summonerspells,
        'spielinfos': spielinfos,
        'leftwins': leftwins,
        'spielLength': spiel_length,
        'matches': matchlist_matches,
        'champion': mychamp,
        'accountid': accountid,
        'gameid': matchlist_first_gameid,
        'championName': championsInGame,
        'teamloopChampionName': teamloop,
    }

    return render(request, 'firstapp/searchMatch.html', content)

def matchInfosByMatchId(matchId,server):
    FINAL_URL_MATCH = BASE_URL_MATCH.format(server,matchId)
    match = json.loads(requests.get(FINAL_URL_MATCH, headers=HEADER).text)

    gameLengthMin = (match['gameDuration']-match['gameDuration']%60) / 60
    gameLengthSec = match['gameDuration'] % 60
    gameLength = {
        "minutes": int(gameLengthMin),
        "seconds": gameLengthSec,
    }

    print("GAME LENGTH: {}:{}".format(int(gameLength['minutes']),gameLength['seconds']))

    if match["teams"][0]["win"] == "Win":#IF TEAM ID 100 WINS # BLUE TEAM
        bluewins = True
        redwins = False
    elif match['teams'][1]["win"]=="Win":#IF TEAM ID 200 WINS # RED TEAM
        redwins = True
        bluewins = False
    else:
        remake = True





    return match
