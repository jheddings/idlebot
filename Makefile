# Makefile for idlebot

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= idlebot
APPVER ?= 1.0

# commands used in the makefile
PYENV := PYTHONPATH=$(BASEDIR)/indigo-idlerpg/src
PY := $(PYENV) python3

################################################################################
.PHONY: all build release runpy runc rund runpy run distclean

################################################################################
all: build

################################################################################
build:
	docker build -t $(APPNAME):dev $(BASEDIR)

################################################################################
release: build
	docker tag $(APPNAME):dev $(APPNAME):latest
	docker tag $(APPNAME):latest $(APPNAME):$(APPVER)

################################################################################
runpy:
	$(PY) $(SRCDIR)/idlebot.py --config=$(BASEDIR)/idlebot_dev.cfg

################################################################################
runc: build
	docker run -it $(APPNAME):dev

################################################################################
rund: release
	docker run --rm --detach $(APPNAME):latest

################################################################################
clean:
	docker rmi --force $(APPNAME):dev

