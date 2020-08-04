FROM pybase:3.8

COPY src/main.py src/irc.py src/idlerpg.py /usr/local/pybot/
COPY idlebot.cfg /etc/idlebot.cfg

CMD ["python", "/usr/local/pybot/main.py", "--config=/etc/idlebot.cfg"]
