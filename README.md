
[![LinkedIn][linkedin-shield]][linkedin-url]
<a name="top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  
  <h3 align="center">Too Good To Go - bot for telegram</h3>

  <p align="center">
    A simple bot for personal use
    
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li><a href="#Features">Features</a></li>
    <li><a href="#Installation">Installation</a></li>
    <li><a href="#Configuration">Configuration</a></li>
    <li><a href="#Usage">Usage</a></li>
    <li><a href="#Acknowledgments">Acknowledgments</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

TGTG Bot is a Telegram bot designed to help users track available items in various stores and manage user preferences regarding their hunting preferences. It uses the tgtg api library to interact with the Too Good To Go service for fetching information about items availability and integrates with Telegram for notifying users in real-time.
#### Please note all comands for bot are in polish, but I can create english version if needed.
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Features -->
## Features

* **Items Availability:** Fetches the availability of items in different stores based on user's location and preferences.
* **User Profiles:** Handles user profiles with custom locations and radius for tracking items.
* **Custom Notifications:** Notifies users about new item availability based on their selected stores.
* **Add/Remove Stores:** Allows users to add or remove stores from their preference list.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Installation -->
## Installation

Before running TGTG Bot, you need to have Python installed. You can download it from [here](https://www.python.org/downloads/).
After installing Python, clone the repository:
```sh
git clone https://github.com/yourusername/shophunterbot.git
cd shophunterbot
```
Now, install the required Python dependencies:
```sh
pip install -r requirements.txt
```
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Configuration -->
## Configuration

Before starting the bot, you will need to create a bot on Telegram and obtain a bot token. Follow [this guide](https://core.telegram.org/bots#6-botfather) to create a bot on Telegram.

After obtaining your bot token, create a file named **credentials.json** in the root directory with the following structure:
```
{
  "bot_token": "YOUR_TOKEN",
  "tgtg_cred": {
    "access_token": "YOUR_ACCESS_TOKEN",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "user_id": "USER_ID",
    "cookie": "COOKIES"
  }
}
```
Replace **YOUR_TELEGRAM_BOT_TOKEN** with the token you got from BotFather.
TGTG credentials can be found using:
```python
from tgtg import TgtgClient
client = TgtgClient(email="<your_email>")
credentials = client.get_credentials()
```
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Usage -->
## Usage

Run the bot using the following command:
```sh
    python bot_talk.py
```
Now, you can interact with your bot on Telegram by sending commands such as **/aktualne** to check available items, **/dodaj** or **/usun** to add or remove stores, and **/profil** to manage your profile.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Acknowledgments -->
## Acknowledgments

Thanks to the creators of the **telebot** and **tgtg** libraries for making the development of this bot possible.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Jakub Mrowka -  jakmrowka@gmail.com

Project Link: [https://https://github.com/jakmrowka](https://https://github.com/jakmrowka)

<p align="right">(<a href="#top">back to top</a>)</p>




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/jakub-mrowka/

