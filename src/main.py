"""
    Module to implement the catch me if you can game
"""

# ======================================================================================================================
# Imports
# ======================================================================================================================

# Standard libraries
from typing import Tuple, List, Optional, Deque
from random import randrange, shuffle
from datetime import datetime
from time import sleep
from pathlib import Path
from _collections import deque

# External libraries and modules
import pygame
from external_modules.pyvidplayer.pyvidplayer import Video


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

        self._sun_radii: Optional[Deque[int]] = None
        self._number_of_sun_radii: int = 0

        self.initialize_sun_radii()

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

    def change_radius(self, first_game_phase: bool, second_game_phase: bool) -> bool:
        """
        Method to change Sun size

        The way the Sun size is changed depends on the game phase :

        - During the first phase change is allowed as long as radius is greater than the reducing value.
          In those cases the method will change the radius and return True
          Else the method will return False

        - During the second phase the size will be picked up from the Sun radii list (o random list of Sun size, between
          the reducing value and its initial size. In those cases the method will change the radius and return True.
          When all sizes have been picked up so the method will return False.
        """

        if first_game_phase and not second_game_phase:
            if self._radius > self.sun_reducing_value:
                self._radius -= self.sun_reducing_value
                self.update()
                return True

            return False

        if not first_game_phase and second_game_phase:
            try:
                self._radius = self._sun_radii.popleft()
                self.update()
                return True

            except IndexError:
                return False

    @property
    def sun_center_x(self) -> int:
        """ Property to return the sun horizontal position """

        return self._center_location[0]

    @property
    def sun_center_y(self) -> int:
        """ Property to return the sun vertical position """

        return self._center_location[1]

    def initialize_sun_radii(self) -> None:
        """ Method to initialize Sun radii from start value """

        self._sun_radii = list(
            range(
                self.sun_reducing_value,
                self.radius + 1 - self.sun_reducing_value,
                self.sun_reducing_value
            )
        )
        shuffle(self._sun_radii)
        self._sun_radii = deque([self.radius] + self._sun_radii)
        self._number_of_sun_radii = len(self._sun_radii)


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

        self._displayed_text: str = ""

        self._center_location: List[int] = [0, 0]

    def update(self) -> None:
        """ Private method to initialize message Surface object """

        if len(self._displayed_text.splitlines()) == 1:
            self.message_surface = self.text_font.render(self._displayed_text, True, self.font_color)
            self._center_location = [self.screen_width / 2, self.screen_height / 2]
            self.message_rect = self.message_surface.get_rect(center=self._center_location)

        else:
            lines: List[str] = self._displayed_text.splitlines()

            line_surface: pygame.Surface
            lines_surfaces: List[pygame.Surface] = []
            line: str

            for line in lines:
                line_surface = self.text_font.render(line, True, self.font_color)
                lines_surfaces.append(line_surface)

            # Compute message surface width and height
            message_surface_width: int = max([line_surface.get_width() for line_surface in lines_surfaces])
            message_surface_height: int = sum([line_surface.get_height() for line_surface in lines_surfaces])

            # The SRCALPHA parameter enables to draw a transparent Surface
            self.message_surface = pygame.Surface((message_surface_width, message_surface_height), pygame.SRCALPHA)

            for surface_index, current_line_surface in enumerate(lines_surfaces):
                message_location: Tuple[int, int] = (
                    (message_surface_width - current_line_surface.get_width()) / 2,
                    current_line_surface.get_height() * surface_index
                )
                self.message_surface.blit(current_line_surface, message_location)

            self._center_location = [self.screen_width / 2, self.screen_height / 2]
            self.message_rect = self.message_surface.get_rect(center=self._center_location)

    @property
    def displayed_text(self) -> str:
        """ Property that returns the message to display text """

        return self._displayed_text

    @displayed_text.setter
    def displayed_text(self, new_text: str) -> None:
        """ Property setter to define new text to be displayed """

        self._displayed_text = new_text
        self.update()


class GameSounds:
    """ Class to handle all the sounds and musics for the game """

    def __init__(self, sounds_location: Path) -> None:
        """ Class constructor """

        self.sounds_location: Path = sounds_location

        self.loaded_sounds: List[pygame.mixer.Sound] = []

        self.__init_sounds()

    def __init_sounds(self) -> None:
        """ Private method to initialize the game sounds """

        for sound in self.sounds_location.glob("*.ogg"):
            if sound.is_file():
                self.loaded_sounds.append(pygame.mixer.Sound(sound))

    def get_random_sound(self) -> pygame.mixer.Sound:
        """ Method to get a random loaded sound """

        return self.loaded_sounds[randrange(0, len(self.loaded_sounds))]


class GameMusics:
    """ Class to handle all the musics for the game """

    def __init__(self, musics_locations: Path) -> None:
        """ Class constructor """

        self._musics_locations: Path = musics_locations
        self._is_playing_music: bool = False

    def play_chosen_music(self, music_name: str) -> None:
        """ Method that plays the chosen music """

        if not self._is_playing_music:
            music_location_path: Path = self._musics_locations / f"{music_name}.ogg"
            if music_location_path.is_file():
                pygame.mixer.music.load(str(music_location_path))
                pygame.mixer.music.play(-1)
                self._is_playing_music = True

    def stop_current_playing_music(self) -> None:
        """ Static method to stop the music currently played """

        if self._is_playing_music:
            pygame.mixer.music.stop()
            self._is_playing_music = False


