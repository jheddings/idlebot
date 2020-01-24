# Makefile for idlebot

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= idlebot
APPVER ?= 1.3

PY := PYTHONPATH="$(SRCDIR)" python3

################################################################################
.PHONY: all build test release runpy runc rund runpy run distclean

################################################################################
all: build

################################################################################
build: test
	docker build -t $(APPNAME):dev $(BASEDIR)

################################################################################
release: build
	docker tag $(APPNAME):dev $(APPNAME):latest
	docker tag $(APPNAME):latest $(APPNAME):$(APPVER)

################################################################################
test:
	$(PY) -m unittest discover -v -s $(BASEDIR)/test

################################################################################
runpy:
	$(PY) $(SRCDIR)/main.py --config=$(BASEDIR)/idlebot.cfg

################################################################################
runc: build
	docker run -it $(APPNAME):dev

################################################################################
rund: release
	docker run --rm --detach $(APPNAME):latest

################################################################################
clean:
	rm -Rf $(SRCDIR)/__pycache__
	docker rmi --force $(APPNAME):dev

