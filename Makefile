
.PHONY : all
all : 
	$(MAKE) -C image

.PHONY : clean
clean :
	$(MAKE) -C image clean
	find . -name '*.pyc' -delete
