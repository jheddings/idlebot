FROM python:3.7

COPY src/main.py /usr/local/pybot/
COPY src/irc.py /usr/local/pybot/
COPY src/idlerpg.py /usr/local/pybot/
COPY idlebot.cfg /etc/idlebot.cfg

RUN pip install pyyaml

CMD ["python", "/usr/local/pybot/main.py", "/etc/idlebot.cfg"]
