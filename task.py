import os
import requests
import time
from datetime import datetime
from colorama import Fore, Style, init
import json

# Initilisation des couleurs pour les notifications
init(autoreset=True)

# Configuration du logging pour supprimer les messages indésirables
import logging
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("instagrapi").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)

# URL du fichier JSON sur GitHub
STATUS_URL = "https://raw.githubusercontent.com/Ken56266325/script-control-server/main/status5.json"

# Contact pour renouvellement
SUPPORT_EMAIL = "kennymampifaly@gmail.com"
SUPPORT_PHONE = "https://t.me/SmmtaskerBot"

# Fichier pour stocker l'ID de l'utilisateur
USER_ID_FILE = "user_id.txt"

# Fonction pour récupérer et synchroniser les données du serveur
def sync_server_data():
    try:
        # Récupération des données du fichier JSON depuis le serveur
        response = requests.get(STATUS_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Erreur lors de la récupération des données du serveur : {e}")
        exit()

# Fonction pour convertir un timestamp en format j/h/min/s
def convert_timestamp_to_time_left(timestamp):
    try:
        # Convertir le timestamp en datetime
        end_time = datetime.fromisoformat(timestamp)
        current_time = datetime.now()
        remaining_time = end_time - current_time

        # Vérifier si le temps est écoulé
        if remaining_time.total_seconds() <= 0:
            return "0j/0h/0min/0s", True  # Temps écoulé, désactivation immédiate

        # Convertir en j/h/min/s
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Retourner le temps restant
        return f"{days}j/{hours}h/{minutes}min/{seconds}s", False
    except Exception as e:
        print(Fore.RED + f"❌ Erreur lors de la conversion du timestamp : {e}")
        return "0j/0h/0min/0s", True

# Vérification du statut de l'utilisateur
def check_user_status(user_id, data):
    # Parcourir les scripts pour trouver l'ID correspondant
    for script in data.get("scripts", []):
        if script.get("id") == user_id:
            status = script.get("status")
            countdown_start = script.get("countdown_start_time")
            affiliation_balance = script.get("affiliation_balance", 0)  # Récupérer le solde d'affiliation
            android_id = script.get("android_id", None)  # Récupérer l'Android ID
            plan = script.get("plan", "Null")  # Récupérer le plan (Basique ou VIP)

            # Si le statut est "inactive", le script est bloqué
            if status != "active":
                return "inactive", countdown_start, affiliation_balance, android_id, plan

            # Si la date de début n'est pas définie ou invalide
            if countdown_start == "0" or not countdown_start:
                return "inactive", "0j/0h/0min/0s", affiliation_balance, android_id, plan

            # Si tout est correct, retourner le countdown_start et affiliation_balance
            return "active", countdown_start, affiliation_balance, android_id, plan

    # Si aucun ID correspondant n'est trouvé
    print(Fore.RED + f"❌ ID non trouvé : {user_id}")
    print(Fore.YELLOW + f"Veuillez contacter le support : {SUPPORT_EMAIL} ou {SUPPORT_PHONE}")
    exit()

# Afficher le statut de l'utilisateur avec le solde d'affiliation
def display_status(user_id, status, countdown, affiliation_balance, plan, announcement):
    os.system('clear')
    print(Fore.GREEN + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + f"Bienvenue, utilisateur ID : {user_id}")
    print(Fore.YELLOW + f"Statut : {status}")
    print(Fore.MAGENTA + f"Temps restant : {countdown}")
    print(Fore.BLUE + f"Solde d'affiliation : {affiliation_balance}Ar")  # Affichage du solde d'affiliation
    
    # Affichage du plan avec emojis
    if plan == "VIP":
        plan_display = "💎VIP💎"
    elif plan == "Basique":
        plan_display = "🔰Basique🔰"
    else:
        plan_display = "❓Aucun Plan❓"
    print(Fore.GREEN + f"Plan : {plan_display}")

    print(Fore.GREEN + f"📢 Annonce du service clientèle : {announcement}")
    print(Fore.GREEN + "=" * 50)

# Enregistrer l'ID de l'utilisateur dans un fichier
def save_user_id(user_id):
    with open(USER_ID_FILE, "w") as file:
        file.write(user_id)

# Lire l'ID de l'utilisateur depuis un fichier
def read_user_id():
    if os.path.exists(USER_ID_FILE):
        with open(USER_ID_FILE, "r") as file:
            return file.read().strip()
    return None

# Fonction pour demander les identifiants API et les enregistrer
def request_and_save_api_credentials():
    if not os.path.exists('config.json'):
        print(Fore.YELLOW + "Vous devez entrer votre API ID, API Hash et numéro de téléphone.")
        api_id = input(Fore.YELLOW + "Entrez votre API ID : ")
        api_hash = input(Fore.YELLOW + "Entrez votre API Hash : ")
        phone_number = input(Fore.YELLOW + "Entrez votre numéro de téléphone : ")

        # Sauvegarder les informations dans un fichier JSON
        with open('config.json', 'w') as config_file:
            json.dump({"api_id": api_id, "api_hash": api_hash, "phone_number": phone_number}, config_file)
            print(Fore.GREEN + "Informations sauvegardées avec succès.")
    else:
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
            api_id = config_data['api_id']
            api_hash = config_data['api_hash']
            phone_number = config_data['phone_number']
    return api_id, api_hash, phone_number

# Demander les identifiants API lors de la première connexion ou les charger
api_id, api_hash, phone_number = request_and_save_api_credentials()
bot_username = '@smmkingdomtasksbot'

# Début du script principal
if __name__ == "__main__":
    os.system('clear')
    print(Fore.CYAN + "🔍 Vérification du statut utilisateur...")

    # Vérifier si un ID est déjà enregistré
    user_id = read_user_id()

    # Si l'ID n'est pas enregistré, demander à l'utilisateur de le saisir
    if not user_id:
        user_id = input(Fore.CYAN + "Entrez votre ID unique : ").strip()
        save_user_id(user_id)  # Enregistrer l'ID pour les futures utilisations

    # Synchroniser les données depuis le serveur
    data = sync_server_data()

    # Vérification de l'ID et récupération du statut et du solde d'affiliation
    status, countdown, affiliation_balance, android_id, plan = check_user_status(user_id, data)

    # Convertir le timestamp en format lisible et vérifier si le temps est écoulé
    countdown_time, expired = convert_timestamp_to_time_left(countdown)

    # Si le statut est inactif ou que le temps est écoulé
    if status == "inactive" or expired:
        print(Fore.RED + f"❌ Statut inactif ou abonnement expiré pour l'ID : {user_id}")
        print(Fore.YELLOW + f"Renouvelez votre abonnement via : {SUPPORT_PHONE}")
        exit()

    # Récupérer l'annonce du serveur
    announcement = data.get("announcement", "Aucune annonce pour le moment.")

    # Afficher le statut et le solde d'affiliation
    display_status(user_id, status, countdown_time, affiliation_balance, plan, announcement)

    # Option pour continuer
    input(Fore.YELLOW + "Appuyez sur Entrée pour continuer vers le script principal...")

# Ton script existant commence ici
import asyncio
from telethon import TelegramClient, events
from instagrapi import Client
from colorama import Fore, Style, init
from datetime import datetime
import time
import re
import json
import os
import random
import requests
from threading import Thread
import subprocess

# Initialisation des couleurs pour les notifications
init(autoreset=True)

# URL du fichier JSON sur GitHub
STATUS_URL = "https://raw.githubusercontent.com/Ken56266325/script-control-server/main/status5.json"

# Fonction pour afficher une bannière stylisée
def print_banner():
    os.system('clear')
    print(Fore.GREEN + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + " ╔═╗┬ ┬┬┬┬┬┌─┐┬ ┌┬┐┌─┐┬─┐")
    print(Fore.CYAN + " ║ ├─┤││││├┤ │ │ │ │├┬┘")
    print(Fore.CYAN + " ╚═╝┴ ┴┴┴┴┴└─┘┴─┘ ┴ └─┘┴└─")
    print(Fore.MAGENTA + " SMM Instagram & Telegram Task Manager")
    print(Fore.YELLOW + " SMMTASKERBOT")
    print(Fore.WHITE + " Developed by Trader Zandriny")
    print(Fore.GREEN + "=" * 50)
    print(Fore.YELLOW + " 💥 Choisissez une option 💥")
    print(Fore.GREEN + " 1️⃣ Tasks - Lancer le script principal")
    print(Fore.CYAN + " 2️⃣ 📱 Gestion des comptes Instagram 📱")
    print(Fore.YELLOW + " 🌐 Veuillez faire un choix : ")

# Demander à l'utilisateur de choisir une option
def get_user_choice():
    while True:
        choice = input(Fore.YELLOW + "Entrez votre choix (1 ou 2) : ")
        if choice == "1":
            return "tasks"
        elif choice == "2":
            os.system('./i.bin')  # Exécution du fichier az.bin
            return "instagram_management"
        else:
            print(Fore.RED + "Choix invalide. Veuillez entrer 1 ou 2.")

# Fonction pour charger les comptes Instagram depuis les fichiers de session
def load_instagram_accounts():
    instagram_accounts = []
    for file in os.listdir():
        if file.endswith("_session.json"):
            username = file.replace("_session.json", "")
            instagram_accounts.append({"username": username, "password": ""})
    return instagram_accounts

clients = {}
response_received = asyncio.Event()
clear_sessions = False
current_account_index = 0

# Fonction pour loguer les messages avec un timestamp
def log_message(message, color=Fore.YELLOW):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {color}{message}")

# Supprimer toutes les anciennes sessions Instagram si nécessaire
def delete_instagram_sessions():
    if clear_sessions:
        for session_file in os.listdir():
            if session_file.endswith(".json"):
                os.remove(session_file)
                log_message(f"Ancienne session supprimée : {session_file}", Fore.RED)

# Connexion aux comptes Instagram
def login_instagram(account):
    username = account['username']
    session_file = f"{username}_session.json"
    client = Client()
    retries = 3
    while retries > 0:
        try:
            if os.path.exists(session_file):
                client.load_settings(session_file)
                log_message(f"✔ Session restaurée pour {username}", Fore.GREEN)
            else:
                log_message(f"❌ Impossible de trouver la session pour {username}", Fore.RED)
            clients[username] = client
            return True
        except Exception as e:
            log_message(f"❌ Erreur pour {username}: {e}", Fore.RED)
            retries -= 1
            if retries == 0:
                log_message(f"❌ Impossible de se connecter à {username} après plusieurs tentatives.", Fore.RED)
            time.sleep(5)
    return False

# Fonction pour vérifier le statut utilisateur et le plan sur GitHub
def check_user_status(user_id):
    try:
        response = requests.get(STATUS_URL)
        response.raise_for_status()
        data = response.json()

        # Parcourir les scripts pour trouver l'ID correspondant
        for script in data.get("scripts", []):
            if script.get("id") == user_id:
                status = script.get("status")
                plan = script.get("plan", "Null")  # Récupérer le plan (Basique ou VIP)

                if status != "active":
                    log_message(f"❌ Statut inactif pour l'ID {user_id}. Contactez le support.", Fore.RED)
                    exit()

                log_message(f"✔ Statut actif pour l'ID {user_id}, Plan : {plan}", Fore.GREEN)
                return plan

        # Si l'ID n'est pas trouvé
        log_message(f"❌ ID {user_id} non trouvé dans les données.", Fore.RED)
        exit()

    except Exception as e:
        log_message(f"❌ Erreur lors de la récupération du statut utilisateur : {e}", Fore.RED)
        exit()

# Limiter les comptes Instagram en fonction du plan
def filter_instagram_accounts(accounts, plan):
    if plan == "Basique":
        log_message("🔰 Plan Basique détecté. Limitation à 100 comptes Instagram.", Fore.YELLOW)
        return accounts[:100]
    elif plan == "VIP":
        log_message("💎 Plan VIP détecté. Limitation à 200 comptes Instagram.", Fore.YELLOW)
        return accounts[:200]
    else:
        log_message("❓ Plan inconnu. Aucun compte ne sera chargé.", Fore.RED)
        return []

# Fonction pour récupérer l'ID utilisateur à partir du fichier
def get_user_id_from_file():
    try:
        with open('user_id.txt', 'r') as file:
            user_id = file.read().strip()
            return user_id
    except Exception as e:
        log_message(f"❌ Erreur lors de la lecture du fichier user_id.txt : {e}", Fore.RED)
        exit()

def connect_instagram_accounts():
    user_id = get_user_id_from_file()  # Récupère l'ID utilisateur depuis le fichier
    log_message("\n[•] Connexion aux comptes Instagram...", Fore.YELLOW)
    delete_instagram_sessions()

    # Charger les comptes Instagram
    instagram_accounts = load_instagram_accounts()

    # Vérifier le plan utilisateur
    plan = check_user_status(user_id)

    # Limiter les comptes Instagram en fonction du plan
    filtered_accounts = filter_instagram_accounts(instagram_accounts, plan)

    connected_accounts = []
    for account in sorted(filtered_accounts, key=lambda x: x['username']):
        if login_instagram(account):
            connected_accounts.append(account)
        else:
            log_message(f"⚠️ Suppression du compte {account['username']} car il n'a pas pu se connecter.", Fore.RED)
    return connected_accounts

client = TelegramClient('session', api_id, api_hash)

# Initialisation de Colorama
init(autoreset=True)

# Chemin vers le fichier audio
audio_file = "/storage/emulated/0/Download/mcbox_jamais_run_hit_aac_29449.m4a"

# Fonction pour jouer un son
def play_sound():
    os.system(f"mpv --no-video --length=12 {audio_file}")

# Fonction pour enregistrer une ligne de log avec une couleur spécifiée
def log_message(message, color=Fore.WHITE):
    # Afficher le message dans la couleur spécifiée sans la date et l'heure
    print(color + message)

# Variables globales
login_required_error_flag = False
INSTAGRAM_ACCOUNTS_DIR = "."
clients = {}
instagram_accounts = []

# Variables globales pour le dernier message envoyé et le timestamp
last_message_sent = None
last_message_time = time.time()
last_message_type = None  # Pour distinguer les types de messages

# Fonction pour récupérer les informations système dynamiquement
def get_system_info():
    def run_command(command):
        try:
            result = subprocess.check_output(command, shell=True, universal_newlines=True)
            return result.strip()
        except Exception as e:
            return None

    # Fonction pour générer des valeurs aléatoires pour la résolution et les DPI
    def generate_random_value(default_value, min_value=200, max_value=500):
        if default_value is None:
            return f"{random.randint(min_value, max_value)}dpi"
        return default_value

    device_info = {
        "model": run_command("getprop ro.product.model"),
        "device": run_command("getprop ro.product.device"),
        "android_version": run_command("getprop ro.build.version.sdk"),
        "android_release": run_command("getprop ro.build.version.release"),
        "dpi": generate_random_value(run_command("wm density | grep -oE '[0-9]+'")),
        "resolution": generate_random_value(run_command("wm size | grep -oE '[0-9]+x[0-9]+'"), min_value=720, max_value=1920),
        "manufacturer": run_command("getprop ro.product.manufacturer"),
        "cpu": run_command("getprop ro.hardware"),
        "version_code": "366906357", # Garder comme valeur par défaut
    }

    # Si certaines informations sont manquantes, les générer de manière aléatoire
    if device_info["model"] is None:
        device_info["model"] = "vivo 1807" # Valeur par défaut
    if device_info["device"] is None:
        device_info["device"] = "vivo" # Valeur par défaut
    if device_info["android_version"] is None:
        device_info["android_version"] = "29" # Valeur par défaut (Android 10)
    if device_info["android_release"] is None:
        device_info["android_release"] = "10" # Valeur par défaut

    device_info["user_agent"] = (
    f"Instagram 269.0.0.18.75 Android ({device_info['android_version']}/"
    f"{device_info['android_release']}; {device_info['dpi']}; "
    f"{device_info['resolution']}; {device_info['manufacturer']}; "
    f"{device_info['model']}; {device_info['device']}; {device_info['cpu']}; "
    f"en_US; {device_info['version_code']})"
)
    return device_info

# Nouvelle fonction : se connecter et sauvegarder une session Instagram
def connect_instagram(username, password):
    client = Client()
    session_file = os.path.join(INSTAGRAM_ACCOUNTS_DIR, f"{username}_session.json")
    old_session_file = f"{username}_session"  # Fichier à supprimer si existant

    # Charger une session existante si elle existe
    if os.path.exists(session_file):
        with open(session_file, "r") as file:
            settings = json.load(file)
        client.set_settings(settings)

    try:
        client.login(username, password)

        # Supprimer le fichier "username_session" s'il existe
        if os.path.exists(old_session_file):
            os.rmdir(old_session_file)

        # Récupérer les informations dynamiquement
        device_settings = get_system_info()

        # Paramètres de localisation pour Madagascar
        location_settings = {
            "country": "MG", # Madagascar (code pays ISO)
            "country_code": "261", # Code téléphonique de Madagascar
            "locale": "fr_FR", # Langue française
            "timezone_offset": 10800 # Fuseau horaire de Madagascar (UTC+3)
        }

        # Sauvegarder la session après connexion avec les nouvelles informations
        settings = client.get_settings()
        settings['device_settings'] = device_settings
        settings['user_agent'] = device_settings['user_agent'] # Mettre à jour user_agent dans la session
        settings.update(location_settings) # Mettre à jour la localisation (pays, fuseau horaire, etc.)

        with open(session_file, "w") as file:
            json.dump(settings, file, indent=4)

        return True # Connexion réussie
    except Exception as e:
        print(Fore.RED + f"Erreur lors de la connexion : {e}")
        return False # Connexion échouée

# Fonction pour gérer l'erreur "login_required"
async def handle_login_required_error(account):
    global login_required_error_flag

    # Si c'est la première occurrence de l'erreur, on joue le fichier audio
    if not login_required_error_flag:
        os.system("mpv --no-video --length=12 /storage/emulated/0/Download/mcbox_jamais_run_hit_aac_29449.m4a")
        login_required_error_flag = True

    print(Fore.RED + "=" * 50)
    print(Fore.YELLOW + "🚨 Erreur 'login_required' rencontrée ! 🚨")
    print(Fore.YELLOW + "Veuillez choisir une option :")
    print(Fore.GREEN + "1️⃣ Supprimer la session du compte")
    print(Fore.BLUE + "2️⃣ Reconnecter le compte")
    print(Fore.CYAN + "3️⃣ Reprendre les tâches normales")
    print(Fore.RED + "=" * 50)

    choice = input(Fore.YELLOW + "Entrez votre choix : ")

    if choice == "1":
        os.remove(f"{account['username']}_session.json")
        log_message(f"✔ Session supprimée pour {account['username']}", Fore.GREEN)
        
        # Créer un dossier vide avec le nom du compte supprimé
        os.makedirs(f"{account['username']}_session", exist_ok=True)
        log_message(f"✔ Dossier créé pour {account['username']}: {account['username']}_session", Fore.GREEN)
        
        await handle_login_required_error(account) # Redemander les options
    elif choice == "2":
        password = input(Fore.YELLOW + f"Entrez le mot de passe pour {account['username']} : ")
        client_instagram = Client()
        try:
            # Connexion avec un appareil virtuel
            device_settings = get_system_info()
            client_instagram.device_settings = device_settings  # Appliquer les informations d'appareil virtuel
            client_instagram.login(account['username'], password)
            client_instagram.dump_settings(f"{account['username']}_session.json")
            log_message(f"✔ Connexion réussie pour {account['username']}", Fore.GREEN)

            # Restaurer et réutiliser le compte qui vient d'être reconnecté
            clients[account['username']] = client_instagram
            await handle_login_required_error(account) # Redemander les options
        except Exception as e:
            log_message(f"❌ Erreur de connexion pour {account['username']}: {e}", Fore.RED)
            await handle_login_required_error(account) # Redemander les options
    elif choice == "3":
        log_message(f"✔ Reprise des tâches normales pour {account['username']}", Fore.GREEN)
    else:
        log_message("❌ Choix invalide, veuillez réessayer.", Fore.RED)
        await handle_login_required_error(account)

async def send_message_with_delay(recipient, message):
    """Envoyer un message avec un délai aléatoire entre 0.2 et 3 secondes"""
    global last_message_sent, last_message_time, last_message_type
    
    # Attendre un délai aléatoire avant d'envoyer le message
    delay = random.uniform(0.2, 1.6)
    await asyncio.sleep(delay)
    
    await client.send_message(recipient, message)
    
    # Mettre à jour les variables globales
    last_message_sent = message
    last_message_time = time.time()
    last_message_type = "message"  # Type générique pour tous les messages

@client.on(events.NewMessage(from_users=bot_username))
async def handler(event):
    global response_received, current_account_index, instagram_accounts, last_message_sent, last_message_time, last_message_type
    
    # Réinitialiser le timer du dernier message
    last_message_time = time.time()
    
    message = event.message.message

    # Vérifier si le compte est en review ou a trop de warnings
    if ("🟡 Account" in message and "is on review now" in message) or ("🔴 Account" in message and "has too many warnings" in message):
        username = instagram_accounts[current_account_index]['username']
        log_message(f"❌ Compte de Point jaune est ne peut pas être utilisé: {username}", Fore.RED)
        os.remove(f"{username}_session.json")
        # Créer un dossier vide avec le nom du compte supprimé
        os.makedirs(f"{username}_session", exist_ok=True)
        instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
        await send_message_with_delay(bot_username, "🔙Back")
        await response_received.wait()
        return

    # Fonction pour extraire le shortcode et le convertir en ID de post
    def extract_shortcode_and_convert_to_post_id(url):
        if "/p/" in url:
            try:
                shortcode = url.split("/p/")[1].split("/")[0]
                alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
                base = len(alphabet)
                id_num = 0
                for char in shortcode:
                    id_num = id_num * base + alphabet.index(char)
                return f"Shortcode : {shortcode}", f"Post ID : {id_num}"
            except Exception as e:
                return None, f"Erreur lors de la conversion du post ID : {e}"
        else:
            return None, "URL invalide, aucun shortcode trouvé."

    # Fonction pour obtenir l'ID du média (post) à partir de l'URL du post
    def get_media_id_from_url(url):
        post_shortcode, post_id = extract_shortcode_and_convert_to_post_id(url)
        if post_id:
            return post_id.split(":")[1].strip()  # Supprime les espaces indésirables
        return None

    # Nouveau condition pour vérifier le message spécifique
    if "Use /support to contact us at any time you want. Feel free to write your suggestions and ideas. 😊" in message:
        await send_message_with_delay(bot_username, "📝Tasks📝")
        log_message("📝Tasks📝 envoyés au bot", Fore.GREEN)
        return

    if "⭕️ Please choose account from the list" in message:
        await send_message_with_delay(bot_username, "🔙Back")
        log_message("🔙Back envoyés au bot", Fore.GREEN)
        return

    if ("❗" in message) or ("▪️ Please give us your profile's username for tasks completing :" in message):
        username = instagram_accounts[current_account_index]['username']
        await send_message_with_delay(bot_username, username)
        log_message(f"{Fore.YELLOW}Username{Fore.WHITE}: {Fore.YELLOW}{username}{Fore.RESET}", Fore.YELLOW)
        response_received.set()
        return

    elif ("✅" in message) or ("Choose social network :" in message) or ("💎" in message):
        await send_message_with_delay(bot_username, "Instagram")
        log_message("Envoyé : Instagram", Fore.YELLOW)
        response_received.set()
        return

    elif "▪️ Link :" in message and "▪️ Action :" in message:
        try:
            link_match = re.search(r"▪️ Link :\s*(https://www.instagram.com/[^\s]+)", message)
            action_match = re.search(r"▪️ Action :\s*(.+)", message)

            if link_match and action_match:
                link = link_match.group(1)
                action = action_match.group(1)

                log_message(f"[🔗] :{link} |{action} ", Fore.CYAN)
                username = instagram_accounts[current_account_index]['username']
                client_instagram = clients[username]
                # Ajout d'une barre oblique à la fin si elle est absente
                if not link.endswith('/'):
                    link += '/'

                # Extraction de l'ID en fonction de l'action
                if action.lower() == "follow the profile":
                    # Extrait le username du lien, même sans "/" à la fin
                    try:
                        user_id = client_instagram.user_id_from_username(link.split("/")[-2])
                        if user_id:
                            log_message(f"{Fore.MAGENTA}[👤] USER ID : {Fore.WHITE}{user_id}", Fore.WHITE)
                            try:
                                client_instagram.user_follow(user_id)
                                log_message(f"[➕] Follow réussi", Fore.GREEN)
                                await send_message_with_delay(bot_username, "✅Completed")
                            except Exception as e:
                                if "challenge_required" in str(e):
                                    log_message(f"⛔Etapes Suplementaire rencontrée pour: {username} \n🔄Connecté Ce Compte a L'apk Instagram puis Reglé le  Problème\n", Fore.RED)
                                    instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                    await send_message_with_delay(bot_username, "🔙Back")
                                    await response_received.wait()
                                    return
                                elif "login_required" in str(e):
                                    os.remove(f"{username}_session.json")
                                    # Créer un dossier vide avec le nom du compte supprimé
                                    os.makedirs(f"{username}_session", exist_ok=True)
                                    instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                    await send_message_with_delay(bot_username, "🔙Back")
                                    await response_received.wait()
                                    return
                                log_message(f"❌ Erreur lors de l'action 'follow the profile': {e}", Fore.RED)
                                await send_message_with_delay(bot_username, "❌Skip")     
                    except Exception as e:
                        log_message(f"❌ Erreur lors de la récupération de l'ID utilisateur: {e}", Fore.RED)
                        await send_message_with_delay(bot_username, "❌Skip")

                elif action.lower() == "like the post below":
                    media_id = get_media_id_from_url(link)
                    if media_id:
                        log_message(f"{Fore.MAGENTA}[📸] POST ID : {Fore.WHITE}{media_id}", Fore.WHITE)
                        try:
                            client_instagram.media_like(media_id)
                            log_message(f"[❤] Like réussi", Fore.GREEN)
                            await send_message_with_delay(bot_username, "✅Completed")
                        except Exception as e:
                            if "challenge_required" in str(e):
                                log_message(f"⛔Etapes Suplementaire rencontrée pour: {username} \n🔄Connecté Ce Compte a L'apk Instagra et Reglé le Problème\n")
                                instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                await send_message_with_delay(bot_username, "🔙Back")
                                await response_received.wait()
                                return
                            elif "login_required" in str(e):
                                os.remove(f"{username}_session.json")
                                # Créer un dossier vide avec le nom du compte supprimé
                                os.makedirs(f"{username}_session", exist_ok=True)
                                instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                await send_message_with_delay(bot_username, "🔙Back")
                                await response_received.wait()
                                return
                            elif "feedback_required" in str(e):
                                log_message(f"❌ Erreur 'feedback_required' pour {username}, suppression du compte.", Fore.RED)
                                os.remove(f"{username}_session.json")
                                # Créer un dossier vide avec le nom du compte supprimé
                                os.makedirs(f"{username}_session", exist_ok=True)
                                instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                await send_message_with_delay(bot_username, "🔙Back")
                                await response_received.wait()
                                return
                            elif "Sorry, this media has been deleted" in str(e):
                                log_message(f"❌ Erreur : Ce média a été supprimé", Fore.RED) 
                                await send_message_with_delay(bot_username, "❌Skip")
                                return

                elif "leave the comment" in action.lower():
                    media_id = get_media_id_from_url(link)
                    if media_id:
                        async for msg in client.iter_messages(bot_username, limit=2):
                            if msg != event.message:
                                comment = msg.text.strip()
                                comment = re.sub(r'`{3,}', '', comment)
                                log_message(f"{Fore.MAGENTA}[📸] POST ID : {Fore.WHITE}{media_id}", Fore.WHITE)
                                try:
                                    client_instagram.media_comment(media_id, comment)
                                    log_message(f"[💬] Commentaire réussi", Fore.GREEN)
                                    await send_message_with_delay(bot_username, "✅Completed")
                                except Exception as e:
                                    if "challenge_required" in str(e):
                                        log_message(f"⛔Etapes Suplementaire rencontrée pour: {username} \n🔄Connecté Ce Compte a L'apk Instagram,puis reglé le Problème\n")
                                        instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                        await send_message_with_delay(bot_username, "🔙Back")
                                        await response_received.wait()
                                        return
                                    if "login_required" in str(e):
                                        os.remove(f"{username}_session.json")
                                        # Créer un dossier vide avec le nom du compte supprimé
                                        os.makedirs(f"{username}_session", exist_ok=True)
                                        instagram_accounts = [account for account in instagram_accounts if account["username"] != username]
                                        await send_message_with_delay(bot_username, "🔙Back")
                                        await response_received.wait()
                                        return
                                    elif "Sorry, this media has been deleted" in str(e):
                                        log_message(f"❌ Erreur : Ce média a été supprimé", Fore.RED)
                                        await send_message_with_delay(bot_username, "❌Skip")
                                        return
                                    log_message(f"❌ Erreur lors de l'action 'leave the comment': {e}", Fore.RED)
                                    await send_message_with_delay(bot_username, "❌Skip")
                            break
                    else:
                        log_message("❌ Aucun commentaire trouvé", Fore.RED)
                        await send_message_with_delay(bot_username, "❌Skip")
                else:
                    log_message(f"Tache : {action}. ", Fore.BLUE)
                    log_message("[👁]View réussi", Fore.GREEN)
                    await send_message_with_delay(bot_username, "✅Completed")
            else:
                log_message("❌ Erreur : Impossible de traiter le message reçu, format inattendu.", Fore.RED)
                await send_message_with_delay(bot_username, "❌Skip")

        except Exception as e:
            log_message(f"❌ Erreur lors du traitement de la tâche : {e}", Fore.RED)
            await send_message_with_delay(bot_username, "❌Skip")

        response_received.set()
        return

    elif "⭕️ Sorry, but there are no active tasks at the moment." in message:
        current_account_index = (current_account_index + 1) % len(instagram_accounts)
        await send_message_with_delay(bot_username, "Instagram")
        response_received.set()

# Fonction pour vérifier le délai d'une minute sans message et réenvoyer le dernier message si nécessaire
async def check_last_message():
    global last_message_sent, last_message_time, last_message_type
    while True:
        current_time = time.time()
        # Vérifier si 1 minute s'est écoulée depuis le dernier message
        if (current_time - last_message_time > 60 and last_message_sent is not None):
            log_message(f"⚠️ Aucune réponse depuis 1 minute, réenvoi du dernier message : {last_message_sent}", Fore.YELLOW)
            
            # Réenvoyer le dernier message avec un délai aléatoire
            delay = random.uniform(0.2, 2.0)
            await asyncio.sleep(delay)
            
            await client.send_message(bot_username, last_message_sent)
            last_message_time = time.time()  # Réinitialiser le délai après l'envoi du message
        
        await asyncio.sleep(1)  # Vérifier toutes les 10 secondes

# Fonction pour synchroniser les comptes Instagram toutes les 2 minutes
async def sync_instagram_accounts():
    global instagram_accounts, clients
    while True:
        await asyncio.sleep(60)  # Attendre 2 minutes

        # Charger les nouveaux comptes Instagram
        new_accounts = load_instagram_accounts()

        # Filtrer les nouveaux comptes qui ne sont pas déjà dans la liste
        new_accounts = [account for account in new_accounts if account not in instagram_accounts]

        if new_accounts:
            # Ajouter les nouveaux comptes à la liste
            instagram_accounts.extend(new_accounts)

            # Trier la liste par ordre alphabétique
            instagram_accounts.sort(key=lambda x: x['username'])

            log_message(f"🔄 {len(new_accounts)} nouveaux comptes Instagram synchronisés.", Fore.GREEN)
            for account in new_accounts:
                log_message(f"🆕 Compte ajouté : {account['username']}", Fore.CYAN)

                # Connecter le nouveau compte et l'ajouter au dictionnaire clients
                if login_instagram(account):
                    log_message(f"✔ Connexion réussie pour {account['username']}", Fore.GREEN)
                else:
                    log_message(f"❌ Échec de la connexion pour {account['username']}", Fore.RED)

# Fonction pour vérifier le statut de l'utilisateur toutes les 2 minutes
async def check_user_status_periodically():
    global user_id
    while True:
        await asyncio.sleep(60)  # Attendre 2 minutes

        # Récupérer les données depuis GitHub
        try:
            response = requests.get(STATUS_URL)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            log_message(f"❌ Erreur lors de la récupération des données du serveur : {e}", Fore.RED)
            continue  # Continuer même en cas d'erreur

        # Vérifier le statut de l'utilisateur
        user_found = False
        for script in data.get("scripts", []):
            if script.get("id") == user_id:
                user_found = True
                status = script.get("status")
                countdown_start = script.get("countdown_start_time")

                # Si le statut est inactif ou que le temps est écoulé
                if status != "active":
                    log_message("❌ Statut utilisateur inactif. Arrêt du script.", Fore.RED)
                    exit()

                # Convertir le timestamp en temps restant
                countdown_time, expired = convert_timestamp_to_time_left(countdown_start)
                if expired:
                    log_message("❌ Abonnement expiré. Arrêt du script.", Fore.RED)
                    exit()

                break  # Sortir de la boucle une fois l'utilisateur trouvé

        if not user_found:
            log_message(f"❌ ID {user_id} non trouvé dans les données.", Fore.RED)
            exit()

async def main():
    print_banner()
    user_choice = get_user_choice()
    if user_choice != "tasks":
        print(Fore.RED + "Le script ne peut pas démarrer sans avoir sélectionné 'Tasks'.")
        return

    try:
        await client.start(phone_number)
        log_message("✅ Connecté à Telegram avec succès", Fore.GREEN)
    except Exception as e:
        log_message(f"❌ Erreur de connexion à Telegram : {e}", Fore.RED)
        return

    global instagram_accounts
    instagram_accounts = connect_instagram_accounts()

    await send_message_with_delay(bot_username, "📝Tasks📝")
    log_message("📝Tasks📝 envoyés au bot", Fore.GREEN)

    # Lancer la vérification en parallèle
    asyncio.create_task(check_last_message())
    asyncio.create_task(sync_instagram_accounts())
    asyncio.create_task(check_user_status_periodically())

    await response_received.wait()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
