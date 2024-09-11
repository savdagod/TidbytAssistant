# TidbytAssistant
Display notifications from HomeAssistant to Tidbyt using this integration. You must also install the TidbytAssistsnt add-on which can be found here:

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
  - name: your device name
    deviceid: device_id_from_previous_step
    token: key_from_previous_step
  - name: another device name
    ...
```
5. You can add as many devices as you want. Be sure to give each a unique name, you will be using this name when calling the action.
6. Restart HomeAssistant.
7. Once HomeAssistant restarts, you should now have a action called TidbytAssistant: Push. Use this in your automations to send notifiations.

As of now, there are only a hadnful of animations available. I plan to update this integration/add-on so that users can also use their own .star files. 
