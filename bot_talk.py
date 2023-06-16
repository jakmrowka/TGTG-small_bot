import json
import telebot
import os
from tgtg import TgtgClient
from threading import Thread
import time

# Load credentials for the bot and TGTG app from a JSON file
with open('credentials.json') as json_file:
    credentials = json.load(json_file)

# Initialize the bot using the token from credentials
bot = telebot.TeleBot(credentials["bot_token"])

# Initialize the TGTG client using the credentials provided in the JSON file
client = TgtgClient(access_token=credentials["tgtg_cred"]["access_token"],
                    refresh_token=credentials["tgtg_cred"]["refresh_token"],
                    user_id=credentials["tgtg_cred"]["user_id"],
                    cookie=credentials["tgtg_cred"]["cookie"])

# Setting the language to English (temporary fix for an issue with the TGTG API)
client.language = "en-US"

# Dictionaries to store user data and notifications
user_dict = {}
notifications = {}


# Define a User class to encapsulate user-related data and methods
class User:
    def __init__(self, name):
        '''
        Initialize a User object with a name (Telegram ID).
        Also initializes the user's location, search radius, and shops of interest.

        :param name: The Telegram ID of the user.
        '''
        self.name = name
        self.lat, self.long, self.rad, self.shops = self.lookfor(name)

    @staticmethod
    def lookfor(name):
        '''
        Load user's search parameters from a file.

        :param name: The Telegram ID of the user.
        :return: The user's latitude, longitude, search radius, and a list of shops of interest.
        '''
        path = f"data/{name}.txt"
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                lines = [line.rstrip() for line in f]
                lat = lines[0]
                long = lines[1]
                rad = lines[2]
                try:
                    shops = lines[3:]
                except:
                    shops = []
            return lat, long, rad, shops
        else:
            return 0, 0, 0, []


@bot.message_handler(commands=['help'])
def help(message):
    '''
    Respond to the user with the list of available commands.
    '''
    text = """Hej jestem botem i chcę Ci pomóc ratować jedzenie. Mam komendy:
/help - wyświetla pomoc
/start - przyjemny wstęp
/profil wprowadzenie/edycja parametrów szukania
/wszystkie - oj lista będzie długa
/aktualne - pokazuje aktualne
/szukaj - podaj chociaż fragment sklepu a postaram się go znaleźć
/omnie - pokazuje parametry szukania
/lista - lista Twoich sklepów do szukania
/dodaj - dodaj sklep
/usun  - usun sklep"""
    sent_msg = bot.send_message(message.chat.id, text)


# Handler function for the '/start' command that welcomes the user or provides instructions
@bot.message_handler(commands=['start'])
def begining(message):
    '''
    Handles the '/start' command. If the user is new, provides instructions for setting up the profile.
    If the user is returning, welcomes them back.
    '''
    path = f"data/{message.chat.id}.txt"
    if os.path.isfile(path):
        text = "mam Cię w bazie"
    else:
        text = "Nie mam Cię w bazie. Podaj proszę parametry szukania. Użyj komendy /profil"
    sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['lista'])
def list_favorite(message):
    '''
    Handles the /lista command.
    :return: Sends a list of favorite shops of the client.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Start building the message text
    text = "List of shops: \n"
    # Add each shop to the message text
    for line in user.shops:
        text += line + '\n'

    # Send the message to the user
    sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['omnie'])
def aboutme(message):
    '''
    Handles the /omnie command.
    :return: Sends data stored about the client.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Build the message text with user data
    text = f"""ID: {message.chat.id}
Latitude: {user.lat}
Longitude: {user.long}
Radius: {user.rad}
List of shops: \n"""
    # Add each shop to the message text
    for line in user.shops:
        text += line + '\n'

    # Send the message to the user
    sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['wszystkie'])
def allofthem(message):
    '''
    Handles the /wszystkie command.
    :return: Sends all shops in the given area and splits the list into messages of 100 shops per message.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Retrieve the items from an external resource
    items = client.get_items(
        favorites_only=False,
        latitude=user.lat,
        longitude=user.long,
        radius=user.rad,
        page_size=400
    )

    # Process the items and send messages in chunks
    if len(items) > 0:
        shops = []
        for temp in items:
            shops.append(temp["store"]["store_name"])
        # Remove duplicate shops
        shops = list(dict.fromkeys(shops))
        # Send the list in chunks of 100
        for i in range(0, len(shops), 100):
            chunk = shops[i:(i + 100)]
            # Construct the text of the message
            text = f"Part {int(i / 100) + 1} of {int(len(shops) / 100 + 1)}: \n"
            for shop in chunk:
                text += shop + "\n"
            # Send the message
            sent_msg = bot.send_message(message.chat.id, text)
    else:
        # No shops found
        text = "No shops found."
        sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['szukaj'])
def searchfor(message):
    '''
    Handles the /szukaj command.
    :param message: Name of the shop or part of it, not case-sensitive.
    :return: Sends a list of shops containing the given name.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Extract the shop_name from the message
    _, shop_name = message.text.split(" ", 1)

    # Retrieve items from an external resource
    items = client.get_items(
        favorites_only=False,
        latitude=user.lat,
        longitude=user.long,
        radius=user.rad,
        page_size=400
    )

    # Process items and send the search results
    if len(items) > 0:
        shops = []
        # Loop through each item and check for a match
        for temp in items:
            if shop_name in temp["store"]["store_name"].lower():
                shops.append(temp["store"]["store_name"])
        # Remove duplicate shops
        shops = list(dict.fromkeys(shops))

        # If matches found, send in chunks of 100
        if len(shops) > 0:
            for i in range(0, len(shops), 100):
                chunk = shops[i:(i + 100)]
                text = f"Part {int(i / 100) + 1} of {int(len(shops) / 100 + 1)}: \n"
                for shop in chunk:
                    text += shop + "\n"
                sent_msg = bot.send_message(message.chat.id, text)
        else:
            # If no matches found, send a message
            text = f"No shops found with the name {shop_name}."
            sent_msg = bot.send_message(message.chat.id, text)
    else:
        # If no items found, send a message
        text = f"No shops found with the name {shop_name}."
        sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['aktualne'])
