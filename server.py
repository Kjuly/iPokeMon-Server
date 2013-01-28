from bottle import Bottle, run, request, response
import redis
from hashlib import md5
import time
import config

server = Bottle()
RADIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB   = 8

# Request Header
class Header(object):
    def __init__(self, headers):
        self.headers = headers

    # Make sure the request is sent via App
    def auth(self):
        if self.headers.get('key') == config.PM_CLIENT_REQUEST_KEY:
            return True
        else:
            return False

    # Get <provider>
    def get_provider(self):
        return self.headers.get('provider')

    # Get <identity>
    def get_identity(self):
        return self.headers.get('identity')


# <xxx>  : Basic
# <!xxx!>: Encrypted

# OpenID for users
# openid:<userid> => A set of <provider> that the user has activated
# 
# <provider>:<!identity!> => <userID>
class OpenID(object):
    def __init__(self, p_provider, p_identity):
        self.redis    = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
        self.provider = p_provider
        self.identity = p_identity

    # The user has no OpenID added before, so add new, and return the new <userid>
    def add(self):
        # Get the new user's ID
        userid = self.redis.incr("global:nextUserid")
        # If add new openID successed(it's value is <userid>),
        # then add new user
        if self.redis.setnx("%s:%s" % (self.provider, md5(self.identity).hexdigest()), userid):
            self.redis.sadd("openid:%s" % userid, self.provider)
            #self.redis.setnx('u:%s:p'   % userid, 0) # UsersPokemonsID
            if User(userid).add(
                    "Trainer%s" % userid, # Name
                    time.time(),          # Time started
                    1000,                 # Money
                    "0,0,0",              # Badges
                    "",                   # Six Pokemons
                    "0",                   # Pokedex
                    0,                    # Number of Pokemons
                    "0:1,300,2,300,3,300,9,300,13,300,19,300,22,300:23,300,6,300,15,300:4,300,7,300,16,300:1,300:0:0:0:0"   # Bag
                    ):
                return userid
        else:
            return 0

    # The user has one or several OpenIDs, add one more OpenID for user
    def add_to_user(self):
        if self.redis.setnx("%s:%s" % (self.provider, md5(self.identity).hexdigest()), self.userid):
            return True
        else:
            return False

    # Remove an OpenID from the user
    def rm_from_user(self):
        if self.redis.delete("%s:%s" % (self.provider, md5(self.identity).hexdigest())):
            return True
        else:
            return False

    # After authenticated, return the authorized user's <userid>
    def authorized_user(self):
        return self.redis.get("%s:%s" % (self.provider, md5(self.identity).hexdigest()))

    # Authenticate the user by <provider> & <identity>
    def authenticate(self):
        return self.redis.get("%s:%s" % (self.provider, md5(self.identity).hexdigest()))
        #if self.redis.sismember("%s:%s" % (self.provider, md5(self.identity).hexdigest()), userid):
        #    return True
        #else:
        #    return False

