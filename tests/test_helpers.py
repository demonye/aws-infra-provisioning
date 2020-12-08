import os
import sys
import re
from io import StringIO
import tempfile
import unittest

from src.lib.helpers import (
    get_logger,
    get_install_requires,
)


class TestInstallRequires(unittest.TestCase):
    requires = {
        'base.txt': [
            'abc==1.0',
            ' xyz==3.4.5 ',
            ' -e  git+https://git.example.com/MyProject@v1.0#egg=MyProject',
            'hg+http://hg.example.com/MyProject@special_feature#egg=MyProject',
            '  svn+ssh://user@svn.example.com/MyProject#egg=MyProject',
        ],
        'require1.txt': [
            '-r base.txt',
            'ABC==10.0.1',
        ],
        'require2.txt': [
            '-r require1.txt',
            ' # comment 123456  ',
            'XYZ==20.9999',
        ]
    }
    base_result = [
        'abc==1.0',
        'xyz==3.4.5',
        'MyProject @ git+https://git.example.com/MyProject@v1.0#egg=MyProject',
        'MyProject @ hg+http://hg.example.com/MyProject@special_feature#egg=MyProject',
        'MyProject @ svn+ssh://user@svn.example.com/MyProject#egg=MyProject',
    ]
    base_dir = None

    @classmethod
    def setUpClass(cls):
        def _write_requires_file(filename, requires):
            with open(os.path.join(cls.base_dir, filename), 'w') as fp:
                for line in requires:
                    fp.write(f'{line}\n')

        cls.base_dir = tempfile.mktemp()
        os.makedirs(cls.base_dir)
        for filename, requires in cls.requires.items():
            _write_requires_file(os.path.join(cls.base_dir, filename), requires)

    @classmethod
    def tearDownClass(cls):
        if cls.base_dir:
            for filename in os.listdir(cls.base_dir):
                os.unlink(os.path.join(cls.base_dir, filename))
            os.rmdir(cls.base_dir)

    def test_base(self):
        requires = get_install_requires('base', self.base_dir)
        assert requires == self.base_result

    def test_require1(self):
        requires = get_install_requires('require1', self.base_dir)
        assert requires == self.base_result + [
            'ABC==10.0.1'
        ]

    def test_require2(self):
        requires = get_install_requires('require2', self.base_dir)
        assert requires == self.base_result + [
            'ABC==10.0.1',
            'XYZ==20.9999',
        ]


class TestGetLogger(unittest.TestCase):

    def test_get_logger_default(self):
        name = 'test123'
        message = 'test message'
        stream = StringIO()
        logger = get_logger(name, stream=stream)
        logger.info(message)
        log_message = stream.getvalue()

        date_regx = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}'
        m = re.match(rf"^\[INFO\] \[{date_regx}\] (.+?) (.*)\n$", log_message)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), name)
        self.assertEqual(m.group(2), message)
