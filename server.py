from bottle import Bottle, run
import redis
from hashlib import md5
import time

server = Bottle()
RADIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB   = 8

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

    # The user has no OpenID added before, so add new
    def add(self):
        # Get the new user's ID
        userid = self.redis.incr("global:nextUserid")
        # If add new openID successed(it's value is <userid>),
        # then add new user
        if self.redis.setnx("%s:%s" % (self.provider, md5(self.identity).hexdigest()), userid):
            self.redis.sadd("openid:%s" % userid, self.provider)
            return User(userid).add(
                    "user%s" % userid,   # Name
                    time.time(),         # Time started
                    1000,                # Money
                    "0",                 # Badges
                    "0",                 # Six Pokemons
                    "0",                 # Pokedex
                    0,                   # Number of Pokemons
                    "0_0_0_0_0_0_0_0_0"  # Bag
                    )
        else:
            return False

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
        if self.redis.sismember("%s:%s" % (self.provider, md5(self.identity).hexdigest())):
            return True
        else:
            return False

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
#       <bag>: <bagItems>_<bagMedicineStatus>_<bagMedicineHP>_<bagMedicinePP>
#           _<bagPokeballs>_<bagTMsHMs>_<bagBerries>_<bagBattleItems>_<bagKeyItems>
#     & <bagItems>, <...>: "1,2,3,..."
#  SO:
#       <bag>: "1,2,3_1,2,3_..._1,2,3"                                              
class User(object):
    def __init__(self, p_user_id):
        self.redis  = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
        self.userid = p_user_id

    # Get all data for a user with <userid>
    def get(self):
        #return self.redis.hget("u:%s" % userid, "name")
        return self.redis.hgetall("u:%s" % self.userid)

    # Update data for user
    def update(self, p_userdata):
        if self.redis.sismember("u:%s" % self.userid):
            self.redis.hmset(
                    "u:%s" % self.userid, # Hash Key
                    p_userdata            # Mapping
                    #"name",        p_userdata['username'],
                    #"timeStarted", p_userdata['timeStarted'],
                    #"money",       p_userdata['money'],
                    #"badges",      p_userdata['badges',
                    #"sixPokemons", p_userdata['sixPokemons'],
                    #"pokedex",     p_userdata['pokedex'],
                    #"pokemons",    p_userdata['pokemons'],
                    #"bag",         p_userdata['bag']
                    )
            return True
        else:
            return False

    
    # Add new user
    def add(self, p_username, timeStarted, p_money, p_badges,
            p_sixPokemons, p_pokedex, p_pokemons, bag):
        # If add user successed, i.e. <userid> does not exist in <users> set
        if self.redis.sadd("users", self.userid):
            #self.redis.hset("u:%s" % self.userid, "name",    p_username)
            #self.redis.hset("u:%s" % self.userid, "pokedex", p_pokedex)
            self.redis.hmset(
                    "u:%s" % self.userid, # Hash Key
                    "id",          self.userid,
                    "name",        p_username,
                    "timeStarted", p_timeStarted,
                    "money",       p_money,
                    "badges",      p_badges,
                    "sixPokemons", p_sixPokemons,
                    "pokedex",     p_pokedex,
                    "pokemons",    p_pokemons,
                    "bag",         p_bag
                    )
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
#       "p_currEXP":   <currEXP>,     # Number.
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
        if self.redis.sismember("pm:%s:%s" % (self.userid, p_pokemon_uid)):
            self.redis.hmset(
                    "pm:%s:%s" % (self.userid, pokemon_uid), # Hash Key
                    p_pokemon_data                           # Mapping
                    #"box",         p_pokemon_data['box'],
                    #"status",      p_pokemon_data['status'],
                    #"happiness",   p_pokemon_data['happiness'],
                    #"level",       p_pokemon_data['level'],
                    #"fourMoves",   p_pokemon_data['fourMoves'],
                    #"maxStats",    p_pokemon_data['maxStats'],
                    #"currHP",      p_pokemon_data['currHP'],
                    #"p_currEXP",   p_pokemon_data['currEXP'],
                    #"toNextLevel", p_pokemon_data['toNextLevel'],
                    #"memo",        p_pokemon_data['memo']
                    )
            return True
        else:
            return False


    # Add new tamed Pokemon
    def add(self, p_sid, p_box, p_status, p_gender, p_happiness, p_level,
            p_fourMoves, p_maxStats, p_currHP, p_currEXP, p_toNextLevel, p_memo):
        if self.redis.sadd("pokedex:%s" % self.userid, p_uid):
            pokemon_uid = self.redis.incr("u:%s" % self.userid, "pokemons")
            self.redis.hmset(
                    "pm:%s:%s" % (self.userid, pokemon_uid), # Hash Key
                    "uid",         pokemon_uid,
                    "sid",         p_sid,
                    "box",         p_box,
                    "status",      p_status,
                    "gender",      p_gender,
                    "happiness",   p_happiness,
                    "level",       p_level,
                    "fourMoves",   p_fourMoves,
                    "maxStats",    p_maxStats,
                    "currHP",      p_currHP,
                    "p_currEXP",   p_currEXP,
                    "toNextLevel", p_toNextLevel,
                    "memo",        p_memo
                    )
            return True
        else:
            return False


#
# RESTs
#
@server.route('/')
def index():
    r = redis.Redis(RADIS_HOST, REDIS_PORT, REDIS_DB)
    r.setnx('global:nextUserid', 0)
    return 'PMService is Running'

#
# User Section
#
# User - GET <userid>
@server.get('/oauth/<provider>/<identity>')
def oauth(provider, identity):
    openID = OpenID(provider, identity)
    if openID.authenticate():
        return openID.authorized_user()

# User - GET Data
@server.get('/user/<userid:int>')
def user(userid):
    return User(userid).get()

# User - POST Data
@server.post('/user/<userid:int>')
def update_user(userid):
    if User(userid).update():
        return True
    else:
        return False


# User - GET Pokemon
@server.get('/user/<userid:int>/<pokemon_uid:int>')
def user_pokemon(userid, pokemon_uid):
    return Pokemon(userid).get_one(pokemon_uid)

# User - GET Six Pokemons
@server.get('/user/<userid:int>/sixpokemons')
def user_sixpokemons(userid):
    return {"sixPokemons":Pokemon(userid).get_six()}

# User - GET Pokedex
@server.get('/user/<userid:int>/pokedex')
def user_pokedex(userid):
    return {"pokedex":Pokemon(userid).get_all()}


#
# Pokemon Section
#
# Pokemon - Area
@server.route('/pokemon/<id:int>/area')
def pokemon_area(id):
    pass

# Region - Wild Pokemons
@server.route('/region/<id:int>/wildpokemons')
def user_pokedex(id):
    pokedex = { 'wildpokemons' :
            [
                {
                    'uid' : 1,
                    'sid' : 1,
                    'status' : 1,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600},
                {
                    'uid' : 2,
                    'sid' : 2,
                    'status' : 2,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600},
                {
                    'uid' : 3,
                    'sid' : 2,
                    'status' : 2,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600},
                {
                    'uid' : 4,
                    'sid' : 4,
                    'status' : 3,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600},
                {
                    'uid' : 5,
                    'sid' : 5,
                    'status' : 3,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600},
                {
                    'uid' : 6,
                    'sid' : 8,
                    'status' : 3,
                    'gender' : 1,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600}
                ]}
    return pokedex


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
