#!/usr/bin/env bash

function outputVideo() {
	local port="${1:-HDMI-1-1}";
	local resolution="${2:-1920x1080}";

	echo "Port       : ${port}";
	echo "Resolution : ${resolution}";

	xrandr --addmode "${port}" "${resolution}";
	xrandr --output "${port}" --mode "${resolution}";
}

outputVideo "${port}" "${resolution}";
