from typing import Optional
from contextlib import contextmanager
from loguru import logger
from fastapi import Request

from .settings import logger_settings as settings


class LoggerHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the logger and setup basic configurations
        """
        if not hasattr(self, 'initialized'):
            self.create_instance()
            self.initialized = True

    def create_instance(self):
        """
        Create a new instance of the logger
        """
        try:
            settings.ensure_dir()

            logger.add(
                "logs/application.log",
                colorize=True,
                level=settings.level,
                format=settings.format_loguru,
                rotation=settings.rotation,
                enqueue=True, # async logging while ensuring thread safety and order (integrity)
                backtrace=True, # for debugging purposes
                diagnose=True, # for debugging purposes
                )

            with logger.contextualize(task='logger', args=''):
                logger.info('Logger initialized successfully')
        except Exception as e:
            err_msg = 'Failed to initialize logger'
            print(f"{err_msg}: {e}")
            raise ValueError(err_msg)

    @logger.catch
    def list_logs_files(self) -> list:
        """
        List the log files in the log directory
        """
        try:
            return settings.existing_logs_files
        except Exception as e: # pylint: disable=unused-variable
            err_msg = 'Failed to list log files from directory'
            logger.exception(err_msg, task='logger', args='')
            return []

    @contextmanager
    def get_logger(self,
                task: str = '',
                request: Optional[Request] = None,
                service_name: Optional[str] = None
                ):
        """
        Return the logger instance
        """
        # create a dict from the args "request", "slug", "hash", "url", "text_content", "force_reprocess" that are not None
        args = {k: str(v) for k, v in locals().items() if v is not None and k != 'self' and k != 'task'}
        args = '' if args == {} else args
        with logger.contextualize(task=task, args=args):
            yield logger

    def log_spacers(self, separator: str = '-') -> None:
        """
        Log separators
        """
        logger.info(separator * 50, task='lifespan', args='')

    def log_lifespan(self, message: str = "Application", shutdown: bool = False) -> None:
        """
        Log lifespan messages
        """
        self.log_spacers() if not shutdown else None # pylint: disable=expression-not-assigned
        logger.info(f'>>> {"Initializing" if not shutdown else "Shutingdown"} {message} <<<', task='lifespan', args='')
        self.log_spacers() if shutdown else None # pylint: disable=expression-not-assigned

    @logger.catch
    def get_logs(self, log_file: str = None, last_n_lines: int = 10) -> list:
        """
        Get the logs from the log file; by default, the last 10 lines and the current log file
        """
        try:
            if not log_file:
                log_file = settings.log_file
            with open(settings.log_dir, 'r') as f: # pylint: disable=unspecified-encoding
                lines = f.readlines()
                return lines[-last_n_lines:]
        except Exception as e: # pylint: disable=unused-variable
            error_message = f"Failed to retrieve last {last_n_lines} lines from log file: {log_file}"
            logger.exception(error_message, last_n_lines=last_n_lines, log_file=log_file, task='logger', args='')
            return []

def get_logger(task: str = '',
               request: Optional[Request] = None,
               service_name: Optional[str] = None):
    """
    Get the logger instance
    """
    return LoggerHandler().get_logger(task=task, request=request, service_name=service_name)