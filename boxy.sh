#!/usr/bin/bash

main ()
{
	d=$(mktemp -d) || return
	mkdir -p boxymusic || return

	mkdir -p "$d/bin" "$d/lib" "$d/usr/bin" "$d/usr/lib" "$d/test" "$d/venv" "$d/www" "$d/dev"
	mount --rbind /bin "$d/bin" || return
	mount --rbind /lib "$d/lib" || return
	mount --rbind /dev "$d/dev"
	mount --rbind /usr/bin/ "$d/usr/bin/" || return
	mount --rbind /usr/lib/ "$d/usr/lib/" || return
	mount --rbind ./test "$d/test/" || return
	mount --rbind ./venv/ "$d/venv/" || return
	mount --rbind ./www/ "$d/www" || return

	# mount staging folder at ./boxymusic
	mount --rbind "$d" ./boxymusic || return

	# loop over all editable packages in venv and bind them
	venvPath=./venv
	for pth in "$venvPath"/lib/python*/site-packages/__editable__.*.pth; do
		[[ -f "$pth" ]] || continue
		while read -r src; do
			[[ -z "$src" ]] && continue
			mkdir -p "$d/$src"
			mount --rbind "$src" "$d/$src"
		done < "$pth"
	done

	boxyPath=/bin:/usr/bin:/venv/bin
	# boxyPrompt='PS1="[boxy] \w\n$ "'
	boxyPrompt="[boxy] \w\n$ "
	# PATH=$boxyPath unshare -U -r -R "$d" bash --rcfile <(echo "$prompt") || return
	PATH=$boxyPath PS1="$boxyPrompt" unshare -U -r -R "$d" bash --norc || return
}

(return 0 2>/dev/null) || main "$@"

