#! /usr/bin/env bash

main ()
{
    www 1313 ./www
}


(return 0 2>/dev/null) || main "$@"