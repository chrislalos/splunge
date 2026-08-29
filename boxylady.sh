#!/usr/bin/bash

workhorse()
{
    local venvPath=$1 wwwPath=$2 testPath=$3 command=$4
    shift 4

    d=$(mktemp -d) || return

    # system mounts
    mkdir -p "$d/bin" "$d/lib" "$d/usr/bin" "$d/usr/lib" "$d/dev"
    mount --rbind /dev "$d/dev"
    mount --bind /bin "$d/bin" || return
    mount --bind /lib "$d/lib" || return
    mount --bind /usr/bin/ "$d/usr/bin/" || return
    mount --bind /usr/lib/ "$d/usr/lib/" || return

    # user mounts
    mkdir -p "$d/www" "$d/venv" "$d/test"
    mount --bind "$wwwPath"  "$d/www"  || return
    mount --bind "$venvPath" "$d/venv" || return
    mount --bind "$testPath" "$d/test" || return

    # editable packages from the given venv
    for pth in "$venvPath"/lib/python*/site-packages/__editable__.*.pth; do
        [[ -f "$pth" ]] || continue
        while read -r src; do
            [[ -z "$src" ]] && continue
            mkdir -p "$d/$src"
            mount --bind "$src" "$d/$src"
        done < "$pth"
    done

    boxyPath=/bin:/usr/bin:/venv/bin
    PATH="$boxyPath" exec unshare -r -R "$d" "$command" "$@"
}

export -f workhorse

main()
{
    local venvPath="" wwwPath="" testPath=""
    while (( $# > 0 )); do
        case $1 in
            --venv) venvPath=$2; shift 2 ;;
            --www)  wwwPath=$2;  shift 2 ;;
            --test) testPath=$2; shift 2 ;;
            *)      break ;;
        esac
    done

    [[ -n "$venvPath" && -n "$wwwPath" && -n "$testPath" ]] || {
        printf 'Usage: boxylady.sh --venv <path> --www <path> --test <path> [command...]\n' >&2
        printf 'Example: ./boxylady.sh --venv ./venv --www ./www/site-01 --test ./test pytest test/test_hello.py -v\n' >&2
        return 1
    }
    command=${1:-pytest}
    shift || true

    unshare -U -r -m bash -c \
        'workhorse "$@"' boxyladyland \
        "$venvPath" "$wwwPath" "$testPath" "$command" "$@"
}

(return 0 2>/dev/null) || main "$@"
