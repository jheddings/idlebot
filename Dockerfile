FROM python:3.7

RUN pip install --upgrade pip
RUN pip install pyyaml

COPY src/main.py src/irc.py src/idlerpg.py /usr/local/pybot/
COPY idlebot.cfg /etc/idlebot.cfg

CMD ["python", "/usr/local/pybot/main.py", "--config=/etc/idlebot.cfg"]
