# TidbytAssistant
Display notifications from HomeAssistant to Tidbyt using this integration. You must also install the TidbytAssistant add-on which can be found here:

```txt
https://github.com/savdagod/ha-addons
```

### Configuration
1. Copy the tidbytassistant folder to your custom_components folder and restart HomeAssistant
2. To add your Tidbyt device, open the Tidbyt app. Navigate to the device you want to add, click the settings icon at the top right then navigate to the Developer tab.
3. Tap on Get API key. Here you will see a Device ID and Key. This is what you will use to set up the integration.
4. In HomeAssistant, navigate to your configuration.yaml and add the following to the bottom:
```txt
tidbytassistant:
  devices:
    - name: your device name
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - name: another device name
      ...
```
5. You can add as many devices as you want. Be sure to give each a unique name, you will be using this name when calling the action.
6. Restart HomeAssistant.
7. Once HomeAssistant restarts, you should now have a action called TidbytAssistant: Push. Use this in your automations to send notifiations.

## Pushing your own files
Coming soon...


## Things to note
### Changing Ports
By default, this integration sends the request on port 9000. If for some reason that port is in use, you can change it in the add-on configuration. Be sure to also change it in your configuration.yaml like so:
```txt
tidbytassistant:
  port: 5000
  devices:
    - name: your device name
      deviceid: device_id_from_previous_step
      token: key_from_previous_step
    - name: another device name
      ...
```

### Using secrets file
I also recommend that you use the secrets.yaml file to store your ID and Key. Add these to secrets.yaml"
```txt
tidbyt_id: device_id_from_previous_step
tidbyt_key: key_from_previous_step
```
Then your configuration will look like this:
```txt
tidbytassistant:
  devices:
    - name: your device name
      deviceid: !secret tidbyt_id
      token: !secret tidbyt_key
    - name: another device name
      ...
```
