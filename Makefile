# Makefile for idlebot

BASEDIR ?= $(PWD)
SRCDIR ?= $(BASEDIR)/src

APPNAME ?= idlebot
APPVER ?= 1.4

PY := PYTHONPATH="$(SRCDIR)" python3

################################################################################
.PHONY: all

all: build

################################################################################
.PHONY: build

build: test
	docker build -t $(APPNAME):dev $(BASEDIR)

################################################################################
.PHONY: release

release: build
	docker tag $(APPNAME):dev $(APPNAME):latest
	docker tag $(APPNAME):latest $(APPNAME):$(APPVER)

################################################################################
.PHONY: test

test:
	$(PY) -m unittest discover -v -s $(BASEDIR)/test

################################################################################
.PHONY: run

run:
	$(PY) $(SRCDIR)/main.py --config=$(BASEDIR)/idlebot.cfg

################################################################################
.PHONY: runc

runc: build
	docker run -it $(APPNAME):dev

################################################################################
.PHONY: rund

rund: release
	docker run --rm --detach $(APPNAME):latest

################################################################################
.PHONY: clean

clean:
	rm -Rf $(SRCDIR)/__pycache__
	docker rmi --force $(APPNAME):dev

################################################################################
.PHONY: clobber

clobber: clean
	docker rmi --force $(APPNAME):latest

