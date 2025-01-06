# VRChatHapticTail
basically sends the information about whether your avatar's tail is grabbed through wifi to a esp32 and this esp32 controls a vibrator for haptic feedback.

## If you are using CH582
Set your vrc osc port by adding --osc=9000:127.0.0.1:8888 to the game launch options.

Flash the firmware to your CH582

Decide wich avatar variable you wish to monitor. It should be a bool. Edit line 39 of OSC_BT.py accordingly.

Run OSC_BT.py, launch the game, turn on OSC in the game.

## If you are using ESP32
Check which avatar variable you wish to monitor, edit 
'haptic.ino' accordingly.

Connect ESP32 to your wifi, find the IP address of your ESP32, then add --osc=9000:[The ip address of your esp32]:8888 to the game launch options.

Launch the game, turn on OSC in the game.