# User
# users: a set of <userid>
#
# u: User
# u:<userID> => {
#       "id"          : <userid>,       # Number
#       "name"        : <username>,     # String
#       "timeStarted" : <timeStarted>,  # Date
#       "money"       : <money>,        # Number
#       "badges"      : <badges>,       # 
#       "sixPokemons" : <sixPokemons>,  # String e.g. "1,2,3,4,5,6"
#       "pokedex"     : <pokedex>,      # String e.g. "101111100..."
#       "pokemons"    : <pokemons>,     # Number e.g. 6
#       "bag"         : <bag>           # String
#       }
#       
#  AS:
#       <bag>: <bagItems>:<bagMedicineStatus>:<bagMedicineHP>:<bagMedicinePP>
#              :<bagPokeballs>:<bagTMsHMs>:<bagBerries>:<bagBattleItems>:<bagKeyItems>
#     & <bagItems>, <...>: "1,2,3,..."
#  SO:
#       <bag>: "1,2,3:1,2,3:...:1,2,3"                                              
class User(object):
    def __init__(self, p_user_id):
        self.redis  = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
        self.userid = p_user_id

    # Get all data for a user with <userid>
    def get(self):
        #return self.redis.hget("u:%s" % userid, "name")
        return self.redis.hgetall("u:%s" % self.userid)

    # If unique, return True
    def check_name_uniqueness(self, p_username):
        p_username = (p_username).lower()
        print(p_username)
        # if name exists, check whether it is belong to current user
        print(self.redis.smembers("usernames"))
        if self.redis.sismember("usernames", p_username):
            # if this name belong to current user, treat it as unique
            username = self.redis.hget("u:%s" % self.userid, "name")
            if (username).lower() == p_username:
                return True
            # otherwise, name is not unique
            else:
                return False
        # not exists, this name is unique, try to set new for usre
        # if succeed, return True
        # else, return False
        else:
            if self.redis.sadd("usernames", (p_username).lower()):
                original_username = self.redis.hget("u:%s" % self.userid, "name")
                self.redis.srem("usernames", (original_username).lower())
                return True
            else:
                return False

    # Update data for user
    def update(self, p_userdata):
        #if self.redis.sismember("u:%s" % self.userid):
        if self.redis.sismember("users", self.userid):
            self.redis.hmset("u:%s" % self.userid, p_userdata)
            return True
        else:
            return False

    
    # Add new user
    def add(self, p_username, p_timeStarted, p_money, p_badges,
            p_sixPokemons, p_pokedex, p_pokemons, p_bag):
        # If add user successed, i.e. <userid> does not exist in <users> set
        if self.redis.sadd("users", self.userid):
            self.redis.sadd("usernames", (p_username).lower())
            print(self.redis.smembers('usernames'))
            #self.redis.hset("u:%s" % self.userid, "name",    p_username)
            #self.redis.hset("u:%s" % self.userid, "pokedex", p_pokedex)
            self.redis.hmset("u:%s" % self.userid, {
                "id":          self.userid,
                "name":        p_username,
                "timeStarted": p_timeStarted,
                "money":       p_money,
                "badges":      p_badges,
                "sixPokemons": p_sixPokemons,
                "pokedex":     p_pokedex,
                "pokemons":    p_pokemons,
                "bag":         p_bag
                })
            return True
        else:
            return False


# Tamed Pokemon
# pokedex:<userid> => a set of <pokemon_uid>,
#                     which belong to the user with <userid>.
#
# pm: PokeMon
# pm:<uid> => {
#       "uid":         <uid>,         # Number. Pokemon's Unique ID
#       "sid":         <sid>,         # Number. Pokemon's Pokedex Number ID
#       "box":         <box>,         # Number.
#       "status":      <status>,      # Number.
#       "gender":      <gender>,      # Number.
#       "happiness":   <happiness>,   # Number.
#       "level":       <level>,       # Number.
#       "fourMoves":   <fourMoves>,   # String. e.g. "1,2,3,4"
#       "maxStats":    <maxStats>,    # String. e.g. "30,30,30,30,30,30"
#       "currHP":      <currHP>,      # Number.
#       "currEXP":     <currEXP>,     # Number.
#       "toNextLevel": <toNextLevel>, # Number.
#       "memo":        <memo>         # String. e.g. "It is caught at ZJUT."
#       }
class Pokemon(object):
    def __init__(self, p_userid):
        self.redis  = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
        self.userid = p_userid

    # Get a dict data for a Pokemon
    def get_one(self, p_pokemon_uid):
        return self.redis.hgetall("pm:%s:%s" % (self.userid, p_pokemon_uid))

    # Get add data for a user's six Pokemon
    def get_six(self):
        six_pokemons = self.redis.hget("u:%s" % self.userid, "sixPokemons")
        if not six_pokemons:
            return
        import ast
        six_pokemons = ast.literal_eval(six_pokemons)
        if type(six_pokemons) is int:
            return six_pokemons
        pokemons = []
        for pokemon_uid in six_pokemons:
            pokemons.append(self.redis.hgetall("pm:%s:%s" % (self.userid, pokemon_uid)))
        return pokemons


    # Get all data for a user's Pokedex
    def get_all(self):
        pokedex = self.redis.smembers("pokedex:%s" % self.userid)
        if len(pokedex) == 0:
            return
        pokemons = []
        for pokemon_uid in pokedex:
            pokemons.append(self.redis.hgetall("pm:%s:%s" % (self.userid, pokemon_uid)))
        return pokemons

    # Update one Pokemon data
    def update_one(self, p_pokemon_uid, p_pokemon_data):
        if self.redis.sismember("pokedex:%s" % self.userid, p_pokemon_uid):
            self.redis.hmset(
                    "pm:%s:%s" % (self.userid, p_pokemon_uid), # Hash Key
                    p_pokemon_data                           # Mapping
                    )
        else:
            self.add(p_pokemon_uid, p_pokemon_data)
        return True

    # Add new tamed Pokemon
    def add(self, p_pokemon_uid, p_pokemon_data):
        if self.redis.sadd("pokedex:%s" % self.userid, p_pokemon_uid):
            #pokemon_uid = self.redis.incr("u:%s" % self.userid, "pokemons")
            #pokemon_uid = self.redis.incr("u:%s:p" % self.userid)
            self.redis.hmset("pm:%s:%s" % (self.userid, p_pokemon_uid), p_pokemon_data)
            return True
        else:
            return False

