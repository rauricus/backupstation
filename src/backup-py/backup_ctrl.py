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

#============  WiringPi Setup for Mode Switch connected between GPIO2 and GND =====================
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(2,0);      #GPIO-Pin 2 becomes in input for mode switching
wiringpi.pinMode(18,1);     #GPIO-Pin 18 becomes an output for LED status display
wiringpi.pullUpDnControl(2, 1)    #GPIO-Pin 2 is programmed to pull-down


wiringpi.digitalWrite(18,1);   # LED on

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


#============ Main Flow ===========================================================================

if not wiringpi.digitalRead(2):
    logging.info("No backup takes place.")
    wiringpi.digitalWrite(18,0);   # LED off
    exit(0);    #if the GPIO is not actively pulled down the script exits here


try:
    logging.debug("Starting ePaper display...")
    
    epd = epd4in2.EPD()
    epd.init()
    epd.Clear()
    time.sleep(3)
    
    font24 = ImageFont.truetype('Font.ttc', 24)
    font18 = ImageFont.truetype('Font.ttc', 18)
    font35 = ImageFont.truetype('Font.ttc', 35)
    
    logging.debug("Drawing initial background image...")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.rectangle((0, 0, 400, 30), outline = 0, fill=0)
    draw.rectangle((0, 280, 400, 300), outline = 0, fill=0)
    draw.text((120, 0), 'Backup Station', font = font24, fill = 255)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    #==================== Execute the backup for all mounted directories
    dir_list = os.listdir(BACKUP_TARGETS_BASE_DIR)     # get a list of all mounted directories
    ypos = 30   # set the yposition of the ePaper text output

    logging.info("Starting backup...")
    for dir in dir_list:
       backup(dir)
       ypos = ypos + 20

    logging.info("Backup done.")

    #===================  Write Footer on ePaper and shutdown
    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    current_date = today.strftime("%d-%m-%Y ");
    draw.text((60, 281), 'Letztes Backup: '+current_date + current_time , font = font18, fill = 255)

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

