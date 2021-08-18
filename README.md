# MagTag-MLB

MLB Baseball Schedule and Scoreboard for the Adafruit MagTag

This is a hobby project I started during my vacation in August 2021. My kids always want to know the recent scores, upcoming games, and current game stats for the Minnesota Twins. The [Adafruit MagTag](https://www.adafruit.com/product/4800) gave me an opportunity to build something fun and useful that could serve this purpose.

The e-ink display can show a baseball schedule or scoreboard, then continue to display while it goes into a low-power mode. Then anyone can check the schedule throughout the day without much drain on the battery. Thanks to [CircuitPython](https://circuitpython.org/), the code files can just be copied to the device (or edited in-place), which makes the development & deployment process easy.

## How it works

Major League Baseball provides a publicly accessible "Stats API" which provides easy access to lots of information about players, games, schedules, and more. I found the best way to discover what's available in the API is to look at the source code of the [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) project. This python project is a more full-featured wrapper for the API, but it's not used in this project. For this project we only really use the schedule data and some of the live game data, so it's been programmed to call those endpoints directly.

The program will show the schedule and a live game scoreboard for one specific team. When the program starts, it checks to see if there's a live game. If so, the scoreboard is shown, otherwise the schedule is displayed. During live games the system updates once per minute, otherwise once per hour.

## Choose your Team

The program requires a "Team ID" to define which team to follow. This is defined as the `team_id` value in the `secrets.py` file (more info below). The Team ID is the ID number used within the MLB Stats API. To find your team of choice, refer to the [full team list via the API](https://statsapi.mlb.com/api/v1/teams?sportIds=1&fields=teams,id,name).

## Secrets file

The programs requires a `secrets.py` file in the same (root level) folder as `code.py`. It basically acts as your config file for the app. This file should contain your wifi SSID and password, as well as your time zone, and your preferred team ID. This has been excluded from the git repository, so you'll need to create your own, here's an example:

```python
secrets = {
    'ssid' : 'MyNetworkName',
    'password' : 'MyNetworkPassword',
    'timezone' : 'America/Chicago', # http://worldtimeapi.org/timezones
    # Team IDs: https://statsapi.mlb.com/api/v1/teams?sportIds=1&fields=teams,id,name
    'team_id' : 142
}
```

## Deploying to the MagTag

The MagTag allows you to just copy the code files to the device when connected via USB, and any changes made on the device will restart the program. So the simplest way to get started is to just copy the contents of the `src` folder directly to the MagTag.

Personally, I like to edit multiple files at a time in VS Code, and only push to the device when I'm ready. So I wrote the `deploy.ps1` powershell script. When ready to deploy some changes, run this script to copy the updated files to the MagTag.

## Attribution/Credits/Etc

Data provided by the MLB Stats API is copyright MLB Advanced Media, L.P.

On-screen fonts were generated from the [Open Sans font on Google Fonts](https://fonts.google.com/specimen/Open+Sans), and converted to BDF format using [FontForge](https://fontforge.org/). Individual letters were edited to look better on the e-ink display.