# Region
class Region(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # get current region
    #
    # API: /r
    # P_code: code for key
    #
    # <code> format = <cc>:<ca>:<cl>
    #   <cc> : code country
    #   <ca> : code administrative area
    #   <cl> : code locality 
    # ##<csl>: code sub-locality next version##
    #
    # e.g.
    #   "CN:ZJ:HZ"
    # 
    # key format = re:<code> e.g.:
    #   "re:CN:ZJ:HZ"
    # if key not exists, return NULL
    #
    # return value e.g.:
    #   "CN:ZJ:HZ=Zhejiang Province=Hangzhou City"
    #   
    def get_with(self, p_code):
        return self.redis.get("re:%s" % p_code)

    # add new region info (will not add same data)
    # wait admin to modify & add to db
    #
    # API: /ur
    # p_ri: region info
    #
    # key e.g.: 'nre:CN'
    #
    # values e.g.:
    #   (
    #     "CN=Zhejiang Province=Hangzhou City", ###=<csl>
    #     "CN=Zhejiang Province=Ningbo City",
    #     .
    #   )
    def add_new(self, p_ri):
        # p_ri[:2] = 'CN'
        # p_ri e.g.: 'CN=Zhejaing Province=Hangzhou City'
        if self.redis.sadd("nre:%s" % p_ri[:2], p_ri):
            print('-1- add new Region Info - %s' % p_ri)
        else:
            print('-0- cannot add new Region Info - %s' % p_ri)


# Wild Pokemon
class WildPokemon(object):
    def __init__(self):
        self.redis = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)

    # args:
    #   p_rps: request.params
    #
    # tails: [
    #   CN,         # country code
    #   CN:ZJ,      # administrative area
    #   CN:ZJ:HZ,   # city (locality)
    #   CN:ZJ:HZ:X, # special points in city
    #   ...
    #   ]
    def get_SIDs(self, p_rps):
        SIDs = []
        for tail in self.generate_tails(p_rps):
            key = 'wpm:%s' % tail
            if self.redis.exists(key):
                SIDs.append(self.redis.get(key))
            else:
                SIDs.append(self.redis.get('wpm:DEFAULT'))
        return ','.join(SIDs)

    # filter request params, generate |tails|, which will used in |get_SIDs()|
    # rps: request params
    #
    # |codes| value format: [<0>,<1>,<2>,<3>,<4>]
    #   <0>=<country>:                      China (CN)
    #   <1>=<administrativeArea(province)>: Zhejiang Province (ZJ)
    #   <2>=<locality(city)>:               Hangzhou City (HZ)
    #   <3>=<sublocality(district)>:        (Space Holder) Yuhang District (YH)
    #   <4>=<special>:                      water, cave
    # |codes| value e.g.:
    #   ['CN', 'ZJ', 'HZ', 'XX', 'XX']
    #
    # |tails| value format: [<0>,<1>,<2>,<3>,<4>]
    #   <0>=codes[0]
    #   <1>=codes[0]:codes[1]
    #   <2>=codes[0]:codes[1]:codes[2]
    #   <3>=codes[0]:codes[1]:codes[2]:codes[3]
    #   <4>=codes[0]:codes[1]:codes[2]:codes[3]:codes[4]
    # |tails| value e.g.:
    #   ['CN', 'CN:ZJ', 'CN:ZJ:HZ', 'CN:ZJ:HZ:XX', 'CN:ZJ:HZ:XX:X']
    #
    def generate_tails(self, p_rps):
        tails = []
        codes = p_rps.get('code').split(':')
        print('CODES:%s' % codes)
        if not codes:
            return
        # init |tails| with |codes[0]|
        # so, |tails[0] == codes[0]|, e.g. 'CN'
        tails.append(codes[0])
        i = 0
        codes_length = len(codes)
        while True:
            i += 1
            if i >= codes_length:
                break
            # add new value to |tails|
            tails.append('%s:%s' % (tails[i-1], codes[i]))
        print('TAILS:%s', tails)
        return tails

    # collect location info for all the world
    def collect_location_info(self):
        pass


