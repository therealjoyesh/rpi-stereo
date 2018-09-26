# RPi Stereo 1.0
# Programmed by Joyesh
# For use with a Adafruit 16x2 lcd plate with a Raspberry Pi

# imports
import vlc
import time
import os
import Adafruit_CharLCD as LCD

# variables
run = True
repeat = True
state = 0
# states:
# 0 - File Explorer
# 1 - Player Info
# 2 - Settings
player = vlc.MediaPlayer()
path = "/mnt/usb"
dirlist = []
filename = ""
selected = 0
lcd = LCD.Adafruit_CharLCDPlate()

# custom charactrs
# music note icon
lcd.create_char(1, [2,3,3,2,14,30,12,0])
# pause icon
lcd.create_char(2, [0,27,27,27,27,27,27,0])
# repeat icon (2 characters)
lcd.create_char(3, [3,4,0,4,14,31,4,3])
lcd.create_char(4, [24,4,31,14,4,0,4,24])

# STARTUP SEQUENCE

lcd.set_color(1, 1, 1)

lcd.clear()

lcd.message("RPiStereo by\nJoyesh")
time.sleep(3)
lcd.clear()
lcd.message("Version 1.0")
time.sleep(3)
lcd.clear()

# scrolling text for long filenames
def renderscrolltext(text, cx, cy):
    if len(text) < 32:
        lcd.set_cursor(cx, cy)
        lcd.message(text[0:15])

# LCD UPDATE
def lcd_update():
    if state == 0:
        rnge = []
        # prevent index out of range errors
        if selected + 2 <= len(dirlist):
            rnge = range(selected, selected + 2)
        elif selected <= len(dirlist):
            rnge = range(selected, selected+1)
        
        # render
        for x in rnge:
            if len(dirlist[x]) > 16:
                renderscrolltext(dirlist[x] + '\n', 0, 1)
            else:
                lcd.message(dirlist[x] + '\n')

    if state == 1:
        lcd.clear()
        if player.is_playing():
            lcd.message("\x01 Now Playing\n" + filename)
        else:
            lcd.message("\x02 Paused\n" + filename)
        if repeat:
            lcd.set_cursor(14,0)
            lcd.message("\x03\x04")


dirlist = os.listdir(path)
dirlist.insert(0, "..")
lcd_update()

# MAIN UPDATE
while run:
    if lcd.is_pressed(LCD.SELECT):
        lcd.clear()
        # SELECT/PLAY/PAUSE
        if state == 0:
            # if path is directory
            if os.path.isdir(path + "/" + dirlist[selected]):
                # append selected folder to path
                path = path + "/" + dirlist[selected]
                # normalize path (if user has selected .., this prevents path from getting too long)
                path = os.path.abspath(path)
                # set directory list
                dirlist = os.listdir(path)
                # add .. to beginning of list
                dirlist.insert(0, "..")
                # set selected item to 0
                selected = 0
            # if path is file
            else:
                # add slash to end of path
                path = path + "/"
                # set filename to selected file
                filename = dirlist[selected]
                # initalize VLC media player
                player = vlc.MediaPlayer(path + filename)
                player.play()
                # set state to player info
                state = 1
            
            # update lcd
            lcd_update()
        
        elif state == 1:
            if player.is_playing():
                player.pause()
            else:
                player.play()

            lcd_update()
    
    elif lcd.is_pressed(LCD.LEFT):
        # STOP
        if state == 1:
            # stop player, reset selected index and state.
            player.stop()
            selected = 0
            state = 0
        
        # update lcd
        lcd_update()

    elif lcd.is_pressed(LCD.UP):
        # UP IN MENU
        # if selected - 1 is not negative (prevent out of range errors)
        if selected - 1 >= 0:
            selected = selected - 1
            lcd.clear()
            lcd_update()

    elif lcd.is_pressed(LCD.DOWN):
        # DOWN IN MENU
        # if selected + 1 is not out of list range
        if selected + 1 <= len(os.listdir(path)):
            selected = selected + 1
            lcd.clear()
            lcd_update()

    elif lcd.is_pressed(LCD.RIGHT):
        # SETTINGS MENU
        state = 2
        lcd_update()

    time.sleep(0.1)

