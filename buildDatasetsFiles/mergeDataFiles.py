
import sys

def insert_lines(dest, first, second):
    lines = []
    with open(first, 'r') as ff:
        lines += ff.readlines()
    with open(second, 'r') as sf:
        lines += sf.readlines()

    with open(dest, 'w') as df:
        df.writelines(lines)




if __name__ == "__main__":
    first_file = sys.argv[1]
    second_file = sys.argv[2]
    dest_path = sys.argv[3]
    insert_lines(dest_path, first_file, second_file)