#
# RESTs
#
@server.route('/')
def index():
    r = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
    r.setnx('global:nextUserid', 0)
    return 'PMService is Running'

# For Debug
@server.route('/debug')
def debug():
    r = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
    output = '<html>'
    # USER
    userids = r.smembers("users")
    output += 'USERs:</br>'
    for userid in userids:
        user = User(userid).get()
        chart = '<tr>#ID:'          + user['id']          + ' </tr>' \
                '<tr>_Name:'        + user['name']        + ' </tr>' \
                '<tr>_TimeStarted:' + user['timeStarted'] + ' </tr>' \
                '<tr>_Money:'       + user['money']       + ' </tr>' \
                '<tr>_Badges:'      + user['badges']      + ' </tr>' \
                '<tr>_SixPokemons:' + user['sixPokemons'] + ' </tr>' \
                '<tr>_Pokedex:'     + user['pokedex']     + ' </tr>' \
                '<tr>_Pokemons:'    + user['pokemons']    + ' </tr>' \
                '<tr>_Bag:'         + user['bag']         + ' </tr>' \
                '</br>'
        output += chart

        # USER's POKEMON
        pokemon = Pokemon(userid)
        output += '</br>USER:' + userid + ' - SIXPOKEMONs:</br>'
        sixpokemons = pokemon.get_six()
        if type(sixpokemons) is list:
            for p in sixpokemons:
                chart = '<tr>#UID:'        + str(p['uid'])         + ' </tr>' \
                        '<tr>_SID:'        + str(p['sid'])         + ' </tr>' \
                        '<tr>_box:'        + str(p['box'])         + ' </tr>' \
                        '<tr>_status:'     + str(p['status'])      + ' </tr>' \
                        '<tr>_gender:'     + str(p['gender'])      + ' </tr>' \
                        '<tr>_happiness:'  + str(p['happiness'])   + ' </tr>' \
                        '<tr>_level:'      + str(p['level'])       + ' </tr>' \
                        '<tr>_fourMoves:'  + p['fourMoves']        + ' </tr>' \
                        '<tr>_maxStats:'   + p['maxStats']         + ' </tr>' \
                        '<tr>_HP:'         + str(p['hp'])          + ' </tr>' \
                        '<tr>_EXP:'        + str(p['exp'])         + ' </tr>' \
                        '<tr>toNextLevel:' + str(p['toNextLevel']) + ' </tr>' \
                        '<tr>memo:'        + p['memo']             + ' </tr>' \
                        '</br>'
                output += chart

        # USER's POKEDEX
        output += '</br>USER:' + userid + ' - POKEDEX:</br>'
        pokedex = pokemon.get_all()
        if type(pokedex) is list:
            for p in pokedex:
                chart = '<tr>#UID:'        + str(p['uid'])         + ' </tr>' \
                        '<tr>_SID:'        + str(p['sid'])         + ' </tr>' \
                        '<tr>_box:'        + str(p['box'])         + ' </tr>' \
                        '<tr>_status:'     + str(p['status'])      + ' </tr>' \
                        '<tr>_gender:'     + str(p['gender'])      + ' </tr>' \
                        '<tr>_happiness:'  + str(p['happiness'])   + ' </tr>' \
                        '<tr>_level:'      + str(p['level'])       + ' </tr>' \
                        '<tr>_fourMoves:'  + p['fourMoves']        + ' </tr>' \
                        '<tr>_maxStats:'   + p['maxStats']         + ' </tr>' \
                        '<tr>_HP:'         + str(p['hp'])          + ' </tr>' \
                        '<tr>_EXP:'        + str(p['exp'])         + ' </tr>' \
                        '<tr>toNextLevel:' + str(p['toNextLevel']) + ' </tr>' \
                        '<tr>memo:'        + p['memo']             + ' </tr>' \
                        '</br>'
                output += chart
    output += '</html>'
    return output

