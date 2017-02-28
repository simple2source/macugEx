import pathlib2
import argparse
import stat
import glob.fnmatch

parser = argparse.ArgumentParser(prog='find')
parser.add_argument('path')
parser.add_argument('-name', dest='name', type=str)
parser.add_argument('-executable', dest='executable', action='store_true')

args = parser.parse_args()


def _walk(path):
    for item in path.iterdir():
        if item.is_dir():
            for ite in _walk(item):
                yield ite
        yield item


def walk(path):
    for x in pathlib2.Path(path):
        yield _walk(x)


def is_executable(item):
    mode = item.lstat().st_mode
    return stat.S_IEXEX & mode > 0


if __name__ == '__main__':
    for item in walk(args.path):
        print(item)