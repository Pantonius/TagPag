# ================================= CONFIG ================================
from dotenv import load_dotenv

loaded = False
def load():
    global loaded
    if not loaded:
        load_dotenv()
        loaded = True