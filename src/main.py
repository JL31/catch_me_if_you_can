"""
    Module to implement the catch me if you can game
"""

# ======================================================================================================================
# Imports
# ======================================================================================================================

# Standard libraries
from typing import Tuple, List, Optional
from random import randrange
from datetime import datetime
from time import sleep

# External libraries
import pygame


# ======================================================================================================================
# Classes
# ======================================================================================================================

class Sun:
    """ Class to implement the Sun """

    def __init__(self, screen_width: int, screen_height: int, radius: int = 60) -> None:
        """ Class constructor """

        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        self._radius: int = radius
        self._center_location: List[int] = [0, 0]

        self.sun_color: Tuple[int, int, int] = (250, 250, 0)
        self.sun_reducing_value: int = 2

        self.sun_surface: Optional[pygame.surface.Surface] = None
        self.sun_circle: Optional[pygame.rect.Rect] = None
        self.sun_rect: Optional[pygame.rect.Rect] = None

        self.update()

    def update(self) -> None:
        """ Private method to draw the circle in the sun surface """

        self.sun_surface = pygame.surface.Surface((self._radius * 2, self._radius * 2), pygame.SRCALPHA)

        self.sun_circle = pygame.draw.circle(
            self.sun_surface,
            self.sun_color,
            (self.sun_surface.get_width() / 2, self.sun_surface.get_height() / 2),
            self._radius
        )

        self._center_location = [
            randrange(self._radius, self.screen_width - self._radius),
            randrange(self._radius, self.screen_height - self._radius)
        ]

        self.sun_rect = self.sun_surface.get_rect(center=self._center_location)

    @property
    def radius(self) -> int:
        """ Property to return the sun radius """

        return self._radius

    def change_radius(self) -> bool:
        """
        Method to reduce Sun size
        Change is allowed as long as radius is greater than the reducing value.
        In those cases the method will change the radius and return True
        Else the method will return False
        """

        if self._radius > self.sun_reducing_value:
            self._radius -= self.sun_reducing_value
            self.update()
            return True

        return False

    @property
    def sun_center_x(self) -> int:
        """ Property to return the sun horizontal position """

        return self._center_location[0]

    @property
    def sun_center_y(self) -> int:
        """ Property to return the sun vertical position """

        return self._center_location[1]


class MessageToDisplay:
    """ Class to implement a message that can be displayed on the screen """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """ Class constructor """

        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        # Font attributes
        self.font_policy: str = "Arial"
        self.font_size: int = 30
        self.font_color: Tuple[int, int, int] = (200, 0, 0)

        self.text_font: pygame.font.Font = pygame.font.SysFont(
            self.font_policy,
            self.font_size,
            bold=True
        )

        self.message_surface: Optional[pygame.surface.Surface] = None
        self.message_rect: Optional[pygame.rect.Rect] = None

        self._displayed_text: str = "Gagné !"

        self._center_location: List[int] = [0, 0]

        self.update()

    def update(self) -> None:
        """ Private method to initialize message Surface object """

        self.message_surface = self.text_font.render(
            self._displayed_text,
            True,
            self.font_color
        )

        self._center_location = [self.screen_width / 2, self.screen_height / 2]

        self.message_rect = self.message_surface.get_rect(center=self._center_location)

    @property
    def displayed_text(self) -> str:
        """ Property that returns the message to display text """

        return self._displayed_text

    @displayed_text.setter
    def displayed_text(self, new_text: str) -> None:
        """ Property setter to define new texte to be displayed """

        self._displayed_text = new_text
        self.update()


class Game:
    """ Class to implement the game """

    def __init__(self, screen_width: int = 640, screen_height: int = 455) -> None:
        """ Class constructor """

        # Initialize pygame modules
        pygame.init()
        
        # Define screen size
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        # Set main window
        self.window: pygame.surface.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Catch me if you can !")

        # Background image
        self.background_image: str = "../data/ciel.jpg"
        self.background: pygame.surface.Surface = pygame.image.load(self.background_image).convert()

        # Initialize Sun
        self.sun = Sun(self.screen_width, self.screen_height)

        # Sun configuration at game level
        self.sun_update_rate: int = 2  # in seconds
        self.last_sun_location_update: datetime = datetime.now()

        # Initialize message to user
        self.message_to_display = MessageToDisplay(self.screen_width, self.screen_height)
        self.message_display_time: int = 1  # in seconds

        # Other game variables
        self.level_time_limit: int = 2  # in seconds

        # Booleans
        self.running: bool = True
        self.end_level: bool = False
        self.end_game: bool = False
        self.victory: bool = False

    @staticmethod
    def __does_point_belong_to_circle(current_point: Tuple[int, int], sun_instance: Sun) -> bool:
        """ Static method to check if given point belongs to given circle """

        return ((current_point[0] - sun_instance.sun_center_x) ** 2 + (current_point[1] - sun_instance.sun_center_y) ** 2) <= sun_instance.radius ** 2

    def process_input(self) -> None:
        """ Method to process user input """

        for event in pygame.event.get():
            event_type: int = event.type

            if event_type == pygame.QUIT:
                self.running = False
                break

            elif event_type == pygame.MOUSEBUTTONDOWN and not self.end_game:
                mouse_center_location: Tuple[int, int] = pygame.mouse.get_pos()

                if self.__does_point_belong_to_circle(mouse_center_location, self.sun):

                    self.end_level = True
                    has_radius_changed: bool = self.sun.change_radius()

                    if not has_radius_changed:
                        self.victory = True

    def render(self) -> None:
        """ Metod to render elements """

        if self.victory:
            self.message_to_display.displayed_text = "Vous avez terminé le jeu, félicitations ^^"
            self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
            pygame.display.flip()
            return None

        if self.end_level:
            self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
            pygame.display.flip()

            sleep(self.message_display_time)

            self.last_sun_location_update = datetime.now()
            self.end_level = False

        if not self.end_game:
            self.window.blit(self.background, (0, 0))
            self.window.blit(self.sun.sun_surface, self.sun.sun_rect)
            pygame.display.flip()

    def change_sun_location(self) -> None:
        """ Method to change sun location with defined frequency """

        if (datetime.now() - self.last_sun_location_update).seconds == self.level_time_limit:
            self.message_to_display.displayed_text = "Perdu !"
            self.end_level = True
            self.end_game = True

        if not self.end_game and (self.end_level or (datetime.now() - self.last_sun_location_update).seconds == self.sun_update_rate):
            self.sun.update()

    def run(self) -> None:
        """ Method to run the game """

        while self.running:
            self.process_input()
            self.change_sun_location()
            self.render()

    def quit_game(self) -> None:
        """ Method to correctly quit game """

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
    game.quit_game()
    