FROM python:3.7

COPY src/idlebot.py /usr/local/pybot/
COPY indigo-idlerpg/src/irc.py /usr/local/pybot/
COPY idlebot_prod.cfg /etc/idlebot.cfg

RUN pip install pyyaml

CMD ["python", "/usr/local/pybot/idlebot.py", "/etc/idlebot.cfg"]