class GameVideos:
    """ Class to handle game videos """

    def __init__(
            self,
            videos_location: Path,
            screen_width: int,
            screen_height: int,
            game_window: pygame.surface.Surface
    ) -> None:
        """ Class constructor """

        self.videos_location: Path = videos_location
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.game_window: pygame.surface.Surface = game_window

        self._current_playing_video: Optional[Video] = None

    def load_video(self, video_name: str) -> None:
        """ Method that plays the chosen video """

        video_location_path: Path = self.videos_location / f"{video_name}.mp4"
        if video_location_path.is_file():
            self._current_playing_video = Video(str(video_location_path))
            self._current_playing_video.set_size((self.screen_width, self.screen_height))

    def play_loaded_video(self) -> None:
        """ Method that plays the loaded video """

        if self._current_playing_video:
            self._current_playing_video.draw(self.game_window, (0, 0))
            pygame.display.flip()

    def stop_current_playing_video(self) -> None:
        """ Method ot stop current playing video """

        if self._current_playing_video:
            self._current_playing_video.close()


class Game:
    """ Class to implement the game """

    def __init__(self, screen_width: int = 640, screen_height: int = 455) -> None:
        """ Class constructor """

        # Initialize pygame modules
        pygame.init()
        pygame.mixer.init()

        # Define game clock
        self.game_clock = pygame.time.Clock()

        # Define screen size
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        # Set main window
        self.window: pygame.surface.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Catch me if you can !")

        # Set data folders
        self.data_location = Path("../data")
        self.images_location: Path = self.data_location / "images"
        self.sounds_locations: Path = self.data_location / "sounds"
        self.musics_locations: Path = self.data_location / "musics"
        self.videos_locations: Path = self.data_location / "videos"

        # Background image
        self.background_image: Path = self.images_location / "ciel.jpg"
        self.background: pygame.surface.Surface = pygame.image.load(str(self.background_image)).convert()

        # Game sounds
        self.game_sounds = GameSounds(self.sounds_locations)

        # Game musics
        self.game_musics = GameMusics(self.musics_locations)

        # Game video
        self.game_videos = GameVideos(self.videos_locations, self.screen_width, self.screen_height, self.window)

        # Initialize Sun
        self.sun = Sun(self.screen_width, self.screen_height)

        # Sun configuration at game level
        self.sun_update_rate: int = 2  # in seconds
        self.last_sun_location_update: datetime = datetime.now()

        # Initialize message to user
        self.message_to_display = MessageToDisplay(self.screen_width, self.screen_height)
        self.message_to_display.displayed_text = "Gagné !"
        self.message_display_time: int = 1  # in seconds

        # Other game variables
        self.level_time_limit: int = 2  # in seconds
        self.FPS: int = 60  # number of frames per second

        # Booleans
        self.running: bool = True
        self.running_end_video: bool = False
        self.end_level: bool = False
        self.end_game: bool = False
        self.first_game_phase: bool = True
        self.second_game_phase: bool = False
        self.victory: bool = False

    def __initialize_some_games_booleans(self) -> None:
        """ Method to initialize some game booleans """

        self.end_level = False
        self.end_game = False
        self.victory = False

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
                self.running_end_video = False
                break

            elif event_type == pygame.MOUSEBUTTONDOWN and not self.end_game:
                mouse_center_location: Tuple[int, int] = pygame.mouse.get_pos()

                if self.__does_point_belong_to_circle(mouse_center_location, self.sun):

                    self.end_level = True
                    has_radius_changed: bool = self.sun.change_radius(self.first_game_phase, self.second_game_phase)

                    if not has_radius_changed:
                        self.victory = True

                        if self.second_game_phase:
                            self.second_game_phase = False

                        if self.first_game_phase:
                            self.first_game_phase = False
                            self.second_game_phase = True

    def render(self) -> None:
        """ Method to render elements """

        if self.victory:

            if not self.first_game_phase and self.second_game_phase:
                self.message_to_display.displayed_text = "\n".join(
                    [
                        "Tu as terminé le jeu, félicitations ^^",
                        "... enfin, peut-être :D",
                        "On recommence ?"
                    ]
                )
                self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
                pygame.display.flip()

                sleep(4 * self.message_display_time)

                self.game_musics.play_chosen_music("fond_sonore_detente")

                self.message_to_display.displayed_text = "Gagné !"

                self.sun.change_radius(self.first_game_phase, self.second_game_phase)
                self.last_sun_location_update = datetime.now()

                self.__initialize_some_games_booleans()

                return None

            elif not self.first_game_phase and not self.second_game_phase:
                pygame.mixer.Sound.play(self.game_sounds.get_random_sound())
                self.message_to_display.displayed_text = "\n".join(
                    [
                        "Félicitations !!!",
                        "Cette fois tu as VRAIMENT terminé le jeu ^^",
                        "Voici ta récompense (c'est ta faute, Kev ^^) !"
                    ]
                )
                self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
                pygame.display.flip()

                sleep(4 * self.message_display_time)

                self.running = False
                self.running_end_video = True

                return None

        if self.end_level:
            self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
            pygame.display.flip()

            if not self.end_game and self.second_game_phase:
                pygame.mixer.Sound.play(self.game_sounds.get_random_sound())

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
            self.game_clock.tick(self.FPS)

    def launch_end_video(self) -> None:
        """ Method to launch the end video if the player won the game"""

        if self.victory:
            # Stop background music
            self.game_musics.stop_current_playing_music()

            # Load video
            self.game_videos.load_video("tata")

            # Play video
            while self.running_end_video:
                self.process_input()
                self.game_videos.play_loaded_video()
                self.game_clock.tick(self.FPS)

    def quit_game(self) -> None:
        """ Method to correctly quit game """

        self.game_musics.stop_current_playing_music()
        self.game_videos.stop_current_playing_video()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
    game.launch_end_video()
    game.quit_game()
