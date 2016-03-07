 Chaos Projectile - Run 'n' Gun meets RPG
==========================================

Synopsis
--------

Chaos Projectile is an open source 2-dimensional action arcade game with
role-playing elements, currently in development.

![screenshot](doc/source/screenshot.png)

The game is set in the run’n’gun genre but there will also be character
development system with which the character can gain additional attri-
butes or actions permanently over the course of the game. Every level
has multiple exits. Dependent on what exit the player chooses, different
character attributes get changed or actions unlocked. The setting is inspired
after ancient Egypt. Visual elements of the Art Nouveau era are present, as well
as influences from the Cthulhu cult by Lovecraft.

![screenshot](doc/source/screenshot2.png)

Used Libraries
--------

- Pygame:  http://www.pygame.org/news.html
- PyTMX:  https://github.com/bitcraft/pytmx
- pyscroll:  https://github.com/bitcraft/pyscroll

Run the game
--------
After pulling the repository, you can run the game using the following commands:
- apt-get install python-pygame python-pip 
- pip install pytmx 'pyscroll<2.16.2' --force-reinstall
- cd src
- python game.py

As the game was mainly developed on Debian-like systems, those commands assume Python and apt-get to be available. If you run the game on non-Debian Operating Systems, you won't be able to run the first command. Thus, you will need to install [PyGame](https://pygame.org/download.shtml) (used engine) and [pip](https://pypi.python.org/pypi/pip/) (installer for the pytmx and pyscroll) from other sources.

![screenshot](doc/source/screenshot3.png)

Developers
--------

- Code by Anna Dorokhova is licensed under [GNU GPLv3](http://www.gnu.org/licenses/gpl-3.0.html)
-  2D game art assets by Anna Dorokhova are licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Leveldesign and balancing by Maik Helfrich [GNU GPLv3](http://www.gnu.org/licenses/gpl-3.0.html)

