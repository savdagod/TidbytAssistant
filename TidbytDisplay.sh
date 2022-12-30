#!/bin/bash

CONTENT=${1:?"missing arg 1 for CONTENT"}
DEVICE=${2:?"missing arg 2 for DEVICE"}

case $DEVICE in
	livingroom)
		TB_DEVICEID=""
		TB_TOKEN=""
	;;

	loft)
		TB_DEVICE=""
		TB_TOKEN=""
	;;
esac

ROOT_DIR=~/pixlet_apps/TidbytDisplay
RENDER_PATH=$ROOT_DIR/render.webp

pixlet render $ROOT_DIR/display/$CONTENT.star -o $RENDER_PATH
		
pixlet push --api-token $TB_TOKEN $TB_DEVICEID $RENDER_PATH
exit 0
