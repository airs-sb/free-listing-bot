# Hypixel Skyblock Listing Bot
This is a hypixel listing bot that uses the [Hypixel API](https://developer.hypixel.net/) to fetch bedwars and skyblock stats.
- The parser I am using is [skyblockparser](https://github.com/noemt-studios/skyblockparser).
- Credits: https://github.com/noemtdotdev
- This requires an [Hypixel API Key](https://developer.hypixel.net/)
## How To Run
- Clone the repository
- Make a virtual environment using `python -m venv listing` (**THIS IS IMPORTANT**)
- Install packages using `pip install -r reqs.txt`
- Enter your discord bot token and owner ID in `config.json`
- Run the main bot using `python bot.py`
- To setup the listing bot, add the manager bot to your guild & use /create
- To update your bot, put your update files in /files folder and run /restart in the bot.
## Contribution
- To customise the listing embeds, go /utils and choose the embed you wish to edit.
- To customise the panel embeds click on the cogs, and directly edit them.
- To add any new commands/features insert your cog in /cogs folder to automatically load it.
- Feel free to revamp the cogs system and it does not have seperate embed files.
## Features
### Listing
- `/list-skyblock` | List a skyblock account.
- `/list-bedwars` | List a bedwars account.
### Addresses
- `/addresses get` | Gets all your addreses
- `/addresses add` | Add an address
- `/addreses remove` | Remove an address
### Configuration
- `/config update-category` | Update a category in the config.
- `/config update-role` | Update a role in the config.
- `/config update-channel` | Update a channel in the config.
- `/config update-value` | Update a value in the config.
### Ticket Panels
- `/ticket-panel coins` | Sends the coin panel.
- `/dnc add-buy` | Add dynamic coin pricing for "Buy"
- `/dnc remove-buy` | Remove dynamic coin pricing for "Buy"
- `/dnc add-sell` | Add dynamic coin pricing for "Sell"
- `/dnc remove-sell` | Remove dynamic coin pricing for "Sell"
- `/mfa-panel` | Sends the MFA panel.
- `/middleman-panel` | Sends the middleman panel.
- `/sellaccount-panel` | Sends the sell account panel.
### Shares
- `/share clear-all` | Clear all seller shares
- `/share clear-seller` | Clear a sellers share
- `/share get` | Get a sellers share
- `/share get-all` | Get all seller shares
- `/share get-own` | Get your own share.
- `/share manual-add` | Add a share to a seller
- `/share setup` | Setup share tax.
- `/log` | Log a sale for yourself.
### Backups
- `/restore-skyblock` | Restore all skyblock accounts
- `/restore-bedwars` | Restore all bedwars accounts
- `/restore-vouches` | Restore all vouches.
### Utils
- `/tag-add` | Add a tag.
- `/tag-remove` | Remove a tag.
- `/restart` | Restart the bot and pull update files.
## Unhappy With The Bot?
> Message [@airterm](https://discord.com/users/1292032485601050667) to purchase a premium version of the bot.