def now_available(message):
    '''
    Handles the /aktualne command.
    :return: Sends a list of shops that currently have items available.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Retrieve items from an external resource
    items = client.get_items(
        favorites_only=False,
        latitude=user.lat,
        longitude=user.long,
        radius=user.rad,
        page_size=400
    )

    # Check if any items were retrieved
    if len(items) > 0:
        # Prepare the message text
        text = "Obecnie paczki są w sklepach: \n"
        shops = []
        # Append shops that have items available
        for temp in items:
            if temp["items_available"] > 0:
                shops.append(temp["store"]["store_name"])
        # Remove duplicate shop entries
        shops = list(dict.fromkeys(shops))
        # Append the shops to the message text
        for shop in shops:
            text += shop + "\n"
    else:
        # If no items are available, set message text accordingly
        text = "brak paczek teraz w sklepach"

    # Send the message to the user
    sent_msg = bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['dodaj', 'usun'])
def edit_shops(message):
    '''
    Handles the /dodaj and /usun commands.
    :return: Adds or removes shops from the user's list and notifies the user.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Split the message into command and shop name
    command, shop_name = message.text.split(" ", 1)

    # If the command is /dodaj, add the shop
    if command[1:] == 'dodaj':
        user.shops.append(shop_name)
        prefix = "dodano "
    # If the command is /usun, remove the shop
    elif command[1:] == 'usun':
        user.shops = [shop for shop in user.shops if shop != shop_name]
        prefix = "usunieto "

    # Save the updated profile
    save_profile(message.chat.id)

    # Notify the user of the action taken
    sent_msg = bot.send_message(message.chat.id, prefix + shop_name)


