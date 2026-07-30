import os

print("RUNNING APP FROM:")
print(os.path.abspath(__file__))

from flask import Flask
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ==========================================
# IMPORT ROUTES
# ==========================================

from routes.auth_routes import *
from routes.hub_routes import *
from routes.ttt_routes import *
from routes.profile_routes import *
from routes.api_routes import *
from routes.game_routes import *
from services.profile_service import get_profile

if __name__ == "__main__":

    app.run(
        debug=True
    )