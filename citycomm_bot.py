from __future__ import with_statement

import sys
import json

def read_config():
    ERROR_MESSAGE = "Configuration error.\n"
    CONFIG_FILE = 'config.json'
    try:
        with open(CONFIG_FILE) as fp:
            config = json.load(fp)
            try:
                assert 'twitter' in config
                assert 'consumer_key' in config['twitter']
                assert 'consumer_secret' in config['twitter']
                assert 'access_token' in config['twitter']
                assert 'access_token_secret' in config['twitter']
            except AssertionError:
                sys.stderr.write(ERROR_MESSAGE)
                exit(1)
            return config
    except IOError:
        sys.stderr.write(ERROR_MESSAGE)
        exit(1)

def main():
    config = read_config()

if __name__ == '__main__':
    main()
