# TidbytAssistant
Display notifications from HomeAssistant to Tidbyt using a custom script and HomeAssistant's shell_command integration.

Create a packages folder in your HA root. Copy the tidbyt.yaml file to your packages folder. Add this line to your HA config:
  '''homeassistant:
       packages: !include_dir_named packages/ 
  '''
Also be sure to add your Tidbyt device_id and tokens to your secrets.yaml

In tidbyt.yaml, you will have to edit <user> which is the user that will log into your Pixlet server (aka wherever you install the Pixlet app) and the <ip> of said server. Also edit the path where you put the contents of TidbytAssistant. Basically the shell command is logging in as a user, and running the TidbytDisplay.sh script with the required arguments. 

Create a .ssh folder in your HA root. You will need to ssh generate keys if you don't already have them: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Also make sure to chmod +x TidbytDisplau.sh on your Pixlet server.

Tidbyt.yaml automatically creates the script for you, so you can call it in your automations and user the dropdown to select what you want to notify and select teh devices. You might have to remove some of the conditions if you have less Tidbyts (I have 3, so three conditions, one for each device). Add more if you have more. Just be sure to reference the correct device_id and token for each condition.

Hopefully I can flesh this out to be more clear but at least there's some sort of documentation to get you started.
