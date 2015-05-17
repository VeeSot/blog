# Set the path
import sys
from main import app, DEBUG

import os
from flask.ext.script import Manager, Server


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=DEBUG,
    use_reloader=True,
    host='0.0.0.0')
)

if __name__ == "__main__":
    manager.run()
