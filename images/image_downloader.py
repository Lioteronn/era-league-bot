import requests
import os
from config import LOGO_PATH


def download_and_save_image(url, team_name):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(LOGO_PATH, exist_ok=True)
        file_path = os.path.join(LOGO_PATH, f"{team_name}.png")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    return None