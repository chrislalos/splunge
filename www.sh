#! /usr/bin/env bash

main ()
{
    www --with-config "$(dirname "$0")/.splunge.env"
}


(return 0 2>/dev/null) || main "$@"