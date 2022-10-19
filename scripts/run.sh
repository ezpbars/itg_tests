#!/usr/bin/env bash
main() {
    . venv/bin/activate
    . /home/ec2-user/config.sh
    python main.py
}

main
