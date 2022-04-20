#!/usr/bin/env bash

set -e;

DOTFILES="$(readlink -f $(dirname "$0"))";

function echo_to_stderr() {
	echo "$*" 1>&2;
}

function die() {
	echo_to_stderr "$*";
	exit 1;
}

function failure() {
	local lineNo=$1;
	echo_to_stderr "Failed at $lineNo line";
}

trap 'failure ${LINENO}' ERR

function symlinkHasPresent() {
	# todo check args
	local what="${1}";

	local source="${DOTFILES}/home/${what}";
	local symlink="${HOME}/${what}";

	if [ ! -f "${source}" ]; then
		die "Error while creating a symlink: \"${source}\" not found!";
	fi

	if [ -L "${symlink}" ]; then
		echo "Skipping creation of a symlink for \"${what}\": already exists.";
		return 0;
	fi
	
	if [ -f "${symlink}" ]; then
		echo "Backuping existed file: \"${what}\"";
		mv "${symlink}" "${symlink}.backup"
	fi

	echo "Creation a symlink for \"${what}\"";
	ln -s "${source}" "${symlink}";
}

function installGitCredentials() {
	# todo check the previous credentials
	local gitUserName="s373r";
	local gitUserEmail="s373r@users.noreply.github.com";

	echo "Setting global git name: ${gitUserName}";
	git config --global user.name "${gitUserName}";

	echo "Setting global git email: ${gitUserEmail}";
	git config --global user.email "${gitUserEmail}";
}

function createDirectoryStructure() {
	echo "Create ~/bin if not exists";
	mkdir -p ${HOME}/bin;
}

function doInstall() {
	createDirectoryStructure;

	symlinkHasPresent .zshrc;
	symlinkHasPresent bin/output-video-to-the-second-monitor.sh;

	installGitCredentials;
}

function main() {
	local mode="${1}";

	case "${mode}" in
		"install")
			doInstall;
			;;
		*)
			die "Mode \"${mode}\" isn't supported. Supported modes: install"
			;;
	esac
}


main "${1}";
