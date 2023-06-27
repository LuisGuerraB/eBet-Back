import sys

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    args = sys.argv[1:]

    if not args:
        app.debug = True
        app.run(threaded=True)

    else:
        port = None
        host = None
        debug = True
        for arg in args:
            if arg[:7] == '--port=':
                port = int(arg[7:])
            elif arg[:8] == '--debug=':
                debug = arg[8:] == 'True'
            elif arg[:7] == '--host=':
                host = arg[7:]
        app.run(host=host, port=port, debug=debug, threaded=True)
