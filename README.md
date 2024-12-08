<p align="center">
  <img src="https://raw.githubusercontent.com/savdagod/TidbytAssistant/main/logo.png">
</p>
</br>

Display notifications from HomeAssistant to Tidbyt using this integration. Installation of the add-on is required.

## Installation
First, install the TidbytAssistant add-on which can be found here (You **MUST** install this add-on whether it's through the add-on store or as a regular Docker container for Push, Publish and Text services to work. If the add-on is not installed, the integration will not load.):

```txt
https://github.com/savdagod/ha-addons
```

I also highly recommend installing the ***Studio Code Server*** and ***Samba*** add-ons if you dont have them already. These will make copying files and editing your **configuration.yaml** much easier. ***Samba*** is part of the official addons and ***Studio Code Server*** is part of the HomeAssistant community add-ons.

### HACS
You can add this repository to HACS if you have it installed by adding this link to your custom repository (click the 3 dots at the top right):
```txt
https://github.com/savdagod/TidbytAssistant
```
Then just search for TidbytAssistant and install the integration. You will have to restart HomeAssistant.

This is the way i recommend you install this integration so that you can stay up-to-date on releases.

### Manual
Copy the entirety of custom_components/tidbytassistant to your /config/custom_components folder. You can do this using ***Samba***.


## Configuration
1. To add your Tidbyt device, open the Tidbyt app. Navigate to the device you want to add, click the settings icon at the top right then navigate to the Developer tab.
2. Tap on Get API key. Here you will see a Device ID and Key. This is what you will use to set up the integration.
3. In HomeAssistant, navigate to your **configuration.yaml** and add the following to the bottom:
```txt
tidbytassistant:
  device:
    - name: your device name #this is optional now, as the integration will get the device name using the Tidbyt API
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - deviceid: device_id_from_previous_step
      token: key_from_previous_step
      ...
```
4. You can add as many devices as you want.
5. Restart HomeAssistant.
6. Once HomeAssistant restarts, you should now have multiple actions as well as light and switch entities for each Tidbyt you've added. Use these in your automations to send notifiations, text, your own .star files or adjust the brightness of your display.

## Features

### Light and switch entities
The integration will expose each devices' sceen as a light entity. The autodim feature is exposed as a switch entity. The states are fetched every 30s.

### Services
#### TidbytAssistant: Push
1. Select the radio button for *Built-in*.
2. Use the *Content* dropdown to select from the built in notifications. These are apps that I have built that have little animations for notifications.
3. Select you device(s) and run the action.

##### Pushing your own files
1. Create a folder in your **/config** directory called **tidbyt**.
2. Place your .star file(s) in this folder.
3. Select the radio button for *Custom*. In the *Custom Content* text box, enter the file name minus the '.star'. Example: If your file is named *custom.star*, you will enter *custom* in the field.
4. You can also pass in arguments as key=value pairs. in the *Arguments* box you can enter these pairs like this, separated with a semi-colon (;): ***key=value;key2=value 2***. (Scroll down to **Passing arguments** to see an example of how this works)
5. Select your device(s) and run the action to see it displayed on your Tidbyt.
   
### Pushing text
#### Use the action TidbytAssistant: Text
1. Select the radio buttom for *Text*
2. In the *Content* box, enter the text you want displayed. You can also select from the avaialble fonts and colors as well as static text or scrolling.
4. Select your device(s) and run the action. You should see your text on the screen.

### Publish app to your Tidbyt
#### Use the action TidbytAssistant: Push (previously Publish)
1. Create a folder in your **/config** directory called **tidbyt**.
2. Create a folder for your app with your app name (myapp.star should be placed inside a folder called myapp) and your .star file(s) in this folder. Pixlet also supports apps with mutiple .star files, so all associated files should be in the same folder. It is best practice to have 1 folder per app regardless of how many .star files your app needs.
3. In the *Custom Content* text box, enter the file name minus the '.star'. Example: If your file is named *custom.star*, you will enter *custom* in the field.
4. Enter a unique name in the *Content ID* field. (specifying this is what adds the app to the rotation)
5. You can also pass in arguments as key=value pairs. in the *Arguments* box you can enter these pairs like this, separated with a semi-colon (;): ***key=value;key2=value 2***. (Scroll down to **Passing arguments** to see an example of how this works)
6. Select you device(s) and run the action to add your app to your app rotation.

### Deleting app from rotation
#### Use the action TidbytAssistant: Delete
1. Enter the content ID of the app you published and device name.
2. Select you device(s) and run the action. The app should now be removed from your rotation.
3. If the app you tried to delete is not installed on the Tidbyt, you will see a list of apps that are available for deletion. Only apps that you have sent through HomeAssistant will show up for deletion.
   
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

### Changing Hosts
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

### External container
If you run the addon as a separate container (ie not part of HomeAssistant), you can set *external_addon* to true like so:
```txt
tidbytassistant:
  host: 192.168.1.200
  port: 1234
  external_addon: true
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

### Passing arguments
Passing arguments to your app can be helpful because it removes the need to hard code values. It also allows you to pass in templated values directly to your apps. The following example is taken from the Pixlet docs and is how you would use these varibles inside your app:
```
def main(config):
    who = config.get("who")
    print("Hello, %s" % who)
```
This example has a varible "who", which can be used as the **key=value** pair **who=me** which will pass the value **me** into your star app. Here is an example I use for the Movie Night app, which has two varibles **time** and **title** and uses HomeAssistant's template values:
```
  ... other service data here
  arguments: >-
    time={{ (now().strftime('%Y-%m-%d') + 'T' +
    states('input_datetime.movie_night_time') + now().isoformat()[-6:]) 
    }};title={{ states('input_text.movie_night_movie') }}
```

### Troubleshooting
The action should do a few checks when you run it and give feedback on what went wrong. However, sometimes everything checks out on the HA side but won't on the add-on side. If you navigate to the add-on page and click 'Logs' you can see what went wrong if the action you ran is not giving you the desired results.
