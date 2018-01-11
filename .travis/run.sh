#!/bin/bash

set -e
set -x

export CONAN_PRINT_RUN_COMMANDS=1

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

python build.py
