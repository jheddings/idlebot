"""Application configuration data for idlebot."""

import logging
import logging.config
import os
import os.path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """Application configuration for IdleBot."""

    interval: int = 60
    count: int = 3
    timeout: Optional[int] = None

    logging: Optional[Dict] = None

    @classmethod
    def load(cls, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"config file does not exist: {config_file}")

        with open(config_file) as fp:
            data = yaml.load(fp, Loader=yaml.SafeLoader)
            conf = AppConfig(**data)

        logger = cls._configure_logging(conf)
        logger.info("loaded AppConfig from: %s", config_file)

        return conf

    @classmethod
    def _configure_logging(cls, conf):
        if conf.logging is None:
            logging.basicConfig(level=logging.WARNING)
        else:
            logging.config.dictConfig(conf.logging)

        return logging.getLogger()
