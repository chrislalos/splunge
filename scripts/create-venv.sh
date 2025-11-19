#! /usr/bin/env bash


main ()
{
    local venvPath="$PWD/venv"
    [[ ! -d "$venvPath" ]] || { printf 'Folder already exists: %s\n' "$venvPath" >&2; return 1; }
    printf '$venvPath=%s\n' "$venvPath"
    python3 -m venv --upgrade-deps "$venvPath" --prompt 'splunge'

    reqsPath="$PWD/venv-reqs.txt"
    # shellcheck disable=SC2016
    [[ -f "$reqsPath" ]] || { printf 'Non-existent path: $reqsPath\n' >&2; return 1; }
    "$venvPath/bin/pip" install --requirement "$reqsPath"
}


if main "$@" && (return 0 2>/dev/null); then
    source "$PWD/venv/bin/activate"
fi    
