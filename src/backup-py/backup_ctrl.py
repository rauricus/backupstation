#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

import logging
import os
import subprocess
import wiringpi
from waveshare_epd import epd4in2
from datetime import datetime
from datetime import date
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.INFO)

#==================================== Global Settings =============================================
BACKUP_TARGETS_BASE_DIR = "/mnt/network/"
HDD_BASE_DIR = "/mnt/ext_hdd/"


#================ Backup function =============================================================
def backup(dir_name):
   draw.text((5,ypos), dir_name+": ", font=font18, fill=0)
   print(dir_name+": ")
   epd.display(epd.getbuffer(Himage))
   time.sleep(2)

   subprocess.run("/usr/bin/rdiff-backup -v 0 --print-statistics "+ BACKUP_TARGETS_BASE_DIR+dir_name+" "+HDD_BASE_DIR+dir_name + " > log.txt", shell=True)
   f = open("log.txt", "r")
   lines = f.readlines()
   out_string = ""

   for line in lines:
       cols = line.split()
       if cols[0] == 'NewFiles':
           out_string = out_string+'New: '+cols[1]
       if cols[0] == 'DeletedFiles':
           out_string = out_string+' Del: ' + cols[1]
       if cols[0] == 'ChangedFiles':
           out_string = out_string+' Chgd: ' + cols[1]
  
   draw.text((110, ypos), out_string, font=font18, fill=0)
   epd.display(epd.getbuffer(Himage))
   time.sleep(2)

   print(out_string)


#============ Utility functions ==============================================================
def draw_centered_text(draw, image_width, image_height, text, font, y_position, fill=255):
    """
    Draws text centered horizontally on the image at the specified y_position.

    :param draw: ImageDraw object to draw on.
    :param image_width: Width of the image.
    :param image_height: Height of the image (not used in this function, but included for completeness).
    :param text: The text to draw.
    :param font: Font object to use for the text.
    :param y_position: The y position to draw the text at.
    :param fill: Color to use for the text.
    """
    # Calculate the width and height of the text to be drawn
    text_width, text_height = draw.textsize(text, font=font)
    
    # Calculate the position at which to draw the text so that it is centered
    x_position = (image_width - text_width) // 2

    # Draw the text on the image
    draw.text((x_position, y_position), text, font=font, fill=fill)



#============ Main ===========================================================================

# --- WiringPi setup for Mode Switch connected between GPIO2 and GND ---
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(2,0);      #GPIO-Pin 2 becomes in input for mode switching
wiringpi.pinMode(18,1);     #GPIO-Pin 18 becomes an output for LED status display
wiringpi.pullUpDnControl(2, 1)    #GPIO-Pin 2 is programmed to pull-down


wiringpi.digitalWrite(18,1);   # LED on


# --- Main flow ---
if not wiringpi.digitalRead(2):
    logging.info("No backup takes place.")
    wiringpi.digitalWrite(18,0);   # LED off
    exit(0);    #if the GPIO is not actively pulled down the script exits here


try:

    # ---  Write header

    logging.debug("Starting ePaper display...")
    
    epd = epd4in2.EPD()
    epd.init()
    epd.Clear()
    time.sleep(3)
    
    font24 = ImageFont.truetype('Font.ttc', 24)
    font18 = ImageFont.truetype('Font.ttc', 18)
    font35 = ImageFont.truetype('Font.ttc', 35)
    
    logging.debug("Drawing initial background image...")

    # Create a new blank image
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

    # Create a drawing object
    draw = ImageDraw.Draw(Himage)

    # Draw black background bars on top and bottom
    draw.rectangle((0, 0, epd.width, 30), outline=0, fill=0)
    draw.rectangle((0, epd.height - 20, epd.width, epd.height), outline=0, fill=0)

    # Draw the header text on the image
    draw_centered_text(draw, epd.width, epd.height, "Backup Station", font24, 0, fill=255)

    # Display the image on the ePaper display
    epd.display(epd.getbuffer(Himage))

    time.sleep(2)


    # --- Backup for all mounted directories

    dir_list = os.listdir(BACKUP_TARGETS_BASE_DIR)     # get a list of all mounted directories
    ypos = 30   # set the yposition of the ePaper text output

    logging.info("Starting backup...")
    for dir in dir_list:
       backup(dir)
       ypos = ypos + 20

    logging.info("Backup done.")


    # ---  Write footer and shutdown

    # Compute date and time backup ended.
    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    current_date = today.strftime("%d-%m-%Y ");

    # Write date centered in footer area.
    draw_centered_text(draw, epd.width, epd.height, 'Letztes Backup: '+current_date + current_time, font18, epd.height-20 + 1, fill=255)

    # Display the image on the ePaper display
    epd.display(epd.getbuffer(Himage))

    time.sleep(2)

    if not wiringpi.digitalRead(2):
        logging.info("Switch changed, not shutting down.")
        wiringpi.digitalWrite(18,0);   # LED off
        exit(0);    # if the GPIO is not actively pulled down the scrips exits here

    logging.info("Run complete, shutting down.")
    os.system("sudo shutdown --poweroff now");  #If the switch in in Backup-Mode the Raspi will be shut down here
    
except IOError as e:
    logging.error(e)
    exit(1)     # exit with general error
    
except KeyboardInterrupt:    
    logging.info("Keyboard interrupt")
    epd4in2.epdconfig.module_exit()
    wiringpi.digitalWrite(18,0);   # LED off
    exit(130)   # exit with "script terminated by ctrl-c"

