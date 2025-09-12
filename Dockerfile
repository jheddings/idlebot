FROM python:3.13

COPY etc/example_config.yaml /etc/idlebot.yaml

COPY src uv.lock pyproject.toml README.md /tmp/idlebot/
RUN pip3 install /tmp/idlebot/ && rm -Rf /tmp/idlebot

# commands must be presented as an array, otherwise it will be launched
# using a shell, which causes problems handling signals for shutdown (#15)
ENTRYPOINT ["python3", "-m", "idlebot"]

# allow local callers to change the config file
CMD ["--config=/etc/idlebot.yaml", "run"]
