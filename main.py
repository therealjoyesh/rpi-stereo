# RPi Stereo 1.2
# Programmed by Joyesh
# For use with a Adafruit 16x2 lcd plate with a Raspberry Pi

# imports
# audio related
import vlc
import alsaaudio
# some other related stuff
import time
import os
import threading
# screen
import Adafruit_CharLCD as LCD

# variables
settings=["Backlight", "Repeat", "Volume", "Exit"]
run = True
PreviousPlayingState = False
PreviousBacklightState = True
repeat = False
stopbyuser = False
backlight = True
state = 0
# states:
# 0 - File Explorer
# 1 - Player Info
# 2 - Settings

# audio stuff
player = vlc.MediaPlayer()
mixer = alsaaudio.Mixer()
vol = int(mixer.getvolume()[0])
# file explorer variables
path = "/mnt/usb"
dirlist = []
filename = ""
# menu variables
selected = 0
# lcd
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

lcd.message("RPiStereo by\nJ0SH")
time.sleep(3)
lcd.clear()
lcd.message("Version 1.2")
time.sleep(3)
lcd.clear()

def repeatcheck():
    while run:
        # cannot check to 1.0 because some songs end before it registers as 100%
        if repeat and player.get_position() > 0.995:
            player.stop()
            player.play()
        # prevent lcd lag (running a while loop with no sleep causes a lot of stress on the CPU)
        time.sleep(0.01)

# spawn repeat thread (this is to allow for more fine-grained checking of repeat)
repthread = threading.Thread(target=repeatcheck)
repthread.start()

# LCD UPDATE
def lcd_update():
    lcd.clear()
    if state == 0:
        rnge = []
        # prevent index out of range errors
        if selected + 2 <= len(dirlist):
            rnge = range(selected, selected + 2)
        elif selected <= len(dirlist):
            rnge = range(selected, selected + 1)
        
        # render
        index = 0
        for x in rnge:
            print(index)
            if len(dirlist[x]) > 16:
                lcd.message(dirlist[x][:16])
            else:
                lcd.message(dirlist[x] + '\n')
            index + 1

    if state == 1:
        if player.is_playing():
            lcd.message("\x01 Now Playing\n" + filename)
        else:
            lcd.message("\x02 Paused\n" + filename)
        if repeat:
            lcd.set_cursor(14,0)
            lcd.message("\x03\x04")

    if state == 2:
        rnge = []
        # prevent index out of range errors
        if selected + 2 <= len(settings):
            rnge = range(selected, selected + 2)
        elif selected <= len(settings):
            rnge = range(selected, selected + 1)
        # render
        for x in rnge:
            lcd.message(settings[x])
            if settings[x] == "Backlight":
                if backlight:
                    lcd.message(" on\n")
                else:
                    lcd.message(" off\n")
            
            elif settings[x] == "Repeat":
                if repeat:
                    lcd.message(" on\n")
                else:
                    lcd.message(" off\n")

            elif settings[x] == "Volume":
                lcd.message(" " + str(vol) + "\n")

dirlist = os.listdir(path)
dirlist.insert(0, "..")
lcd_update()

# MAIN UPDATE
while run:
    # check if playing state has changed, if it has, update lcd
    if not PreviousPlayingState == player.is_playing():
        lcd_update()
    # if backlight state has changed, update backlight
    if not PreviousBacklightState == backlight:
        if backlight:
            lcd.set_color(1,1,1)
        else:
            lcd.set_color(0,0,0)
    
    PreviousBacklightState = backlight
    PreviousPlayingState = player.is_playing()
    if lcd.is_pressed(LCD.SELECT):
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
                #set stop by user to false just incase was stopped by user before
                stopbyuser = False
                # set state to player info
                state = 1
        
        elif state == 1:
            if player.is_playing():
                stopbyuser = True
                player.pause()
            else:
                player.play()
                stopbyuser = False

        elif state == 2:
            if settings[selected] == "Backlight":
                backlight = not backlight
            if settings[selected] == "Repeat":
                repeat = not repeat
            if settings[selected] == "Volume":
                if vol == 0:
                    vol = 25
                    mixer.setvolume(25)
                elif vol == 25:
                    vol = 50
                    mixer.setvolume(50)
                elif vol == 50:
                    vol = 75
                    mixer.setvolume(75)
                elif vol == 75:
                    vol = 100
                    mixer.setvolume(100)
                elif vol == 100:
                    vol = 0
                    mixer.setvolume(0)

            if settings[selected] == "Exit":
                run = not run

        lcd_update()
    
    elif lcd.is_pressed(LCD.LEFT):
        # STOP
        if state == 1:
            # stop player, reset selected index and state.
            stopbyuser = True
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
            lcd_update()

    elif lcd.is_pressed(LCD.DOWN):
        # DOWN IN MENU
        # if selected + 1 is not out of list range
        #if not t1._stopevent.isSet():
            #t1.join()
        #if not t2._stopevent.isSet():
            #t2.join()
        if state == 0:
            if selected + 1 <= len(os.listdir(path)):
                selected = selected + 1

        elif state == 2:
            if selected + 2 <= len(settings):
                selected = selected + 1

        lcd_update()

    elif lcd.is_pressed(LCD.RIGHT):
        # SETTINGS MENU
        if state == 2:
            selected = 0
            state = 0
        else:
            selected = 0
            state = 2
        lcd_update()

    time.sleep(0.1)

lcd.clear()
lcd.message("Exiting")
time.sleep(3)
lcd.clear()
lcd.message("To turn back on,\n you must reboot")
