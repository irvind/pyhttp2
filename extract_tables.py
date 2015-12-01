import os
import argparse


def extract_static_table():
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'static_table.txt'
    )

    with open(path, 'r') as f:
        print('(')

        lines = list(f)
        for line in lines[3:len(lines)-1]:
            sp = line.split('|')
            name = sp[2].strip()
            value = sp[3].strip()
            print("    ('{0}', '{1}'),".format(name, value))

        print(')\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data (as tuples) from *.txt tables of this repo.')
    parser.add_argument('-s', '--static', action='store_true', help='print static tuple')
    parser.add_argument('-H', '--huffman', action='store_true', help='print huffman tuple')

    args = parser.parse_args()
    if args.static:
        extract_static_table()
    if args.huffman:
        pass
