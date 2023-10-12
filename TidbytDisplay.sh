#!/usr/bin/env sh

# These will be sent directly from HomeAssistant
CONTENT=${1:?"missing arg 1 for CONTENT"} 
TB_DEVICEID=${2:?"missing arg 2 for DEVICE ID"}
TB_TOKEN=${3:?"missing arg 3 for TOKEN"}

ROOT_DIR=/usr/share/hassio/homeassistant/TidbytDisplay #this is wherever you put the folder
RENDER_PATH=$ROOT_DIR/render.webp

pixlet render $ROOT_DIR/display/$CONTENT.star -o $RENDER_PATH

pixlet push --api-token $TB_TOKEN $TB_DEVICEID $RENDER_PATH

exit 0
