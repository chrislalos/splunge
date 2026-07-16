#! /usr/bin/env bash

SCRIPT_DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")
PROJECT_DIR="$SCRIPT_DIR/.."

command -v gunicorn >/dev/null || {
    printf 'gunicorn not found. Activate a venv with splunge installed:\n' >&2
    printf '  source venv/bin/activate\n' >&2
    exit 1
}

WWW=$(printf '%s' "$PROJECT_DIR/scripts/www")
[[ -f "$WWW" ]] || { printf 'www not found\n' >&2; exit 1; }

cd "$PROJECT_DIR" || exit 1


test-serve-tcp()
{
    "$WWW" --graceful-timeout 1 --port 19871 --code-folder ./www &
    until curl -s http://localhost:19871/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19871/hello.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-serve-uds()
{
    "$WWW" --graceful-timeout 1 --socket /tmp/splunge-test-$$.sock --code-folder ./sample-site &
    until curl -s --unix-socket /tmp/splunge-test-$$.sock http://localhost/index.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt --unix-socket /tmp/splunge-test-$$.sock http://localhost/index.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    rm -f /tmp/splunge-test-$$.sock
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-host-port()
{
    "$WWW" --graceful-timeout 1 --host 127.0.0.1 --port 19872 --code-folder ./www &
    until curl -s http://127.0.0.1:19872/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://127.0.0.1:19872/hello.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-python-page()
{
    "$WWW" --graceful-timeout 1 --port 19873 --code-folder ./www &
    until curl -s http://localhost:19873/foo.py | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19873/foo.py)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-markdown()
{
    "$WWW" --graceful-timeout 1 --port 19874 --code-folder ./www &
    until curl -s http://localhost:19874/hello.md | grep -q .; do sleep 1; done

    curl -s http://localhost:19874/hello.md | grep -q "helloooo"
    local result=$?
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$result" -eq 0 ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-404()
{
    "$WWW" --graceful-timeout 1 --port 19875 --code-folder ./www &
    until curl -s http://localhost:19875/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19875/nonexistent)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "404" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-init()
{
    local tmpDir; tmpDir=$(mktemp -d --tmpdir test-www-init.XXXXXX)
    pushd "$tmpDir" >/dev/null || return 1

    printf "testproj\n./web\ntcp\nlocalhost\n80\n\n$HOME/tmp/testproj/log/splunge.log\n\ny\n" | "$WWW" init 2>/dev/null
    local result=$?

    popd >/dev/null
    [[ "$result" -eq 0 && -f "$tmpDir/.splunge.env" ]] \
        && { printf '  PASS\n'; return 0; } \
        || { printf '  FAIL\n'; return 1; }
}


test-config-auto()
{
    "$WWW" --graceful-timeout 1 --port 19876 --code-folder ./sample-site &
    until curl -s http://localhost:19876/some-values.py | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19876/some-values.py)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-config-explicit()
{
    mkdir -p /tmp/splunge-cfg
    cat > /tmp/splunge-cfg/env <<EOF
SPLUNGE_PORT=19877
SPLUNGE_CODEFOLDER=./www
EOF

    "$WWW" --graceful-timeout 1 --with-config /tmp/splunge-cfg/env &
    until curl -s http://localhost:19877/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19877/hello.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-flag-override()
{
    "$WWW" --graceful-timeout 1 --port 19878 --code-folder ./www &
    until curl -s http://localhost:19878/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19878/hello.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-missing-content()
{
    "$WWW" --graceful-timeout 1 --port 80 --code-folder /nonexistent 2>&1 | grep -qi 'not found'
    local result=$?
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$result" -eq 0 ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-env-only()
{
    export SPLUNGE_PORT=19879 SPLUNGE_CODEFOLDER=./www
    "$WWW" --graceful-timeout 1 &
    until curl -s http://localhost:19879/hello.html | grep -q .; do sleep 1; done

    local code
    code=$(curl -s -w "%{http_code}" -o /tmp/_splunge_test_body.txt http://localhost:19879/hello.html)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-port-socket-mutex()
{
    "$WWW" --graceful-timeout 1 --port 80 --socket /tmp/s 2>&1 | grep -q "mutually exclusive"
    local result=$?
    [[ "$result" -eq 0 ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
}


test-python-path()
{
    local tmpDir; tmpDir=$(mktemp -d)
    mkdir -p "$tmpDir/mylib"
    printf 'def hello(): return "hello"\n' > "$tmpDir/mylib/__init__.py"
    printf 'from mylib import hello\n_ = {"output": hello()}\n' > "$tmpDir/import_test.pyp"

    "$WWW" --graceful-timeout 1 --port 19900 --code-folder "$tmpDir" \
           --python-path "$tmpDir" &
    until curl -s -w '%{http_code}' --output /tmp/_poll.txt http://localhost:19900/import_test.pyp \
           | grep -q '^[2-5]'; do sleep 1; done

    local code
    code=$(curl -s -w '%{http_code}' -o /tmp/_body.txt http://localhost:19900/import_test.pyp)
    local jp; jp=$(jobs -p); [[ -n "$jp" ]] && kill $jp; wait
    [[ "$code" == "200" ]] && { printf '  PASS\n'; return 0; } || { printf '  FAIL\n'; return 1; }
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
        test-python-path
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
        test-python-path)                          test-python-path "$@";;
        *)                                 printf 'Unknown test: %s\n' "$1" >&2; exit 1 ;;
    esac
}


if ! (return 0 2>/dev/null); then
    main "$@"
fi