# Connection checking - GET feedback
# cc: Check Connection from client to server
@server.get('/cc')
def check_connection():
    header = Header(request.headers)
    if not header.auth():
        return False
    return {'v':1}

#
# User Section
#
# User - GET <userid>, if valid, return user's id
@server.get('/id')
def get_userid():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    userid = None
    # If authenticated, get the <userid>
    if openID.authenticate():
        userid = openID.authorized_user()
    # Else, add a new OpenID for a new user
    else:
        userid = openID.add()
    return {'userID':userid}

# User - GET if valid, return user's data
# u: User
@server.get('/u')
def get_user():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    userid = None
    # If authenticated, get the <userid>
    if openID.authenticate():
        userid = openID.authorized_user()
    # Else, add a new OpenID for a new user
    else:
        userid = openID.add()
    # Return user data if the <userid> is valid
    if userid:
        return User(userid).get()
    else:
        return False

# User - POST with <name>, check uniqueness for it
# cu: Check Uniqueness
@server.post('/cu')
def get_user():
    header = Header(request.headers)
    if not header.auth():
        return {'u':-1}
    openID = OpenID(header.get_provider(), header.get_identity())
    userid = None
    # If authenticated, get the <userid>
    if openID.authenticate():
        userid = openID.authorized_user()
    # Else, add a new OpenID for a new user
    else:
        userid = openID.add()
    # Return result whether <name> is unique
    uniqueness = -1
    if userid:
        # If ture, means exist, return 0
        if User(userid).check_name_uniqueness(request.params.get("name")):
            uniqueness = 1
        else:
            uniqueness = 0
    else:
        uniqueness = -1
    return {'u':uniqueness}

# User - POST Data
# uu: Update User
@server.post('/uu')
def update_user():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    # If authenticated, update user data
    if openID.authenticate():
        data = request.params
        userdata = {}
        for key in data.keys():
            userdata[key] = data.get(key)
        if User(openID.authorized_user()).update(userdata):
            return {'v':1}
    return {'v':0}


# User - GET Pokemon
# pm: PokeMon
@server.get('/pm/<pokemon_uid:int>')
def user_pokemon(pokemon_uid):
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    if openID.authenticate():
        return Pokemon(openID.authorized_user()).get_one(pokemon_uid)

# User - GET Six Pokemons
# 6pm: Six PokeMons
@server.get('/6pm')
def user_sixpokemons():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    if openID.authenticate():
        return {"sixPokemons":Pokemon(openID.authorized_user()).get_six()}

# User - GET Pokedex
# pd: PokeDex
@server.get('/pd')
def user_pokedex():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    if openID.authenticate():
        return {"pd":Pokemon(openID.authorized_user()).get_all()}

# User - POST Pokemon
# upm: Update PokeMon
@server.post('/upm')
def user_pokemon():
    header = Header(request.headers)
    if not header.auth():
        return False
    openID = OpenID(header.get_provider(), header.get_identity())
    if openID.authenticate():
        data = request.params
        pokemon_data = {}
        for key in data.keys():
            pokemon_data[key] = data.get(key)
        Pokemon(openID.authorized_user()).update_one(pokemon_data["uid"], pokemon_data)
    else:
        return False

#
# Region Section
#
# Region - GET regions for user's current location
# r:Region
# <code>=<cc>:<ca>:<cl> e.g. 'CN:ZJ:HZ'
#  ### next version: <cc>:<ca>:<cl>:<csl>
#
# <cc>:  code country
# <ca>:  code administrative area
# <cl>:  code locality
# ###<csl>: code sub-locality
@server.get('/r/<code>')
def get_region(code):
    # just auth whether it is sent from App Client
    #   no need to auth the user
    if not Header(request.headers).auth():
        return False
    return {"r":Region().get_with(code)}

# Region - POST update new regions
# ur:Update Region
@server.post('/ur')
def update_region():
    if not Header(request.headers).auth():
        return False
    # ri: region info
    # e.g. 'CN:ZJ:HZ'
    ri = request.params.get('ri')
    if ri: Region().add_new(ri)

