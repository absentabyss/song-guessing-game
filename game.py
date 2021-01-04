#!/bin/env python

from datetime import datetime as dt
from math import trunc
from os import system, walk
from random import choice, randint
from re import escape
import datetime
import subprocess

FOLDERS = [
#        "teotb", 
        "aivaib",
        ]
print(FOLDERS)

def song_length(folder, song):
    ffprobe = subprocess.Popen(["ffprobe", "{}/{}".format(folder, song)], stderr=subprocess.PIPE)
    sed = subprocess.check_output(["sed", "-n", "s/^.*Duration:\\s*\\([0-9:]*\\).*$/\\1/p"], stdin=ffprobe.stderr)
    length = sed.decode("utf-8")
    length = length.split(":")
    length = int(length[0]) * 3600 + int(length[1]) * 60 + int(length[2][:-1])
    return length

GUESS_LIMIT = 10
songs = []
for f in FOLDERS:
    for s in next(walk(f))[-1]:
        songs.append((f, s, song_length(f, s)))

def secs_to_mins(secs):
    return "{:02.0f}:{:02.0f}".format(trunc(secs / 60), secs % 60)

def record(streak):
    with open("pb", 'r') as f:
        pb = int(f.read())
    if streak > pb:
        print("Keep it going!")
        with open("pb", 'w') as f:
            f.write(str(streak))

streak = 0
while True:
    start = dt.now()
    song = choice(songs)
    delay = randint(0, song[2] - GUESS_LIMIT)
    print("Reproducing at {}.".format(secs_to_mins(delay)))
    p = subprocess.Popen(["play", "{}/{}".format(song[0], escape(song[1])),
        "trim", "{}".format(delay)], stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while True:
        guess = input()
        if guess == song[1]:
            p.kill()
            guess_time = dt.now() - start
            print("Correct!\nGuessed in {}.".format(guess_time))
            if guess_time < datetime.timedelta(seconds=GUESS_LIMIT):
                streak += 1
                print("Current streak: {}.".format(streak))
                record(streak)
            else:
                streak = 1
                print("Too slow! You lost your streak.")
            break
        elif guess == "Skip!":
            p.kill()
            print("It was: {}.".format(song[1]))
            streak = 0
            print("You lost your streak.")
            break
        else:
            print("Nope.")
            streak = 0
            start = dt.now()
