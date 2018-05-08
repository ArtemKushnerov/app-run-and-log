import logging

import subprocess


def log(msg_before, level=logging.INFO):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            msg = f'{self.apk.package}, {self.apk.type}: {msg_before}'
            logging.log(level, msg)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def exception(WrapperException=None, proceed_anyway=False, suppress_output=False):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if type(e) is subprocess.CalledProcessError:
                    out = e.output.decode('utf-8')
                    wrapped_exception = WrapperException(out)
                    if proceed_anyway:
                        logging.info(f'Proceeding after {wrapped_exception.__class__.__name__} happened')
                        if not suppress_output:
                            logging.error(wrapped_exception)
                    else:
                        raise wrapped_exception
                else:
                    raise e
        return wrapper

    return decorator

