from logging import INFO, basicConfig, getLogger

basicConfig(
    level=INFO,
    format='[%(levelname)s]: %(asctime)s -- %(message)s',
)

logger = getLogger()
