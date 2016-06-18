CC=chmod

# servers executables

servers: httpserver dnsserver

scripts: setup.sh deployCDN runCDN stopCDN

all: scripts servers


httpserver: Makefile
	${CC} 775 ./httpserver

dnsserver: Makefile
	${CC} 775 ./dnsserver

setup.sh: Makefile
	${CC} 775 ./setup.sh

deployCDN: Makefile
	${CC} 775 ./deployCDN

runCDN: Makefile
	${CC} 775 ./runCDN

stopCDN: Makefile
	${CC} 775 ./stopCDN

clean: Makefile
	rm ./*.pyc

