# Motorchik
Motorchik, discord bot written in python.

## Longer about
Motorchik is a discord bot, written in python using [discord.py](https://github.com/Rapptz/discord.py).
At current state Motorchik provides simple tools for discord servers, such as delete a number of messages, ban or kick someone, give default roles to new members (without breaking Verification Level), etc.
Per-server configuration system is still in development, but working (not working: command black-/whitelisting).
If you want to add this bot on your server, hosted nearly 24/7 on my OrangePi PC, message me at discord John The Cooling Fan#6411 for a bot invitation link.

## Features
* Misc
  - Greeting message on member join.
  - Default roles given when member joins.
  - Message when member leaves.
  - Log bans and unbans.
* Factorio stuff
  - Get a mod (or mods) statistics and display as embed.
  - Send a list of mod statistics info.
* Configuration
  - Motorchik is highly configurable for servers (guilds).
 
## How to use / Installation
### 1. Clone this repo to your local machine
### 2. Make sure you have `discord.py`, `python-dateutil`, `bs4` and `natsort`:
  ```
  # python3 -m pip install discord.py python-dateutil bs4 natsort
  ```
  or
  ```
  $ python3 -m pip install --user discord.py python-dateutil bs4 natsort
  ```
### 3. Run `main.py`
  ```sh
  python3 main.py
  ```
  or
  ```sh
  ./main.py
  ```
### 4. Autostart
  You can use any type of auto-starting. My host runs linux and I use systemd unit to run it automatically
  `~/.config/systemd/user/Motorchik.service`
  ```ini
  [Unit]
  Description=Motorchik, discord bot written in python
  After=network-online.target
  
  [Service]
  ExecStart=/path/to/Motorchik/main.py
  WorkingDirectory=/path/to/Motorchik
  
  [Install]
  WantedBy=default.target
  ```
  And then
  ```
  $ systemctl --user enable Motorchik.service
  $ systemctl --user start Motorchik.service
  ```
  Everything will be logged to STDOUT, so you can view entire bot's log with:
  ```
  $ journalctl --user -u Motorchik.service
  ```
  (Requires restarting the unit for entire log to show up)
