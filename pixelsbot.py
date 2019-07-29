# -*- coding: utf-8 -*-
import time
import datetime
import logging
from threading import RLock
from threading import Thread
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import os
import sys
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.error import TelegramError
from emoji import emojize
import html
from firebase_admin import db

#ref = db.reference('server/saving-data/fireblog')
#users_ref = ref.child('users')

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level = logging.INFO)

logger = logging.getLogger(__name__)

# Building buttons menu for every occasion 
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# emojis
ethumb = emojize(":thumbsup: ", use_aliases=True)
eblacksquare = emojize(":black_small_square: ", use_aliases=True)
earrowfwd = emojize(":arrow_forward: ", use_aliases=True)
ebangbang = emojize(":bangbang: ", use_aliases=True)
eheart = emojize(":heart: ", use_aliases=True)
ebluediamond = emojize(":small_blue_diamond: ", use_aliases=True)
eredtriangle = emojize(":small_red_triangle_down: ", use_aliases=True) 
esmile = emojize(":smile: ", use_aliases=True) 
ecross = emojize(":x: ", use_aliases = True)
efastfwd = emojize(":fast_forward: ", use_aliases=True)
estar = emojize(":star2: ", use_aliases=True)
eorangedimaond = emojize(":small_orange_diamond: ", use_aliases=True)
ewarning = emojize(":warning: ", use_aliases=True)
equestion = emojize(":question: ", use_aliases=True)
esparkles = emojize(":sparkles: ", use_aliases=True)
enoentry = emojize(":no_entry: ", use_aliases=True)
etada = emojize(":tada: ", use_aliases=True)
einfo = emojize(":information_source: ", use_aliases=True)
eexclaim = emojize(":heavy_exclamation_mark: ", use_aliases=True)
etick = emojize(":white_check_mark: ", use_aliases=True)
earrowleft = emojize(":arrow_left: ", use_aliases=True)
earrowright = emojize(":arrow_right: ", use_aliases=True)
eok = emojize(":ok: ", use_aliases=True)
ezap = emojize(":zap: ", use_aliases=True)


#Set up Google Spreadsheet Credentials and gspread token
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'RC4FOCPixelsBot-23acce0b35a4.json', scope)
http = httplib2.Http()
credentials.authorize(http)
gc = gspread.authorize(credentials)

# get relevant spreadsheets
DAY2SHEET = gc.open("Points System").get_worksheet(1)
spreadsheets = {
    "Day2": {
        "spreadsheet": DAY2SHEET,
    }
}

#Set up telegram token 
TELEGRAM_TOKEN = os.environ['RC4FOCPIXELSBOT_TOKEN'] 

admin_group_id = '-251537951'
allowed_channel = '@focpixelstestchannel123' 
allowed_user_ids = [250741897, 77345091, 417794228] #cpf, yh, aidan

