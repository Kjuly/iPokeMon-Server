from bottle import Bottle, run

app = Bottle()

@app.route('/')
def index():
    return 'PService Running'

#
# Start a server instance
#
run(
        app,                    # Run |app| Bottle() instance
        host     = '0.0.0.0',
        port     = 8080,
        reloader = True,        # restarts the server every time edit a module file
        debug    = True         # Comment out it before deploy
        )
