#! /usr/bin/env bash

SCRIPT_DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")
PROJECT_DIR="$SCRIPT_DIR/.."

# Find www — either on PATH or in scripts/
WWW=$(command -v www 2>/dev/null || printf '%s' "$PROJECT_DIR/scripts/www")
[[ -f "$WWW" ]] || { printf 'www not found\n' >&2; exit 1; }

www() { "$WWW" "$@"; }

command -v bwrap >/dev/null || { printf 'bwrap not installed\n' >&2; exit 1; }


ns()
{
    if ! $HAS_NET_NS; then
        return 0  # skip — no network namespace support
    fi
    bwrap --unshare-net --cap-add all --bind / / --proc /proc --dev /dev \
        --chdir "$PROJECT_DIR" \
        bash -e -o pipefail -c "$1"
}


# Filesystem-only isolation — no network namespace needed
ns_isolate()
{
    bwrap --bind / / --proc /proc --dev /dev \
        --chdir "$PROJECT_DIR" \
        bash -e -o pipefail -c "$1"
}


# Pre-flight: check if network namespace + loopback is supported
check_net_ns()
{
    bwrap --unshare-net --bind / / --proc /proc \
        bash -c 'ip link set lo up' 2>/dev/null
}


HAS_NET_NS=false
check_net_ns && HAS_NET_NS=true


test-serve-tcp()
{
    ns '
        trap "kill 0" EXIT
        www --port 80 --code-folder ./www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/hello.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-serve-uds()
{
    ns '
        trap "kill 0" EXIT
        www --socket /tmp/splunge-test.sock --code-folder ./sample-site &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" --unix-socket /tmp/splunge-test.sock http://localhost/index.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-host-port()
{
    ns '
        trap "kill 0" EXIT
        www --host 127.0.0.1 --port 8080 --code-folder ./www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/hello.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-python-page()
{
    ns '
        trap "kill 0" EXIT
        www --port 80 --code-folder ./www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/foo.py)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-markdown()
{
    ns '
        trap "kill 0" EXIT
        www --port 80 --code-folder ./www &
        sleep 2
        curl -s http://localhost/hello.md | grep -q "Hello"
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-404()
{
    ns '
        trap "kill 0" EXIT
        www --port 80 --code-folder ./www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/nonexistent)
        [[ "$code" == "404" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-init()
{
    local tmpDir; tmpDir=$(mktemp -d --tmpdir test-www-init.XXXXXX)
    pushd "$tmpDir" >/dev/null || return 1

    printf "80\nlocalhost\n./www\n./templates\n$HOME/tmp/splunge/log/splunge.log\n" | "$WWW" init 2>/dev/null
    local result=$?

    popd >/dev/null
    [[ "$result" -eq 0 && -f "$tmpDir/.splunge.env" ]] \
        && { printf '  PASS\n'; return 0; } \
        || { printf '  FAIL\n'; return 1; }
}


test-config-auto()
{
    ns '
        trap "kill 0" EXIT
        cat > .splunge.env <<EOF
SPLUNGE_PORT=80
SPLUNGE_CODEFOLDER=./sample-site
SPLUNGE_TEMPLATES_FOLDER=./www/templates
EOF
        www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/some-values.py)
        [[ "$code" == "200" ]]
        rm -f .splunge.env
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-config-explicit()
{
    ns '
        trap "kill 0" EXIT
        mkdir -p /tmp/splunge-cfg
        cat > /tmp/splunge-cfg/env <<EOF
SPLUNGE_PORT=80
SPLUNGE_CODEFOLDER=./www
EOF
        www --with-config /tmp/splunge-cfg/env &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/hello.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-flag-override()
{
    ns '
        trap "kill 0" EXIT
        cat > .splunge.env <<EOF
SPLUNGE_PORT=9090
SPLUNGE_CODEFOLDER=./www
EOF
        www --port 80 &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/hello.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-missing-content()
{
    "$WWW" --port 80 --code-folder /nonexistent 2>&1 | grep -qi 'not found' \
        && { printf '  PASS\n'; return 0; } \
        || { printf '  FAIL\n'; return 1; }
}


test-env-only()
{
    ns '
        trap "kill 0" EXIT
        export SPLUNGE_PORT=80 SPLUNGE_CODEFOLDER=./www
        www &
        sleep 2
        code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/hello.html)
        [[ "$code" == "200" ]]
    ' && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-port-socket-mutex()
{
    "$WWW" --port 80 --socket /tmp/s 2>&1 | grep -q "mutually exclusive" \
        && { printf '  PASS\n'; return 0; } \
        || { printf '  FAIL\n'; return 1; }
}


all()
{
    local tests=(
        test-serve-tcp
        test-serve-uds
        test-host-port
        test-python-page
        test-markdown
        test-404
        test-init
        test-config-auto
        test-config-explicit
        test-flag-override
        test-missing-content
        test-env-only
        test-port-socket-mutex
    )
    local total=${#tests[@]} passed=0 failed=0
    for t in "${tests[@]}"; do
        printf 'Test: %s\n' "$t"
        if "$t"; then (( passed++ )); else (( failed++ )); fi
    done
    printf '\n%d passed, %d failed, %d total\n' "$passed" "$failed" "$total"
    return "$failed"
}


main()
{
    case ${1:-all} in
        all|"")                                   all;;
        test-serve-tcp)                           test-serve-tcp "$@";;
        test-serve-uds)                           test-serve-uds "$@";;
        test-host-port)                           test-host-port "$@";;
        test-python-page)                         test-python-page "$@";;
        test-markdown)                            test-markdown "$@";;
        test-404)                                 test-404 "$@";;
        test-init)                                test-init "$@";;
        test-config-auto)                         test-config-auto "$@";;
        test-config-explicit)                     test-config-explicit "$@";;
        test-flag-override)                       test-flag-override "$@";;
        test-missing-content)                     test-missing-content "$@";;
        test-env-only)                            test-env-only "$@";;
        test-port-socket-mutex)                   test-port-socket-mutex "$@";;
        *)                                 printf 'Unknown test: %s\n' "$1" >&2; exit 1 ;;
    esac
}


if ! (return 0 2>/dev/null); then
    main "$@"
fi
