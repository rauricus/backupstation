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

HEADER_HEIGHT = 30
ROW_HEIGHT = 20
TABLE_ROW_HEIGHT = 30
FOOTER_HEIGHT = 20

font18 = ImageFont.truetype('Font.ttc', 18)
font24 = ImageFont.truetype('Font.ttc', 24)
font35 = ImageFont.truetype('Font.ttc', 35)


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
    
    # Calculate the bounding box of the text to be drawn
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    
    # Calculate the position at which to draw the text so that it is centered
    x_position = (image_width - text_width) // 2

    # Draw the text on the image
    draw.text((x_position, y_position), text, font=font, fill=fill)


def draw_table(draw, image_width, headers, data, font, start_y, fill=0):
    """
    Draws a table with headers and data.

    :param draw: ImageDraw object to draw on.
    :param image_width: Width of the image.
    :param headers: List of header strings.
    :param data: List of data rows, where each row is a list of column values.
    :param font: Font object to use for the text.
    :param start_y: The y position to start drawing the table.
    :param fill: Color to use for the text.
    """
     # Calculate the column widths based on the header widths
    col_widths = [draw.textbbox((0, 0), header, font=font)[2] for header in headers]
    
    # Ensure column widths can accommodate the widest text in each column
    for row in data:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths[i], draw.textbbox((0, 0), col, font=font)[2])
    
    # Calculate x positions for each column
    x_positions = [sum(col_widths[:i]) for i in range(len(headers))]

    # Draw the headers
    for i, header in enumerate(headers):
        draw.text((x_positions[i], start_y), header, font=font, fill=fill)
    
    # Draw a separator line below the headers
    draw.line((0, start_y + TABLE_ROW_HEIGHT - 5, image_width, start_y + TABLE_ROW_HEIGHT - 5), fill=fill)
    
    # Draw the data rows
    for row_num, row in enumerate(data):
        y_position = start_y + (row_num + 1) * TABLE_ROW_HEIGHT
        for col_num, col in enumerate(row):
            draw.text((x_positions[col_num], y_position), col, font=font, fill=fill)




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
    
    logging.debug("Drawing initial background image...")

    # Create a new blank image
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

    # Create a drawing object
    draw = ImageDraw.Draw(Himage)

    # Draw black background bars on top and bottom
    draw.rectangle((0, 0, epd.width, HEADER_HEIGHT), outline=0, fill=0)
    draw.rectangle((0, epd.height - FOOTER_HEIGHT, epd.width, epd.height), outline=0, fill=0)

    # Draw the header text on the image
    draw_centered_text(draw, epd.width, epd.height, "Backup Station", font24, 0, fill=255)

    # Display the image on the ePaper display
    epd.display(epd.getbuffer(Himage))

    time.sleep(2)


    # --- Backup for all mounted directories

    dir_list = os.listdir(BACKUP_TARGETS_BASE_DIR)     # get a list of all mounted directories

    data = []

    ypos = 30   # set the yposition of the ePaper text output

    logging.info("Starting backup...")
    for dir_name in dir_list:
       
        # Show name of directory we're about to back up
        draw.text((5,ypos), dir_name+": ", font=font18, fill=0)
        epd.display(epd.getbuffer(Himage))

        logging.info(dir_name+": ")

        time.sleep(2)

        # === Run the actual backup ===
        subprocess.run("/usr/bin/rdiff-backup -v 0 --print-statistics "+ BACKUP_TARGETS_BASE_DIR+dir_name+" "+HDD_BASE_DIR+dir_name + " > log.txt", shell=True)

        # Extract results in log file and write to screen
        f = open("log.txt", "r")
        lines = f.readlines()
        result_string = ""

        for line in lines:
            cols = line.split()
            if cols[0] == 'NewFiles':
                new_files = cols[1]
                result_string = result_string+'New: '+ new_files
            if cols[0] == 'DeletedFiles':
                deleted_files = cols[1]
                result_string = result_string+' Del: ' + deleted_files
            if cols[0] == 'ChangedFiles':
                changed_files = cols[1]
                result_string = result_string+' Chgd: ' + changed_files
        
        draw.text((110, ypos), result_string, font=font18, fill=0)
        epd.display(epd.getbuffer(Himage))

        logging.info(result_string)

        time.sleep(2)

        # Remember data for final summary
        data.append([dir_name,new_files, changed_files, deleted_files])

        ypos = ypos + ROW_HEIGHT

    logging.info("Backup done.")

    # --- Delete screen and write summary in table

    headers = ["Ort", "Neu", "Geändert", "Gelöscht"]

    # Draw a white rectangle over the specified portion to clear it
    draw.rectangle((0, HEADER_HEIGHT, epd.width, epd.height - FOOTER_HEIGHT), outline=255, fill=255)

    # Use the function to draw the table
    draw_table(draw, epd.width, headers, data, font18, HEADER_HEIGHT+20, fill=0)

    # Display the image on the ePaper display
    epd.display(epd.getbuffer(Himage))


    # ---  Write footer and shutdown

    # Compute date and time backup ended.
    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    current_date = today.strftime("%d-%m-%Y ");

    # Write date centered in footer area.
    footer_text = 'Letztes Backup: '+current_date + current_time
    draw_centered_text(draw, epd.width, epd.height, footer_text, font18, epd.height-FOOTER_HEIGHT + 1, fill=255)

    # Display the image on the ePaper display
    epd.display(epd.getbuffer(Himage))

    time.sleep(2)

    # ---  Shutdown
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

