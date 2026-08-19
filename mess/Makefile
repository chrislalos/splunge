CC = gcc
CFLAGS = -Wall -Wextra -pedantic -O2

idid: idid.c
	$(CC) $(CFLAGS) -o $@ $<

setuid: idid
	chown root:root idid
	chmod u+s idid

unsetuid:
	chmod u-s idid

install: setuid
	mv idid /usr/local/bin/

clean:
	rm -f idid

.PHONY: setuid unsetuid install clean
