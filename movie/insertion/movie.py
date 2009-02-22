import sys

import models

if __name__ == '__main__':
    if len(sys.argv) == 1 or len(sys.argv[1]) == 0:
        print 'No movie name given!'
        sys.exit(1)
    models.Movie(sys.argv[1])
