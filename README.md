<p align="center">
  <img src="https://raw.githubusercontent.com/savdagod/TidbytAssistant/main/logo.png">
</p>
</br>

Display notifications from HomeAssistant to Tidbyt using this integration. You must also install the TidbytAssistant add-on which can be found here:

```txt
https://github.com/savdagod/ha-addons
```

I also highly recommend installing the ***Studio Code Server*** and ***Samba*** add-ons if you dont have them already. These will make copying files and editing your **configuration.yaml** much easier. ***Samba*** is part of the official addons and ***Studio Code Server*** is part of the HomeAssistant community add-ons.

You can also add this repository to HACS if you have it installed by adding this link to your custom repository:
```txt
https://github.com/savdagod/TidbytAssistant
```



### Configuration
1. Copy the **tidbytassistant** folder to your **custom_components** folder and restart HomeAssistant.
2. To add your Tidbyt device, open the Tidbyt app. Navigate to the device you want to add, click the settings icon at the top right then navigate to the Developer tab.
3. Tap on Get API key. Here you will see a Device ID and Key. This is what you will use to set up the integration.
4. In HomeAssistant, navigate to your **configuration.yaml** and add the following to the bottom:
```txt
tidbytassistant:
  device:
    - name: your device name
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - name: another device name
      ...
```
5. You can add as many devices as you want. Be sure to give each a unique name, you will be using this name when calling the action.
6. Restart HomeAssistant.
7. Once HomeAssistant restarts, you should now have an action called TidbytAssistant: Push. Use this in your automations to send notifiations.

## Features
### Pushing built-in notifications
#### Use the action TidbytAssistant: Push
1. Select the radio button for *Built-in*.
2. Use the *Content* dropdown to select from the built in notifications. These are apps that I have built that have little animations for notifications.
3. Type out your device name and run the action.

### Pushing your own files
#### Use the action TidbytAssistant: Push
1. Create a folder in your **/config** directory called **tidbyt**.
2. Place your .star file(s) in this folder.
3. Select the radio button for *Custom*. In the *Custom Content* text box, enter the file name minus the '.star'. Example: If your file is named *custom.star*, you will enter *custom* in the field.
   
### Pushing text
#### Use the action TidbytAssistant: Text
1. Select the radio buttom for *Text*
2. In the *Custom Content* box, enter the text you want displayed. You can also select from the avaialble fonts and colors as well as static text or scrolling.
4. Enter your device name and run the action. You should see your text on the screen.

### Adding app to your regular app rotation
#### Use the action TidbytAssistant: Publish
1. Create a folder in your **/config** directory called **tidbyt**.
2. Place your .star file(s) in this folder.
3. In the *Content* text box, enter the file name minus the '.star'. Example: If your file is named *custom.star*, you will enter *custom* in the field.
4. Enter a unique name in the *Content ID* field.
5. Enter your device name. Run the action to add your app to your app rotation.

### Deleting app from roation
#### Use the action TidbytAssistant: Delete
1. Enter the contend ID of the app you published and device name.
2. Run the action. The app should now be removed from your rotation.
   
## Things to note
### Changing Ports
By default, this integration sends the request on port 9000. If for some reason that port is in use, you can change it in the add-on configuration. Be sure to also change it in your configuration.yaml like so:
```txt
tidbytassistant:
  port: 5000
  device:
    - name: your device name
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - name: another device name
      ...
```

### Changing Ports
By default, this integration sends the request to locahost. If you want to host the add-on separately or using HA Core then you can change the host in the configuration:
```txt
tidbytassistant:
  host: 192.168.1.200
  device:
    - name: your device name
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - name: another device name
      ...
```

### Using secrets file
I also recommend that you use the secrets.yaml file to store your ID and Key. Add these to secrets.yaml:
```txt
tidbyt_id: device_id_from_previous_step
tidbyt_key: key_from_previous_step
```
Then your configuration will look like this:
```txt
tidbytassistant:
  device:
    - name: your device name
      deviceid: !secret tidbyt_id
      token: !secret tidbyt_key
    - name: another device name
      ...
```

### Troubleshooting
The action should do a few checks when you run it and give feedback on what went wrong (ie if you enter an incorrect device name, it will give you a list of valid names). However, sometimes everything checks out on the HA side but won't on the add-on side. If you navigate to the add-on page and click 'Logs' you can see what went wrong if the action you ran is not giving you the desired results.
