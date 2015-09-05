Frikanalen MLT TV playout
=========================

The latest version of the source is available from
https://github.com/Frikanalen/mltplayout .

Trying it out
-------------

It's currently not that easy to try out. Hopefully it'll become easier to set
up in the future.  Right now we can give a few tips on how to proceed.

This should give you a screen coming up when you're finished.

    # Create a virtual environment to install the python dependencies
    virtualenv2 env

    # Activate the environment
    . env/bin/activate

    # Install the requirements
    pip install -r requirements.txt

    # You also need to install mlt, the mlt python bindings and VLC
    sudo apt install python-mlt vlc  # Debian and Ubuntu

    # And try the software (it probably won't run yet, you might need to tweak a
    # bit more).
    python bin/integrated.py
