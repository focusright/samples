
GAME = 'Geometry Cometry'
AUTHOR_NAME = 'David Cooper'
AUTHOR_EMAIL = 'dave@kupesoft.com'
AUTHOR = '%s <%s>' % (AUTHOR_NAME, AUTHOR_EMAIL)
VERSION = '0.1-dev'

LICENSE = '''\
Copyright (c) 2008, David Cooper <dave@kupesoft.com>
All rights reserved.

Dedicated to Kate Lacey

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyright notice, the above dedication, and this
permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.'''

# Screen width and height. These values need to be fixed at (800, 600).
# Change these if you want but be forwarned, YMMV!
WIDTH, HEIGHT = (800, 600)

DATA_DIRNAME = 'data'
FONT_FILENAME = 'font.ttf'

SOUND_FILES = ('explode.wav', 'laser.wav', 'music.wav', 'title.wav')

BACKGROUND = (0x11, 0x11, 0x11)
WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x00, 0x00, 0x00)

TRANSPARENT = BLACK

HIGHSCORES_AMOUNT = 10

FRAME_RATE = 60
MENU_FRAME_RATE = 24