#
# Wild Pokemon Section
#
# Pokemon's 9 Habitat types' related SIDs
"""
# Pokemon Habitat
typedef enum {
  kPokemonHabitatCave         = 1,
  kPokemonHabitatForest       = 2,
  kPokemonHabitatGrassland    = 3,
  kPokemonHabitatMountain     = 4,
  kPokemonHabitatRare         = 5, // Mean "Unknow"
  kPokemonHabitatRoughTerrain = 6,
  kPokemonHabitatSea          = 7,
  kPokemonHabitatUrban        = 8,
  kPokemonHabitatWatersEdge   = 9
}PokemonHabitat;
"""
k_habitat = [
        "51,92,42,94,50,93,41,95",
        "46,70,13,10,18,26,48,16,69,47,71,14,11,127,102,12,17,25,103,49,15",
        "2,58,123,20,37,83,44,125,33,85,78,128,31,96,115,40,24,59,38,45,1,29,84,19,43,32,34,108,77,30,97,114,39,3,23",
        "105,68,56,35,74,76,104,67,5,142,126,57,36,75,4,6,143,66",
        "144,145,151,146,150",
        "21,111,28,81,112,82,22,27",
        "90,139,117,87,73,120,140,91,86,116,131,121,141,138,72",
        "133,63,107,135,101,110,122,52,137,89,132,109,64,106,65,124,113,53,136,134,88,100",
        "9,80,119,147,54,61,130,149,98,7,148,79,118,55,62,129,8,99,6"
        ]
# wpm: Wild PokeMon
@server.get('/wpm')
def user_pokedex():
    header = Header(request.headers)
    if not header.auth():
        return {}
    openID = OpenID(header.get_provider(), header.get_identity())
    if not openID.authenticate():
        return {}
    return {'wpm':WildPokemon().get_SIDs(request.params)}
    #if not habitat_type:
    #    return {"wpm":self.redis.get(str(KEY)[:-1])}
        #return {"wpm":"1,2,3,4,5,6,7,8,9,10,11,12"}
    # wpm:Wild PokeMon
    #return {"wpm":k_habitat[int(habitat_type) - 1]}

#
# Pokemon Area
#
# pma: PokeMon Area
# GET all
@server.get('/pma')
def get_all_pokemon_area():
    header = Header(request.headers)
    if not header.auth():
        return {}
    openID = OpenID(header.get_provider(), header.get_identity())
    if not openID.authenticate():
        return {}
    # mas: Map AnnotationS
    # l: Level
    # as: AnotationS
    return {'pma':[
        '1=31.8867,117.2330:39.9333,116.2830:29.5167,106.4830:26.0833,119.2830:\
            36.0167,103.7500:23.1667,113.3330:22.8167,108.3500:26.5833,106.7170:\
            20.0333,110.3500:38.0500,114.4670:47.7500,126.6830:34.7167,113.6500:\
            30.6167,114.1330:28.2000,113.0830:32.0000,118.8000:28.6000,115.9170:\
            43.8500,126.5500:41.8000,123.4000:40.8167,111.6830:38.4833,106.2170:\
            36.6167,101.7670:34.3000,108.9330:36.6833,116.9830:31.2333,121.4670:\
            37.7833,112.5500:30.6667,104.0170:39.1833,117.3500:43.9000,87.4667:\
            29.6667,91.1333:25.0167,102.6830:30.2333,120.1670'
        ]}

# GET for special SID
@server.get('/pma/<sid:int>')
def get_pokemon_area(sid):
    header = Header(request.headers)
    if not header.auth():
        return {}
    openID = OpenID(header.get_provider(), header.get_identity())
    if not openID.authenticate():
        return {}
    # mas: Map AnnotationS
    # l: Level
    # as: AnotationS
    return {'pma':'31.8867,117.2330:39.9333,116.2830:29.5167,106.4830:26.0833,119.2830:\
            36.0167,103.7500:23.1667,113.3330:22.8167,108.3500:26.5833,106.7170:\
            20.0333,110.3500:38.0500,114.4670:47.7500,126.6830:34.7167,113.6500:\
            30.6167,114.1330:28.2000,113.0830:32.0000,118.8000:28.6000,115.9170:\
            43.8500,126.5500:41.8000,123.4000:40.8167,111.6830:38.4833,106.2170:\
            36.6167,101.7670:34.3000,108.9330:36.6833,116.9830:31.2333,121.4670:\
            37.7833,112.5500:30.6667,104.0170:39.1833,117.3500:43.9000,87.4667:\
            29.6667,91.1333:25.0167,102.6830:30.2333,120.1670'}


