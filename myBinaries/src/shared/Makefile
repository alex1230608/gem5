prog=shared
all:
	g++ -g -c $(prog).c
	g++ --static -o ../../$(prog) $(prog).o -lpthread

clean:
	rm $(prog).o ../../$(prog)
