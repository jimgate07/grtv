
import requests
import re
import sys
import subprocess
def install_bs4():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "bs4"])

try:
    from bs4 import BeautifulSoup
except:
    install_bs4()
    from bs4 import BeautifulSoup


