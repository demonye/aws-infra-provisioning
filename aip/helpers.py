import sys
import io
import re
import logging

require_regx = re.compile(r'^-r\s+(.+?)\.txt$')
editable_regx = re.compile(r'^(?:-e\s+|)(.+?#egg=(.+))')


class DotDict(dict):
    """ dot.notation access to dictionary attributes.
    Examples:
        dotdict = DotDict(name='Some one', age=30, weight='unknown')
        dotdict.age = 2
        print(dotdict) will be: {'name': 'Tester', 'age': 20}
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get_logger(
    name: str,
    level: int = logging.INFO,
    stream: io.TextIOWrapper = sys.stdout,
    log_format: str = '[{levelname}] [{asctime}.{msecs:.0f}] {name} {message}',
    date_format: str = '%Y-%m-%d %H:%M:%S',
) -> logging.Logger:
    """A helper function to get logger for printing logs

    Parameters
    ----------
    name : str
        logger name showing in the log
    level : int
        log level, logging.DEBUG, INFO, WARN, ERROR, CRITICAL
    stream : io.TextIOWrapper
        stream to print out the log
    log_format : str
        log_format
    date_format : str
        datetime format in the log

    Returns
    -------
    logging.Logger

    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(log_format, datefmt=date_format, style='{')
    ch = logging.StreamHandler(stream)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_install_requires(name: str = 'base', base_dir: str = 'requirements') -> list:
    """Get requirements from {name}.txt file

    Sample contents in the requirements file:
      aws-ckd==1.77.0
      -r base.txt
      -e git+https://github.com/aws/aws-cdk.git@master#egg=aws-cdk

    Parameters
    ----------
    name : str
        requirements filename,

    Returns
    -------
    requirements list

    """
    requirements = []
    with open(f'{base_dir}/{name}.txt') as fp:
        for line in fp:
            req = line.strip()
            if req.startswith('#'):
                continue
            m = require_regx.match(req)
            if m:
                requirements += get_install_requires(m.group(1), base_dir)
                continue
            m = editable_regx.match(req)
            if m:
                requirements.append(f'{m.group(2)} @ {m.group(1)}')
                continue
            requirements.append(req)
    return requirements
