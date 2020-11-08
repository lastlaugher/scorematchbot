# Score! Match bot
This is an automated bot for `Score! Match` mobile game.
- You don't need to play the app every 4 hours to open free package or unlock/open boxes.
- You don't need to watch the boring video to get the reward.

## Features
- [X] Open packages every 4 hours
- [X] Unlock available boxes
- [X] Open boxes whose waiting time is over
- [X] Open rewards given for every 10 goals
- [X] Open free collect package and watch the ad video
- [X] Run Memu and Score! Match app
- [X] Play game
- [ ] Enhance the game AI
- [ ] Show status (Bux, Gem, Star, and Arena)
- [ ] Chat

## Environment
- Windows
- Memu Android Emulator

## Installation
### Memu
- Download [Memu Android Emulator](https://www.memuplay.com/) and install it
- Set the display resolution: 1280x720 (It's the default resolution)
### Score! Match APK
- Currently, it can't be found in Google Play. From Googling, you can find the APK file.
- Install the downloaded APK in Memu
- Set language as English in the app
- (For only playing game) Set distinguishing one-colored uniform such as red, color, and yellow. Stripe or patterned uniform is not recommended.
### ScoreMatchBot
- Download this code repository and unzip
### (Optional) Facebook app
- If you need to share your account between Memu emulator and your phone, Facebook app is needed to install in Memu in order to keep your account logged in

## Usage
Run `smbot.exe` in the unzipped directory

## Advaned usage
### Help message
```
usage: smbot.exe [-h] [--log LOG] [--debug] [--play-duration PLAY_DURATION]
                 [--play-game]

optional arguments:
  -h, --help            show this help message and exit
  --log LOG             Log level (CRITICAL, ERROR, WARNING, INFO, and DEBUG)
  --debug
  --play-duration PLAY_DURATION
                        Time duration how often play the game (default: 60
                        miniutes)
  --play-game           If set, play the game every [play-duration] minutes
```

### Playing game (default duration: 1 hour)
*WARNING: Playing game AI is not good enough now. It's just working level. It'll descrease your star points. Just use this option for the purpose of getting free gems and bux. The game AI will be enhanced continuously.*
```
smbot.exe --play-game
```

### Playing game with custom duration
```
smbot.exe --play-game --play-duration [minutes]
```

If you want to play every 4 hours
```
smbot.exe --play-game --play-duration 240
```