def start(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    logger.info(update.message.text.strip())
    welcome_text = "Hello there! Hope you are enjoying your RC4 FOC Camp so far! :)\n\nUnfortunately, it is no fun speaking with me as all I say is this exact text...\n\nBut I do help to update your base ownerships once in a while for Cartoon Wars!"

    bot.send_message(text = welcome_text,
                    parse_mode=ParseMode.HTML,
                    chat_id = chatid)

    return 



def update(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    logger.info(update.message.text.strip())

    # initialise sheet 
    CARTOONWARS_SHEET = spreadsheets["Day2"]["spreadsheet"]

    # KEY LIST OF STATIONS; Index matters:
    All_Stations_List = CARTOONWARS_SHEET.row_values(2)
    All_Stations_List = list(filter(None, All_Stations_List))
    Leaderboard_Stations_List = All_Stations_List[:15]
    Arena_Stations_List = All_Stations_List[15:]

    Leaderboard_Dict = {}
    for station in Leaderboard_Stations_List:
        Leaderboard_Dict[station] = {}
        Leaderboard_Dict[station]["Index"] = station.split('.')[0]
        Leaderboard_Dict[station]["RealScoreList1"] = []
        Leaderboard_Dict[station]["RealScoreList2"] = []
        Leaderboard_Dict[station]["OwnerClan"] = ''


    # decipher preference rank first
    preference_row = CARTOONWARS_SHEET.row_values(3)
    possible_preferences = ['1max', '1min', '2max', '2min']
    units_row = CARTOONWARS_SHEET.row_values(4)

    # Tag station name to ScoreList1 and ScoreList2 based on rank, to Criteria (min or max), and Units
    # Convert all spreadsheet columns to raw data lists for ScoreList1 and ScoreList2 (if any) first
    current_station_pos = -1
    for i, pref in enumerate(preference_row):
        if pref in possible_preferences:
            rank = pref[0] # rank is either 1 or 2 
            criteria = pref[1:] # criteria is either max or min
            if rank == '1':
                current_station_pos += 1
                current_station = Leaderboard_Stations_List[current_station_pos]
                ScoreList1_Col_Num = i + 1
                Leaderboard_Dict[current_station]["ScoreList1"] = CARTOONWARS_SHEET.col_values(ScoreList1_Col_Num)
                Leaderboard_Dict[current_station]["Crit_ScoreList1"] = criteria
                Leaderboard_Dict[current_station]["Units_ScoreList1"] = CARTOONWARS_SHEET.cell(4, ScoreList1_Col_Num).value # corresponding units is in row 4
            elif rank == '2':
                current_station = Leaderboard_Stations_List[current_station_pos]
                ScoreList2_Col_Num = i + 1
                Leaderboard_Dict[current_station]["ScoreList2"] = CARTOONWARS_SHEET.col_values(ScoreList2_Col_Num)
                Leaderboard_Dict[current_station]["Crit_ScoreList2"] = criteria
                Leaderboard_Dict[current_station]["Units_ScoreList2"] = CARTOONWARS_SHEET.cell(4, ScoreList2_Col_Num).value # corresponding units is in row 4
            else: 
                pass 
        else:
            pass

    # From here, we don't deal with spreadsheet index or notation anymore 
    # Take out only the OG names and relevant scorelists data and update the ScoreList for each station name accordingly 
    OG_Col = CARTOONWARS_SHEET.col_values(2)
    OG_Pixels_Col = CARTOONWARS_SHEET.col_values(3)

    OG_List = []
    Clan_List = ["Monsters Inc", "Monsters Inc", "Monsters Inc", "Monsters Inc", 
                "Incredibles", "Incredibles", "Incredibles", "Incredibles",
                "Avatar", "Avatar", "Avatar", "Avatar", 
                "Scooby Doo", "Scooby Doo", "Scooby Doo", "Scooby Doo", 
                "Adventure Time", "Adventure Time", "Adventure Time", "Adventure Time"]
    Pixel_List = []

    # Start gathering leaderboard text
    final_leaderboard_text = ""

    # start at index 5 
    for i in range(5, len(OG_Col), 6):
        OG_List.extend(OG_Col[i:i+4])
        Pixel_List.extend(OG_Pixels_Col[i:i+4])
        for station in Leaderboard_Dict:
            Current_ScoreList1 = Leaderboard_Dict[station]["ScoreList1"]
            Leaderboard_Dict[station]["RealScoreList1"].extend(Current_ScoreList1[i:i+4])
            try: 
                Current_ScoreList2 = Leaderboard_Dict[station]["ScoreList2"]
                Leaderboard_Dict[station]["RealScoreList2"].extend(Current_ScoreList2[i:i+4])
            except KeyError: # due to no ScoreList2
                pass 

    # For every station, convert RealScoreLists all to float, compare max or min 
    for station in Leaderboard_Dict:
        Leaderboard_Dict[station]["RealScoreList1"] = [float(i) for i in Leaderboard_Dict[station]["RealScoreList1"]] # convert to float to rank
        scorelist1 = Leaderboard_Dict[station]["RealScoreList1"]
        criteria1 = Leaderboard_Dict[station]["Crit_ScoreList1"] # get criteria (max or min) to compare
        units1 = Leaderboard_Dict[station]["Units_ScoreList1"] # get units to print 
        
        logger.info(station)
        logger.info(scorelist1)
        logger.info(criteria1)
        logger.info(units1)

        if criteria1 == 'max':
            finalscore1 = max(scorelist1)
            if finalscore1 == 0:
                finalscore1 = "UNCLAIMED" # if everyone is 0 initially

        else: # for min criteria
            try: 
                finalscore1 = min(i for i in scorelist1 if i > 0)  # reject negatives and 0 which are admin values
                logger.info(finalscore1)
            except ValueError: # if everyone is 0 initially
                finalscore1 = "UNCLAIMED"
                
        if finalscore1 != "UNCLAIMED": # for normal route where there is a clear finalscore1
            index_score1_repeats = [i for i, j in enumerate(scorelist1) if j == finalscore1] # this is a list of all the indexes 

            if len(index_score1_repeats) > 1: # if there are more than 1 OG with this first scorelist, we use finalscore2
                try: 
                    Leaderboard_Dict[station]["RealScoreList2"] = [float(i) for i in Leaderboard_Dict[station]["RealScoreList2"]]
                    scorelist2 = Leaderboard_Dict[station]["RealScoreList2"]
                    criteria2 = Leaderboard_Dict[station]["Crit_ScoreList2"] # get criteria (max or min) to compare
                    units2 = Leaderboard_Dict[station]["Units_ScoreList2"] # get units to print 
                    
                    logger.info("TESTING 123")
                    logger.info(scorelist2)
                    logger.info(criteria2)
                    logger.info(units2)

                    scores2_to_compare = [scorelist2[i] for i in index_score1_repeats] # sieve out winning OGs from finalscore1 to compare score2
                    
                    if criteria2 == 'max':
                        finalscore2 = max(scores2_to_compare)
                        logger.info(finalscore2)

                        final_index = scorelist2.index(finalscore2) # get the final index based on index of the finalscore2 instead of finalscore1
                        owner_og = OG_List[final_index]
                        owner_clan = Clan_List[final_index]
                        stationtext = eblacksquare + "<b>" + station + "</b>: " + owner_og + ", " + owner_clan + " (" + str(finalscore1) + " " + units1 + ", " + str(finalscore2) + " " + units2 + ")\n"
                        Leaderboard_Dict[station]["OwnerClan"] = owner_clan
                        final_leaderboard_text += stationtext

                    else: # for min criteria
                        try:
                            finalscore2 = min(i for i in scores2_to_compare if i > 0)  # reject negatives and 0 which are admin values
                            logger.info(finalscore2)

                            final_index = scorelist2.index(finalscore2) # get the final index based on index of the finalscore2 instead of finalscore1
                            owner_og = OG_List[final_index]
                            owner_clan = Clan_List[final_index]
                            stationtext = eblacksquare + "<b>" + station + "</b>: " + owner_og + ", " + owner_clan + " (" + str(finalscore1) + " " + units1 + ", " + str(finalscore2) + " " + units2 + ")\n"
                            Leaderboard_Dict[station]["OwnerClan"] = owner_clan
                            final_leaderboard_text += stationtext

                        except ValueError: # if everyone is 0
                            stationtext = eblacksquare + "<b>" + station + "</b>: " + "UNCLAIMED\n"
                            final_leaderboard_text += stationtext

                except KeyError: # due to no ScoreList2
                    stationtext = eblacksquare + "<b>" + station + "</b>: " + "ERROR\n"
                    final_leaderboard_text += stationtext

            else: # if there is only 1 OG with clear win in first list, we use finalscore1
                final_index = scorelist1.index(finalscore1)
                owner_og = OG_List[final_index]
                owner_clan = Clan_List[final_index]
                stationtext = eblacksquare + "<b>" + station + "</b>: " + owner_og + ", " + owner_clan + " (" + str(finalscore1) + " " + units1 + ")\n"
                logger.info(stationtext)
                Leaderboard_Dict[station]["OwnerClan"] = owner_clan
                final_leaderboard_text += stationtext

        else: # will show unclaimed by default if the first scorelist1 doesnt even have any value yet
            stationtext = eblacksquare + "<b>" + station + "</b>: " + "UNCLAIMED\n"
            final_leaderboard_text += stationtext


    ###############################################################
    # Now for Arena bases!
    OG_List = [] # reinitialise
    
    Arena_Dict = {}
    for station in Arena_Stations_List:
        Arena_Dict[station] = {}
        Arena_Dict[station]["RealOwnershipChecklist"] = []
        Arena_Dict[station]["Index"] = station.split('.')[0]
        Arena_Dict[station]["Owner"] = ''

    arena_mark_row = CARTOONWARS_SHEET.row_values(5) # to check for "OWNED BY" LABEL

    # Tag arena base to ownership check list 
    current_station_pos = -1
    for i, pref in enumerate(arena_mark_row):
        if pref == 'OWNED BY':
            current_station_pos += 1
            current_station = Arena_Stations_List[current_station_pos]
            Ownership_Checklist_Col_Num = i + 1
            Arena_Dict[current_station]["OwnershipChecklist"] = CARTOONWARS_SHEET.col_values(Ownership_Checklist_Col_Num)
        else:
            pass
    
    # start at index 5 
    final_arena_text = ''
    for i in range(5, len(OG_Col), 6):
        OG_List.extend(OG_Col[i:i+4])
        for station in Arena_Dict:
            OwnershipChecklist = Arena_Dict[station]["OwnershipChecklist"] 
            Arena_Dict[station]["RealOwnershipChecklist"].extend(OwnershipChecklist[i:i+4])
    
    for station in Arena_Dict:
        FinalOwnershipChecklist = Arena_Dict[station]["RealOwnershipChecklist"] 
        try: 
            final_index = FinalOwnershipChecklist.index('1') # only OG with index 1 is current owner
            owner_og = OG_List[final_index]
            owner_clan = Clan_List[final_index]
            Arena_Dict[station]["OwnerClan"] = owner_clan
            stationtext = ebluediamond + "<b>" + station + " Arena Base</b>: " + owner_og + ", " + owner_clan + "\n"
        except ValueError: # no index 1 at all 
            stationtext = ebluediamond + "<b>" + station + " Arena Base</b>: UNCLAIMED ERROR" +  "\n"
        final_arena_text += stationtext

    # Finally, compile both messages together
    final_send_text = esparkles + "<b>Latest Base Ownwership Update</b>\n\n"
    final_send_text += final_arena_text + "\n" + final_leaderboard_text
    final_send_text += "\nBase ownerships are automatically updated by @RC4FOCPixelsBot. This may not be the most updated version."

    bot.send_message(text = final_send_text,
                    parse_mode=ParseMode.HTML,
                    chat_id = allowed_channel)

    # Compile list of owner clans from both leaderboard and arena sides:
    Compiled_Ownership_Dict = {}
    Compiled_Ownership_Dict["bases"] = {}
    for station in Arena_Dict:
        index = "square" + Arena_Dict[station]["Index"] 
        if Arena_Dict[station]["OwnerClan"] == 'Monsters Inc':
            colour = 'green'
        elif Arena_Dict[station]["OwnerClan"] == 'Avatar':
            colour = 'blue'
        elif Arena_Dict[station]["OwnerClan"] == 'Incredibles':
            colour = 'red'
        elif Arena_Dict[station]["OwnerClan"] == 'Scooby Doo':
            colour = 'purple'
        elif Arena_Dict[station]["OwnerClan"] == 'Adventure Time':
            colour = 'yellow'
        else:
            colour = 'white'
        Compiled_Ownership_Dict["bases"][index] = {}
        Compiled_Ownership_Dict["bases"][index]["currentColour"] = colour

    for station in Leaderboard_Dict:
        index = "square" + Leaderboard_Dict[station]["Index"] 
        if Leaderboard_Dict[station]["OwnerClan"] == 'Monsters Inc':
            colour = 'green'
        elif Leaderboard_Dict[station]["OwnerClan"] == 'Avatar':
            colour = 'blue'
        elif Leaderboard_Dict[station]["OwnerClan"] == 'Incredibles':
            colour = 'red'
        elif Leaderboard_Dict[station]["OwnerClan"] == 'Scooby Doo':
            colour = 'purple'
        elif Leaderboard_Dict[station]["OwnerClan"] == 'Adventure Time':
            colour = 'yellow'
        else:
            colour = 'white'
        Compiled_Ownership_Dict["bases"][index] = {}
        Compiled_Ownership_Dict["bases"][index]["currentColour"] = colour
    


    logger.info(Compiled_Ownership_Dict)

    return 


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def update_token(bot, job):
    global credentials
    global http
    global gc
    refresh_credentials()


def refresh_credentials():
    global credentials
    global gc
    global http
    if credentials.access_token_expired:
        logger.info("New gspread token is being generated")
        # credentials.refresh(http)
        # gc = gspread.authorize(credentials)
        gc.login()

    
def main():   
    updater = Updater(TELEGRAM_TOKEN)    
    # get job queue
    job_queue = updater.job_queue    
    # refresh update gspread token regularly
    job_queue.run_repeating(update_token, interval=60, first=60) 
          
    # dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('update', update, filters=Filters.chat(chat_id = allowed_user_ids)))

    # logs all errors 
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
