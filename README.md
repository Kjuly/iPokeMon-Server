iPokeMon (Server)
=================

[![Build Status](https://travis-ci.org/Kjuly/iPokeMon-Server.png)](https://travis-ci.org/Kjuly/iPokeMon-Server)

# Description

This is iPokeMon Server's source code. It uses [Redis][URL:Redis] as its database.

# What is iPokeMon?

View the detail description [HERE][URL:iPokeMon Project Page].

> [CLIENT SOURCE CODE](https://github.com/Kjuly/iPokeMon).

# Usage

Run it locally:

    $ cd iPokeMon-Server
    $ redis-server /etc/redis.conf
    $ python server.py

Or on remote (e.g. Amazon Web Service):

    $ ssh -D 7070 ubuntu@<server-ip>
    $ cd iPokeMon-Server
    $ redis-server /etc/redis.conf &
    $ nohup python server.py &

Shutdown:

    $ redis-cli
    $ > shutdown
    $ > exit
    $ ps aux | grep server
    $ kill -9 <server.py's pid>


  [URL:iPokeMon Project Page]: http://dev.kjuly.com/iPokeMon
  [URL:Redis]: http://redis.io

