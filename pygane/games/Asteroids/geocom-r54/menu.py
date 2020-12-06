import sys

import pygame

import lib
from locals import *
from config import conf
from sound import sound

class Menu(object):
    
    GAME = GAME
    ALT = '...or Once Upon a Heroic Triangle'
    VERSION = 'Version: %s' % VERSION
    WEBSITE = 'http://geocom.kupesoft.com/'
    
    TITLE_COLOUR = (0x00, 0x99, 0xFF)
    SELECTED_COLOUR = (0xFF, 0x33, 0xCC)
    
    START = 'Start'
    OPTIONS = 'Options'
    SCORES = 'High Scores'
    ABOUT = 'About'
    HELP = 'Help'
    QUIT = 'Quit'
    
    MAIN_OPTIONS = [START, OPTIONS, SCORES, HELP, ABOUT, QUIT]
    
    EFFECTS = 'Extra Effects'
    FULLSCREEN = 'Fullscreen Mode'
    SOUND = 'Sounds'
    BACK = 'Return to Main Menu'
    
    OPTIONS_OPTIONS = [EFFECTS, FULLSCREEN, SOUND, BACK]
    OPTIONS_CONF = {EFFECTS: 'effects', FULLSCREEN: 'fullscreen', SOUND: 'sound'}
    
    NOSCORES = "There are no scores available at this time"
    
    EXIT_SURE = "Are you sure?"
    YES = "Yes"
    NO = "No"
    
    EXIT_OPTIONS = [YES, NO]
    
    HELP_TEXT = '''\
The game is controlled by the following keys:

      Right/Left
           Rotate your ship clockwise or counterclockwise
      Up/Down
           Engage your thrusters forward or in reverse
      Ctrl
           Shoot your laser
      Space
           Use the special item in your cargo hold (if any)
      P/Pause
           Pause or unpause the game
      ESC
           Spontaneously combust and exit to the main menu'''
    
    HELP2_TEXT = '''\
Bonuses are green circles with one of these letters inside:

      B
           Fill your cargo hold with a laser burst cartridge
      S
           Fill your cargo hold with a temporary sheild activator
      1
           Increase your lives by one
      R
           Fill your cargo hold with a rapid fire cartridge'''
         
    
    def __init__(self, game):
        self.game = game
      
    def _return_to_menu(self):
        self._display_func = self._main
        self._action_func = self._main_action
        self._choice = self._last_choice
        self._choice_max = len(self.MAIN_OPTIONS)
        
    def show(self):
        
        sound.play('title', -1)
        
        self._last_choice = 0
        self._return_to_menu()
        background = lib.draw_background()
        
        while True:
            
            self.game.screen.blit(background, (0, 0))
            
            y_pos = 60
            
            title = lib.render_text(self.GAME, 72, self.TITLE_COLOUR)
            self.title_width = title.get_width()
            self.game.screen.blit(title, (WIDTH/2 - self.title_width/2, y_pos))
            y_pos += title.get_height()
            
            alt = lib.render_text(self.ALT, 22)
            alt_x = (WIDTH - self.title_width)/2 + self.title_width - alt.get_width() - 15
            self.game.screen.blit(alt, (alt_x, y_pos))
            y_pos += alt.get_height() + 25
            
            version = lib.render_text(self.VERSION, 14)
            self.game.screen.blit(version, (WIDTH - version.get_width() - 3,
                                      HEIGHT - version.get_height() - 1))
            website = lib.render_text(self.WEBSITE, 14)
            self.game.screen.blit(website, (3, HEIGHT - version.get_height() - 1))
            
            self._display_func(y_pos)
                
            pygame.display.update()
            self.game.clock.tick(MENU_FRAME_RATE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # if in the main menu, exit, otherwise exit to main menu
                        if self._display_func == self._main:
                            self._last_choice = self._choice
                            self._choice = self.MAIN_OPTIONS.index(self.QUIT)
                            self._main_action(False)
                        elif self._display_func == self._exit:
                            raise SystemExit
                        else:
                            self._return_to_menu()
                    elif event.key == pygame.K_UP:
                        self._choice = (self._choice - 1) % self._choice_max
                    elif event.key == pygame.K_DOWN:
                        self._choice = (self._choice + 1) % self._choice_max
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # If self._action_func() returns true, we leave the menu
                        if self._action_func():
                            sound.stop('title')
                            return
                        break
            
    def _main(self, y_pos):
        
        y_pos += 30
        
        for option_text in self.MAIN_OPTIONS:
            
            if option_text == self.MAIN_OPTIONS[self._choice]:
                colour = self.SELECTED_COLOUR
            else:
                colour = WHITE
            
            option = lib.render_text(option_text, 38, colour)
            option_width, option_height = option.get_width(), option.get_height()
            self.game.screen.blit(option, (WIDTH/2 - option_width/2, y_pos))
            
            if option_text == self.MAIN_OPTIONS[self._choice]:
                circ_y = y_pos + option_height/2
                for sign in (-1, 1):
                    circ_pos = (WIDTH/2 + sign*(option_width/2 + 25), circ_y)
                    pygame.draw.circle(self.game.screen, colour, circ_pos, 5)

            y_pos += option_height + 3
                    
    def _main_action(self, set_last_choice=True):
        '''returns True if the main menu should exit (i. e. play selected)'''
        
        if set_last_choice:
            self._last_choice = self._choice
        
        if self.MAIN_OPTIONS[self._choice] == self.START:
            return True
        elif self.MAIN_OPTIONS[self._choice] == self.OPTIONS:
            choice_max = len(self.OPTIONS_OPTIONS)
            self._choice, self._choice_max = choice_max - 1, choice_max
            self._display_func = self._options
            self._action_func = self._options_action
        elif self.MAIN_OPTIONS[self._choice] == self.SCORES:
            self._choice, self._choice_max = 0, 1
            self._display_func = self._highscores
            self._action_func = self._return_to_menu
        elif self.MAIN_OPTIONS[self._choice] == self.HELP:
            self._choice, self._choice_max = 0, 1
            self._display_func = self._help
            self._action_func = self._help_action
        elif self.MAIN_OPTIONS[self._choice] == self.ABOUT:
            self._choice, self._choice_max = 0, 1
            self._display_func = self._about
            self._action_func = self._about_action
        elif self.MAIN_OPTIONS[self._choice] == self.QUIT:
            self._choice, self._choice_max = 0, len(self.EXIT_OPTIONS)
            self._display_func = self._exit
            self._action_func = self._exit_action
        
    def _options(self, y_pos):
        
        y_pos += 50
        x_pos_text = WIDTH/2 - self.title_width/2 + 100
        x_pos_box = WIDTH/2 + self.title_width/2 - 150
        
        for option_text in self.OPTIONS_OPTIONS:
            
            if option_text == self.OPTIONS_OPTIONS[self._choice]:
                colour = self.SELECTED_COLOUR
            else:
                colour = WHITE
                            
            option = lib.render_text(option_text, 24, colour)
            option_width, option_height = option.get_width(), option.get_height()
            
            if option_text == self.BACK:
                y_pos += option_height + 3 # same as the last line of the loop
            
            self.game.screen.blit(option, (x_pos_text, y_pos))
            
            if option_text != self.BACK:
                y_pos_box = y_pos + 1
                option_box_w = option_height - 2
                option_box = pygame.Rect(x_pos_box, y_pos_box, option_box_w, option_box_w)
                # Line width here is 2
                if getattr(conf, self.OPTIONS_CONF[option_text]):
                    pygame.draw.line(self.game.screen, colour, (x_pos_box, y_pos_box), \
                                     (x_pos_box + option_box_w, y_pos_box + option_box_w), 2)
                    pygame.draw.line(self.game.screen, colour, (x_pos_box  + option_box_w, y_pos_box), \
                                     (x_pos_box, y_pos_box + option_box_w), 2)
                pygame.draw.rect(self.game.screen, colour, option_box, 2)

            y_pos += option_height + 3
            
    def _options_action(self):
        
        selection = self.OPTIONS_OPTIONS[self._choice]
        
        if selection == self.BACK:
            self._return_to_menu()
        else:
            # Flip bool value in conf
            attr = not getattr(conf, self.OPTIONS_CONF[selection])
            setattr(conf, self.OPTIONS_CONF[selection], attr)
            
            # Handle special case stuff
            if selection == self.FULLSCREEN:
                self.game.set_screen()
            elif selection == self.SOUND:
                # will stop and replay if enabled
                sound.play('title', -1)
                
    def _highscores(self, y_pos):
        highscore = lib.render_text(self.SCORES, 34)
        highscore_width = highscore.get_width()
        highscore_x = WIDTH/2 - highscore_width/2
        self.game.screen.blit(highscore, (highscore_x, y_pos))
        y_pos += highscore.get_height()
        #underline
        pygame.draw.line(self.game.screen, WHITE, (highscore_x, y_pos), \
                         (highscore_x + highscore_width, y_pos), 2)
        y_pos += 20 
        
        x_pos_text = WIDTH/2 - self.title_width/2 + 100
        x_pos_score = WIDTH/2 + self.title_width/2 - 125
        
        # Text size here is 22
        
        if len(conf.highscores):
            for name_text, score_text in conf.highscores:
                
                name = lib.render_text(name_text, 22)
                self.game.screen.blit(name, (x_pos_text, y_pos))
                
                score = lib.render_text(str(score_text), 22)
                self.game.screen.blit(score, (x_pos_score, y_pos))
                
                y_pos += name.get_height() + 3
        else:
            y_pos += 25
            self.__render_lines(self.NOSCORES, 22, 0, y_pos)
            

    def __render_lines(self, lines, size, spacing, y_pos):
        
        text = []
        longest = 0
        height = 0
        
        for line in lines.splitlines():
            if line:
                rendered_text = lib.render_text(line, size)
                width = rendered_text.get_width()
                text.append(rendered_text)
                if not height:
                    height = rendered_text.get_height()
                if width > longest:
                    longest = width
            else:
                text.append(False)
                
        x_pos = WIDTH/2 - longest/2
        
        for line in text:
            if line:
                self.game.screen.blit(line, (x_pos, y_pos))
            y_pos += height + spacing
            
    def _help(self, y_pos):
        self.__render_lines(self.HELP_TEXT, 18, 2, y_pos)
        
    def _help_action(self):
        self._display_func = self._help2
        self._action_func = self._return_to_menu
        
    def _help2(self, y_pos):
        self.__render_lines(self.HELP2_TEXT, 18, 2, y_pos)
        
    def _about(self, y_pos):
        
        y_pos += 100

        about_text = "%s %s\n" % (GAME, VERSION)
        about_text += u'Copyright \u00A92008 %s\n\n' % AUTHOR_NAME
        about_text += "Python Version: %d.%d.%d-%s\n" % sys.version_info[:4]
        about_text += "Pygame Version: %s\n" % pygame.version.ver
        
        about_text += "Psyco version: "
        
        if conf.psyco:
            try:
                import psyco
                about_text += "%d.%d.%d-%s" % psyco.version_info[:4]
            except ImportError:
                about_text += "disabled (unavailable)"
        else:
            about_text += "disabled (configuration)"
        
        self.__render_lines(about_text, 20, 5, y_pos)
            
    def _about_action(self):
        self._display_func = self._about2
        self._action_func = self._return_to_menu
        
    def _about2(self, y_pos):
        self.__render_lines(LICENSE, 14, 2, y_pos)
        
    def _exit(self, y_pos):
        choice, self._choice = self._choice, self._last_choice
        self._main(y_pos)
        self._choice = choice
        
        y_pos = HEIGHT/2 - 75
        
        box_white = pygame.Rect(WIDTH/2 - 125, y_pos, 250, 150)
        box_black = box_white.inflate(-5, -5)
        pygame.draw.rect(self.game.screen, WHITE, box_white)
        pygame.draw.rect(self.game.screen, BACKGROUND, box_black)
        
        y_pos += 10
        
        sure = lib.render_text(self.EXIT_SURE, 24)
        self.game.screen.blit(sure, (WIDTH/2 - sure.get_width()/2, y_pos))
        
        y_pos += sure.get_height() + 7
        
        if self.EXIT_OPTIONS[self._choice] == self.YES:
            yes_colour, no_colour = self.SELECTED_COLOUR, WHITE
        else:
            yes_colour, no_colour = WHITE, self.SELECTED_COLOUR
            
        yes = lib.render_text(self.YES, 38, yes_colour)
        no = lib.render_text(self.NO, 38, no_colour)
        
        self.game.screen.blit(yes, (WIDTH/2 - yes.get_width()/2, y_pos))
        y_pos += yes.get_height()
        self.game.screen.blit(no, (WIDTH/2 - no.get_width()/2, y_pos))
        
    
    def _exit_action(self):
        
        if self.EXIT_OPTIONS[self._choice] == self.YES:
            raise SystemExit
        else:
            self._return_to_menu()
        
