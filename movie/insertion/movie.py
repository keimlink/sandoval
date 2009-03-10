import sys

import models

if __name__ == '__main__':
    if len(sys.argv) == 1 or len(sys.argv[1]) == 0:
        print 'No movie name given!'
        sys.exit(1)
    for number in range(1, len(sys.argv)):
        models.Movie(sys.argv[number])
