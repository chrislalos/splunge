import pytest
from splunge.cli import create_parser


class TestBind:
    @staticmethod
    def parse(argv):
        return create_parser().parse_args(argv)

    def test_bind_value(self):
        args = self.parse(['init', '--bind', 'localhost:8000'])
        assert args.bind == ['localhost:8000']

    def test_bind_unix_socket(self):
        args = self.parse(['init', '--bind', 'unix:/tmp/splunge.sock'])
        assert args.bind == ['unix:/tmp/splunge.sock']

    def test_bind_ipv6(self):
        args = self.parse(['init', '--bind', '[::1]:8080'])
        assert args.bind == ['[::1]:8080']

    def test_bind_with_folder_flags(self):
        args = self.parse([
            'init',
            '--bind', 'localhost:8000',
            '--code-folder', './py',
            '--content-folder', './www',
        ])
        assert args.bind == ['localhost:8000']
        assert args.codeFolder == ['./py']
        assert args.contentFolder == ['./www']

    def test_bind_last_wins(self):
        args = self.parse([
            'init',
            '--bind', '127.0.0.1:8000',
            '--bind', '0.0.0.0:9000',
        ])
        assert args.bind == ['0.0.0.0:9000']

    def test_bind_no_value_fails(self):
        with pytest.raises(SystemExit):
            self.parse(['init', '--bind'])


class TestName:
    @staticmethod
    def parse(argv):
        return create_parser().parse_args(argv)

    def test_name_value(self):
        args = self.parse(['init', '--name', 'myapp'])
        assert args.name == ['myapp']

    def test_name_multipart(self):
        args = self.parse(['init', '--name', 'my-cool-app'])
        assert args.name == ['my-cool-app']

    def test_name_with_flags(self):
        args = self.parse([
            'init', '--name', 'myapp',
            '--bind', 'localhost:8000',
            '--code-folder', './py',
        ])
        assert args.name == ['myapp']
        assert args.bind == ['localhost:8000']
        assert args.codeFolder == ['./py']

    def test_name_last_wins(self):
        args = self.parse([
            'init',
            '--name', 'app1',
            '--name', 'app2',
        ])
        assert args.name == ['app2']

    def test_name_no_value_fails(self):
        with pytest.raises(SystemExit):
            self.parse(['init', '--name'])


class TestRun:
    @staticmethod
    def parse(argv):
        return create_parser().parse_args(argv)

    def test_run_bind_value(self):
        args = self.parse(['run', '--bind', 'localhost:8000'])
        assert args.bind == ['localhost:8000']

    def test_run_name_value(self):
        args = self.parse(['run', '--name', 'myapp'])
        assert args.name == ['myapp']

    def test_run_folder_flag(self):
        args = self.parse(['run', '--code-folder', './a'])
        assert args.codeFolder == ['./a']

    def test_with_config_omitted(self):
        args = self.parse(['run'])
        assert args.withConfig == './.splunge.cfg.py'

    def test_with_config_implied(self):
        args = self.parse(['run', '--with-config'])
        assert args.withConfig == './.splunge.cfg.py'

    def test_with_config_explicit(self):
        args = self.parse(['run', '--with-config', './other.py'])
        assert args.withConfig == './other.py'

    def test_run_all_flags(self):
        args = self.parse([
            'run',
            '--bind', 'localhost:8000',
            '--name', 'myapp',
            '--code-folder', './py',
            '--with-config', './custom.py',
        ])
        assert args.bind == ['localhost:8000']
        assert args.name == ['myapp']
        assert args.codeFolder == ['./py']
        assert args.withConfig == './custom.py'

    def test_run_unknown_flag_fails(self):
        with pytest.raises(SystemExit):
            self.parse(['run', '--bogus'])


class TestAppendWithMulti:
    @staticmethod
    def parse(argv):
        return create_parser().parse_args(argv)

    def test_single(self):
        args = self.parse(['init', '--code-folder', './a'])
        assert args.codeFolder == ['./a']

    def test_multi_arg(self):
        args = self.parse(['init', '--code-folder', './a', './b'])
        assert args.codeFolder == ['./a', './b']

    def test_multi_flag(self):
        args = self.parse([
            'init', '--code-folder', './a',
            '--code-folder', './b', './c',
        ])
        assert args.codeFolder == ['./a', './b', './c']

    def test_different_flags_dont_interfere(self):
        args = self.parse([
            'init', '--code-folder', './a',
            '--template-folder', './t',
        ])
        assert args.codeFolder == ['./a']
        assert args.templateFolder == ['./t']

    def test_content_folder_single(self):
        args = self.parse(['init', '--content-folder', './www'])
        assert args.contentFolder == ['./www']

    def test_content_folder_multi_arg(self):
        args = self.parse(['init', '--content-folder', './www', './static'])
        assert args.contentFolder == ['./www', './static']

    def test_content_folder_multi_flag(self):
        args = self.parse([
            'init',
            '--content-folder', './www',
            '--content-folder', './static', './assets',
        ])
        assert args.contentFolder == ['./www', './static', './assets']

    def test_all_folder_flags(self):
        args = self.parse([
            'init',
            '--code-folder', './py',
            '--content-folder', './www',
            '--template-folder', './templates',
        ])
        assert args.codeFolder == ['./py']
        assert args.contentFolder == ['./www']
        assert args.templateFolder == ['./templates']

    def test_all_folder_flags_multi(self):
        args = self.parse([
            'init',
            '--code-folder', './py', './lib',
            '--content-folder', './www', './static', './assets',
            '--template-folder', './templates',
            '--code-folder', './extra',
        ])
        assert args.codeFolder == ['./py', './lib', './extra']
        assert args.contentFolder == ['./www', './static', './assets']
        assert args.templateFolder == ['./templates']

    def test_unknown_flag_fails(self):
        with pytest.raises(SystemExit):
            self.parse(['init', '--bogus'])
