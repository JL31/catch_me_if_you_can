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
from pathlib import Path

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

        # if self._radius > self.sun_reducing_value:
        #     self._radius -= self.sun_reducing_value
        #     self.update()
        #     return True

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

        self.musics_locations: Path = musics_locations

    def play_chosen_music(self, music_name: str) -> None:
        """ Method that plays the chosen music """

        music_location_path: Path = self.musics_locations / f"{music_name}.ogg"
        if music_location_path.is_file():
            pygame.mixer.music.load(str(music_location_path))
            pygame.mixer.music.play(-1)

    @staticmethod
    def stop_current_playing_music() -> None:
        """ Static method to stop the music currently played """

        pygame.mixer.music.stop()


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

        self._current_playing_video.close()


# TODO : ajouter taille random pour la soleil

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
        self.game_musics.play_chosen_music("fond_sonore_detente")

        # Game video
        self.game_videos = GameVideos(self.videos_locations, self.screen_width, self.screen_height, self.window)

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
        self.FPS: int = 60  # number of frames per second

        # Booleans
        self.running: bool = True
        self.running_end_video: bool = False
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
                self.running_end_video = False
                break

            elif event_type == pygame.MOUSEBUTTONDOWN and not self.end_game:
                mouse_center_location: Tuple[int, int] = pygame.mouse.get_pos()

                if self.__does_point_belong_to_circle(mouse_center_location, self.sun):

                    self.end_level = True
                    has_radius_changed: bool = self.sun.change_radius()

                    if not has_radius_changed:
                        self.victory = True

    def render(self) -> None:
        """ Method to render elements """

        if self.victory:
            pygame.mixer.Sound.play(self.game_sounds.get_random_sound())
            # self.message_to_display.displayed_text = "Vous avez terminé le jeu, félicitations ^^"
            self.message_to_display.displayed_text = "C'est ta faute, Kev ^^"
            self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
            pygame.display.flip()

            sleep(4 * self.message_display_time)

            self.running = False
            self.running_end_video = True

            return None

        if self.end_level:
            self.window.blit(self.message_to_display.message_surface, self.message_to_display.message_rect)
            pygame.display.flip()

            if not self.end_game:
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

        self.game_videos.stop_current_playing_video()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
    game.launch_end_video()
    game.quit_game()
