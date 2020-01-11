# Makefile for idlebot

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src
APPNAME ?= idlebot

# commands used in the makefile
PYENV := PYTHONPATH=$(BASEDIR)/indigo-idlerpg/src
PY := $(PYENV) python3

################################################################################
.PHONY: all build runpy clean run

################################################################################
all: build

################################################################################
build:
	docker build -t $(APPNAME) $(BASEDIR)

################################################################################
runpy:
	$(PY) $(SRCDIR)/idlebot.py --config=$(BASEDIR)/idlebot.cfg

################################################################################
run: build
	docker run --rm --detach $(APPNAME)

################################################################################
clean:
	docker rmi --force $(APPNAME)

