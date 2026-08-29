#!/usr/bin/env bash

main ()
{
	prompt='PS1="[brap] \w\n$ "'
	unshare -U -r -m bash --rcfile <(cat ~/.bashrc; echo "$prompt") || return
}

(return 0 2>/dev/null) || main "$@"

