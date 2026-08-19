import argparse


class AppendWithMulti(argparse.Action):
    ''' Allow multiple occurrences of a flag
        Each flag can have one or more arguments:
        e.g. --file foo.txt --file bar.txt bum.txt
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest) or []
        current.extend(values)
        setattr(namespace, self.dest, current)


class ToScalar(argparse.Action):
    ''' argparse doesn't have a good way of specifying 'give me 1 value.'
        I'm serious. Just one. nargs=1 is close but it returns a list
        of one value. ToScalar converts this list to a single value
        which is what anyone specifying nargs=1 actually wants.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        if values and len(values) > 1:
            raise ValueError(f'>1 values ({len(values)})')
        val = values[0] if values else None
        setattr(namespace, self.dest, val)


def create_parser():
	''' arg parser w subcommands '''
	parser = argparse.ArgumentParser(prog='')
	parser.add_argument('--content', nargs=1, required=True, action=ToScalar, dest='content')
	parser.add_argument('--tests', nargs=1, required=True, action=ToScalar, dest='tests')
	return parser


def main ():
	print("brap-brap")
	parser = create_parser()
	args = parser.parse_args()
	print(f'content={args.content}')
	print(f'tests={args.tests}')


if __name__ == '__main__':
	main()
