from inspy_logger import InspyLogger, Loggable

ROOT_LOGGER = InspyLogger(name="APIKeyPER", console_level='info', no_file_logging=True)

MOD_LOGGER = ROOT_LOGGER.get_child('log_engine')


__all__ = [
    'Loggable',
    'MOD_LOGGER',
    'ROOT_LOGGER',
]