@bot.message_handler(commands=['single'])
def single_shot(message):
    '''
    Handles the /single command.
    :return: Sends a list of the user's favorite shops that currently have items available.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Retrieve items from an external resource
    items = client.get_items(
        favorites_only=False,
        latitude=user.lat,
        longitude=user.long,
        radius=user.rad,
        page_size=400
    )

    # Check if any items were retrieved
    if len(items) > 0:
        # Prepare the message text
        text = "Poluj: \n"
        shops = []
        # Append favorite shops that have items available
        for temp in items:
            if temp["items_available"] > 0:
                if temp["store"]["store_name"] in user.shops:
                    shops.append(temp["store"]["store_name"])
        # Remove duplicate shop entries
        shops = list(dict.fromkeys(shops))
        # Append the shops to the message text
        for shop in shops:
            text += shop + "\n"

        # If no shops found, update the message text
        if len(shops) <= 0:
            text = "musisz poczekać"
        else:
            # Send the message to the user
            sent_msg = bot.send_message(message.chat.id, text)
    else:
        # If no items are available, update the message text
        text = "musisz poczekać"


@bot.message_handler(commands=['profil'])
def profilowe(message):
    '''
    Handles the /profil command.
    :return: Begins the process of editing or creating a user profile.
    '''
    # Create a User object and add it to the user_dict
    user = User(message.chat.id)
    user_dict[message.chat.id] = user

    # Define the file path for the user's data
    path = f"data/{message.chat.id}.txt"

    # Check if the file already exists (i.e. editing profile vs creating profile)
    if os.path.isfile(path):
        # If editing, notify user and prompt for latitude
        text = "Zmieniamy dane. Podaj latitude. Twoja aktualna: {user.lat}"
    else:
        # If creating, prompt for latitude
        text = "Tworzymy profil. Podaj latitude"

    # Send message and register next step handler
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, latitude)


def latitude(message):
    '''
    Handles the latitude input during profile creation/editing.
    :return: Prompts the user for the longitude.
    '''
    # Retrieve the User object from the user_dict
    user = user_dict[message.chat.id]
    # Store the latitude
    user.lat = message.text
    # Define the file path for the user's data
    path = f"data/{message.chat.id}.txt"

    # Check if editing profile or creating profile
    if os.path.isfile(path):
        # If editing, notify user and prompt for longitude
        text = "Zmieniamy dane. Podaj longitude. Twoja aktualna: {user.long}"
    else:
        # If creating, prompt for longitude
        text = "Tworzymy profil. Podaj longitude"

    # Send message and register next step handler
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, longitude)


def longitude(message):
    '''
    Handles the longitude input during profile creation/editing.
    :return: Prompts the user for the radius.
    '''
    # Retrieve the User object from the user_dict
    user = user_dict[message.chat.id]
    # Store the longitude
    user.long = message.text
    # Define the file path for the user's data
    path = f"data/{message.chat.id}.txt"

    # Check if editing profile or creating profile
    if os.path.isfile(path):
        # If editing, notify user and prompt for radius
        text = "Zmieniamy dane. Podaj radius. Twoja aktualna: {user.rad}"
    else:
        # If creating, prompt for radius
        text = "Tworzymy profil. Podaj radius"

    # Send message and register next step handler
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, radius)


def radius(message):
    '''
    Handles the radius input during profile creation/editing.
    :return: Finalizes the profile creation/editing and notifies the user.
    '''
    # Retrieve the User object from the user_dict
    user = user_dict[message.chat.id]
    # Store the radius
    user.rad = message.text
    # Define the file path for the user's data
    path = f"data/{message.chat.id}.txt"

    # Check if editing profile or creating profile
    if os.path.isfile(path):
        # If editing, notify user that profile has been updated
        text = "zmieniłem profil mozemy zaczynać"
    else:
        # If creating, notify user that profile has been created
        text = "utworzyłem profil co moge jescze zrobić?"

    # Save the profile
    save_profile(message.chat.id)
    # Send final message
    sent_msg = bot.send_message(message.chat.id, text)


def save_profile(name):
    '''
    Saves the profile data to a file.
    :param name: The identifier for the user's data file.
    :return: None
    '''
    # Retrieve the User object from the user_dict
    user = user_dict[name]
    # Define the file path for the user's data
    path = f"data/{name}.txt"
    # Open the file and write the user data
    with open(path, "w", encoding="utf-8") as file:
        file.writelines([user.lat + "\n", user.long + "\n", user.rad + "\n", *[line + "\n" for line in user.shops]])


def prepare_hunt():
    '''
    Periodically checks for clients and initiates hunting process.
    :return: None
    '''
    # Continuous loop
    while True:
        # Retrieve a list of client files
        client_list = [f for f in os.listdir("data/") if os.path.isfile(os.path.join("data/", f))]
        # If there are client files, check each client
        if len(client_list) > 0:
            for client in client_list:
                check_for_client(client[:-4])
        else:
            # If no client files, sleep for 60 seconds before rechecking
            time.sleep(60)
        # Sleep for 6 seconds before next iteration
        time.sleep(6)


def check_for_client(name):
    # Initialize a user object with the given name
    user = User(name)

    # Add the user object to the user_dict dictionary with the user's name as the key
    user_dict[name] = user

    # Fetch items from a client using specified parameters such as latitude, longitude, radius, and page size
    items = client.get_items(
        favorites_only=False,
        latitude=user.lat,
        longitude=user.long,
        radius=user.rad,
        page_size=400
    )

    # Initialize notifications for the user if not already present
    if notifications.get(name) is None:
        notifications[name] = {}
    # Reset the counters of existing notifications to 0
    else:
        for key in notifications[name].keys():
            notifications[name][key] = 0

    # Check if any items are retrieved
    if len(items) > 0:
        # Initialize the text for the message to be sent
        text = "Poluj: \n"
        # List to keep track of the shops
        shops = []
        # Loop through each item
        for temp in items:
            # Check if the item is available and the store is in user's shop list
            if temp["items_available"] > 0 and temp["store"]["store_name"] in user.shops:
                # If the store is not in notifications, add it to the shops list
                if notifications[name].get(temp["store"]["store_name"]) is None:
                    shops.append(temp["store"]["store_name"])
                # Mark the store as notified
                notifications[name][temp["store"]["store_name"]] = 1

        # Remove duplicate entries from the shops list
        shops = list(dict.fromkeys(shops))

        # If there are shops with available items, send a message to the user
        if len(shops) >= 1:
            for shop in shops:
                text += shop + "\n"
            sent_msg = bot.send_message(name, text)
            print(f"New notifications for {name}", shops)

    # Find keys to be removed where the value is 0
    keys_to_remove = [key for key, value in notifications[name].items() if value == 0]

    # If there are keys to be removed, print a message
    if len(keys_to_remove) >= 1:
        print(f"Deleted notification batches for {name}", keys_to_remove)

    # Remove the keys from the notifications
    for key in keys_to_remove:
        notifications[name].pop(key)


# Handle all other messages
@bot.message_handler(func=lambda message: True)
def other_messages(message):
    # Default response text for unsupported inputs
    text = "Nie znam tej komendy. Jeżeli masz problemy napisz /help"
    # Send the message
    sent_msg = bot.send_message(message.chat.id, text)


if __name__ == "__main__":
    # Start a thread for preparing hunt which runs in the background
    Thread(target=prepare_hunt).start()
    # Start polling for bot updates
    bot.polling(none_stop=True)
