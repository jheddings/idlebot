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
	docker image build --tag $(APPNAME):dev $(BASEDIR)

################################################################################
.PHONY: rebuild

rebuild: test
	docker image build --pull --no-cache --tag $(APPNAME):dev $(BASEDIR)

################################################################################
.PHONY: release

release: build
	docker image tag $(APPNAME):dev $(APPNAME):latest
	docker image tag $(APPNAME):latest $(APPNAME):$(APPVER)

################################################################################
.PHONY: test

# TODO use a container for tests...

test:
	$(PY) -m unittest discover -v -s $(BASEDIR)/test

################################################################################
.PHONY: run

run:
	$(PY) $(SRCDIR)/main.py --config=$(BASEDIR)/idlebot.cfg

################################################################################
.PHONY: runc

runc: build
	docker container run --interactive --tty $(APPNAME):dev

################################################################################
.PHONY: rund

rund: release
	docker container run --rm --detach $(APPNAME):latest

################################################################################
.PHONY: runs

runs: release
	docker container run --restart always --detach $(APPNAME):latest

################################################################################
.PHONY: clean

clean:
	rm -f $(SRCDIR)/*.pyc
	rm -Rf $(SRCDIR)/__pycache__
	rm -f $(BASEDIR)/test/*.pyc
	rm -Rf $(BASEDIR)/test/__pycache__

################################################################################
.PHONY: clobber

clobber: clean
	docker image rm --force $(APPNAME):dev
	docker image rm --force $(APPNAME):latest
