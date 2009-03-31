
CFLAGS:=`pkg-config --cflags pycairo cairo glib-2.0`
CFLAGS+=`python-config --include --cflags `
CFLAGS+=-c -fPIC
LDFLAGS:= `pkg-config --libs pycairo cairo glib-2.0` `python-config --libs --ldflags` -ltiff

image.so: wrap_image.c image.c image.h
	gcc -g -O2 -Wall $(CFLAGS) image.c -o modul_image.o
	gcc -g -O2 -Wall $(CFLAGS) wrap_image.c -o wrap_image.o
	gcc -shared $(LDFLAGS) wrap_image.o modul_image.o -o image.so

.PHONY : clean
clean :
	-rm *.o *.so