#
# Map Annotations
#
# mas: Map AnnotationS
# GET
@server.get('/mas/<code>')
def get_annotations(code):
    header = Header(request.headers)
    if not header.auth():
        return {}
    openID = OpenID(header.get_provider(), header.get_identity())
    if not openID.authenticate():
        return {}
    # mas: Map AnnotationS
    # l: Level
    # as: AnotationS
    return {"mas":[
        {
            'l':'1=2',
            'as' : [
                "CN=39.9333=116.2830=China=China"
                ]
            },
        {
            'l':'3=5',
            'as':[
                "CNAH=31.8867=117.2330=Anhui=Anhui",
                "CNBJ=39.9333=116.2830=Beijing=Beijing",
                "CNCQ=29.5167=106.4830=Chongqing=Chongqing",
                "CNFJ=26.0833=119.2830=Fujian=Fujian",
                "CNGS=36.0167=103.7500=Gansu=Gansu",
                "CNGD=23.1667=113.3330=Guangdong=Guangdong",
                "CNGX=22.8167=108.3500=Guangxi=Guangxi",
                "CNGZ=26.5833=106.7170=Guizhou=Guizhou",
                "CNHI=20.0333=110.3500=Hainan=Hainan",
                "CNHE=38.0500=114.4670=Hebei=Hebei",
                "CNHL=47.7500=126.6830=Heilongjiang=Heilongjiang",
                "CNHA=34.7167=113.6500=Henan=Henan",
                "CNHB=30.6167=114.1330=Hubei=Hubei",
                "CNHN=28.2000=113.0830=Hunan=Hunan",
                "CNJS=32.0000=118.8000=Jiangsu=Jiangsu",
                "CNJX=28.6000=115.9170=Jiangxi=Jiangxi",
                "CNJL=43.8500=126.5500=Jilin=Jilin",
                "CNLN=41.8000=123.4000=Liaoning=Liaoning",
                "CNNM=40.8167=111.6830=Nei Mongol=Nei Mongol",
                "CNNX=38.4833=106.2170=Ningxia=Ningxia",
                "CNQH=36.6167=101.7670=Qinghai=Qinghai",
                "CNSN=34.3000=108.9330=Shaanxi=Shaanxi",
                "CNSD=36.6833=116.9830=Shandong=Shandong",
                "CNSH=31.2333=121.4670=Shanghai=Shanghai",
                "CNSX=37.7833=112.5500=Shanxi=Shanxi",
                "CNSC=30.6667=104.0170=Sichuan=Sichuan",
                "CNTJ=39.1833=117.3500=Tianjin=Tianjin",
                "CNXJ=43.9000=87.4667=Xinjiang=Xinjiang",
                "CNXZ=29.6667=91.1333=Xizang=Xizang",
                "CNYN=25.0167=102.6830=Yunnan=Yunnan",
                "CNZJ=30.2333=120.1670=Zhejiang=Zhejiang"
                ]
            },
        {
            'l':'5=7',
            'as':[
                "CNZJHY=30.8943480=120.0868230=Huzhou=Huzhou",
                "CNZJHZ=30.2333=120.1670=Hangzhou=Hangzhou",
                "CNZJJH=29.107778=120=Jinhua=Jinhua",
                "CNZJJX=30.770696=120.752378=Jiaxing=Jiaxing",
                "CNZJLS=28.480321=119.930035=Lishui=Lishui",
                "CNZJNB=29.8=121.55=Ningbo=Ningbo",
                "CNZJQZ=28.942726=118.871851=Quzhou=Quzhou",
                "CNZJSX=29.701667=120.6=Shaoxing=Shaoxing",
                "CNZJTZ=28.683643=121.444462=Taizhou=Taizhou",
                "CNZJWZ=28.019158=120.653923=Wenzhou=Wenzhou",
                "CNZJZS=30.020324=122.111273=Zhoushan=Zhoushan"
                ]
            }
        ]}



#
# Start a server instance
#
run(
        server,                 # Run Bottle() instance: |server|
        host     = 'localhost',
        port     = 8080,
        reloader = True,        # restarts the server every time edit a module file
        debug    = True         # Comment out it before deploy
        )
