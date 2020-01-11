# Makefile for idlebot

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= idlebot
APPVER ?= 1.1

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
	python3 $(SRCDIR)/main.py --config=$(BASEDIR)/idlebot.cfg

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

