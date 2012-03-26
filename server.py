from bottle import Bottle, run

server = Bottle()

@server.route('/')
def index():
    return 'PService Running'

#
# User Section
#
# User
@server.route('/user/<id:int>')
def user(id):
    dict_list = {
            'id'     : 1,
            'name'   : 'Trainer Name 1',
            'pokedex': '1111001101',
            'sixPokemons' : '4,5,6,2,3',
            'money'  : 999999,
            'badges' : 123,
            'adventure_started' : '2012-01-22',
            'bagItems' : '1,3,2,3,3,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3,29,3,30,3,31,3,32,3',
            'bagMedicineStatus' : '1,3,2,3,3,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3',
            'bagMedicineHP' : '5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3',
            'bagMedicinePP' : '4,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3',
            'bagPokeballs' : '1,3,2,3,3,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3',
            'bagTMsHMs' : '',
            'bagBerries' : '1,3,2,3,3,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3,29,3,30,3,31,3,32,3,33,3,34,3,35,3,36,3,37,3,38,3,39,3,40,3,41,3,42,3,43,3,44,3,45,3,46,3,47,3,48,3,49,3,50,3,51,3,52,3,53,3,54,3,55,3,56,3,57,3,58,3,59,3,60,3,61,3,62,3,63,3,64,3',
            'bagBattleItems' : '1,3,2,3,3,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3,29,3,30,3,31,3,32,3,33,3,34,3,35,3,36,3,37,3,38,3,39,3,40,3,41,3,42,3,43,3,44,3,45,3,46,3,47,3,48,3,49,3,50,3,51,3,52,3,53,3,54,3,55,3,56,3,57,3,58,3,59,3,60,3,61,3,62,3,63,3,64,3,64,3,65,3,66,3,67,3,68,3,69,3,70,3,71,3,72,3,73,3,74,3,75,3,76,3,77,3,78,3,79,3,80,3,81,3,82,3,83,3,84,3,85,3,86,3,87,3,88,3,89,3,90,3,91,3,92,3,93,3,94,3,95,3,96,3,97,3,98,3,99,3,100,3,101,3,102,3,103,3,104,3,105,3,106,3,107,3,108,3,109,3,110,3,111,3,112,3',
            'bagKeyItems' : '1,3,2,3,3,3,4,3,5,3,6,3,7,3,8,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3,20,3,21,3,22,3,23,3,24,3,25,3,26,3,27,3,28,3,29,3,30,3,31,3,32,3,33,3,34,3,35,3,36,3,37,3'
            }
    return dict_list

# User - Pokedex
@server.route('/user/<id:int>/pokedex')
def user_pokedex(id):
    pokedex = { 'pokedex' :
            [
                {
                    'uid' : 1,
                    'sid' : 1,
                    'box' : 1,
                    'status' : 1,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'},
                {
                    'uid' : 2,
                    'sid' : 12,
                    'box' : 1,
                    'status' : 2,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'},
                {
                    'uid' : 3,
                    'sid' : 6,
                    'box' : 1,
                    'status' : 2,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'},
                {
                    'uid' : 4,
                    'sid' : 4,
                    'box' : 1,
                    'status' : 3,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'},
                {
                    'uid' : 5,
                    'sid' : 5,
                    'box' : 1,
                    'status' : 3,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'},
                {
                    'uid' : 6,
                    'sid' : 8,
                    'box' : 1,
                    'status' : 3,
                    'gender' : 1,
                    'happiness' : 70,
                    'level' : 10,
                    'fourMoves' : '1,30,26,2,35,31,3,25,21,4,5,4',
                    'maxStats' : '145,49,49,65,65,45',
                    'currHP' : 132,
                    'currEXP' : 10240,
                    'toNextLevel' : 3600,
                    'memo' : 'Memo Words Here.'}
                ]}
    return pokedex

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
