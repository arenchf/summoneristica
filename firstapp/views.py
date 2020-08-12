from django.shortcuts import render
from django.http import HttpResponseNotFound
from . import models
from requests.utils import requote_uri
import requests
import json
from firstapp.secrets import *
# Create your views here.

BASE_URL_SUMMONER = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'
BASE_URL_MATCHLIST = 'https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}'
BASE_URL_PROFILEICON = 'http://raw.communitydragon.org/10.16/game/assets/ux/summonericons/profileicon{}.png'
BASE_URL_MATCH = 'https://{}.api.riotgames.com/lol/match/v4/matches/{}'

HEADER = {'X-Riot-Token': '{}'.format(RIOT_API_KEY)}


def home(request):
    return render(request, 'base.html')


def search_sum(request):
    summoner_name = request.POST.get('search_sum_input')
    server_input = request.POST.get('serverselector')
    # Showing witch server is the summoner on
    print('Getting {}\'s info on {} '.format(summoner_name, server_input))
    FINAL_URL_SUMMONER = BASE_URL_SUMMONER.format(
        server_input, requote_uri(summoner_name))
    print('SUMMONER FINAL URL: ', FINAL_URL_SUMMONER)
    print('HELLO GITHUB')
    r_summoner = json.loads(requests.get(
        FINAL_URL_SUMMONER, headers=HEADER).text)
    # print(r_summoner) prints all the summoner data as json
    if 'accountId' not in r_summoner:
        return render(request, 'firstapp/summonerNotFound.html')
    print('ACCOUNT ID: ', r_summoner['accountId'])

    FINAL_URL_MATCHLIST = BASE_URL_MATCHLIST.format(
        server_input, r_summoner['accountId'])
    r_matchlist = json.loads(requests.get(
        FINAL_URL_MATCHLIST, headers=HEADER).text)

    print('MATCHLIST FINAL URL: ', FINAL_URL_MATCHLIST)
    # print('MATCHLIST REQUEST \t', r_matchlist)

    profile_icon_img = BASE_URL_PROFILEICON.format(r_summoner['profileIconId'])

    summoner_data = {
        'summoner_name': summoner_name,
        'summoner_id': r_summoner['id'],
        'account_id': r_summoner['accountId'],
        'puu_id': r_summoner['puuid'],
        'profile_icon_id': r_summoner['profileIconId'],
        'profile_icon_img': profile_icon_img,
        'summoner_level': r_summoner['summonerLevel'],
        'match_data': r_matchlist,
        'summoner_server': server_input,
    }
    return render(request, 'firstapp/sumSearch.html', summoner_data)


def search_match(request):
    server = request.POST.get('search_match_input_summonerserver')
    accountid = request.POST.get('search_match_input_accountid')
    sicon = requests.get(
        'http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/summoner.json')

    summonericons = json.loads(sicon.text)

    FINAL_URL_MATCHLIST = BASE_URL_MATCHLIST.format(server, accountid)

    m = json.loads(requests.get(FINAL_URL_MATCHLIST, headers=HEADER).text)
    matchlist_matches = m['matches']
    matchlist_first_champion = matchlist_matches[0]['champion']
    matchlist_first_gameid = matchlist_matches[0]['gameId']

    championsInGame = []
    championresponse = requests.get(
        "http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json")
    chmapionRawData = json.loads(championresponse.text)
    championIdToName = {}

    for key, champion in chmapionRawData['data'].items():
        championIdToName[int(champion['key'])] = champion['name']

    summonerspells = {}
    for a in summonericons['data']:
        summonerspells[str(summonericons['data'][a]['key'])] = a

    spiel = requests.get(BASE_URL_MATCH.format(
        server, matchlist_first_gameid), headers=HEADER).json()

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
        left_bans.append(championIdToName[leftteam['bans'][x]['championId']])
        right_bans.append(championIdToName[rightteam['bans'][x]['championId']])

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


# m = requests.get(
#    "https://tr1.api.riotgames.com/lol/match/v4/matchlists/by-account/PRCqUXa1Iuy0Dm1qgF18EtD7re4_vWX06MMlWB3oJusWRmEI2tie8XXo", headers=HEADER)
