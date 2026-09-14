import os
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.toast import toast

# Support Android Native MediaPlayer
if platform == 'android':
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
else:
    MediaPlayer = None

# Dossier courant du projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(PROJECT_DIR, "icon.png")

KV = '''
ScreenManager:
    ListeScreen:
    PlayerScreen:

<ListeScreen>:
    name: 'liste'
    MDFloatLayout:
        md_bg_color: 0.94, 0.97, 0.94, 1

        MDCard:
            size_hint: 1, 0.12
            pos_hint: {"top": 1}
            radius: [0, 0, 25, 25]
            md_bg_color: 0.18, 0.49, 0.20, 1
            elevation: 4

            MDFloatLayout:
                MDLabel:
                    text: "usulus'salasa"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .5, "center_y": .5}

                MDIconButton:
                    icon: "share-variant"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_y": .5, "right": .98}

        ScrollView:
            size_hint: 0.9, 0.82
            pos_hint: {"center_x": .5, "top": 0.85}

            MDBoxLayout:
                id: container
                orientation: 'vertical'
                spacing: "15dp"
                size_hint_y: None
                height: self.minimum_height

<PlayerScreen>:
    name: 'player'
    MDFloatLayout:
        md_bg_color: 0.94, 0.97, 0.94, 1

        MDCard:
            size_hint: 1, 0.10
            pos_hint: {"top": 1}
            radius: [0, 0, 20, 20]
            md_bg_color: 0.18, 0.49, 0.20, 1

            MDFloatLayout:
                MDIconButton:
                    icon: "arrow-left"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_y": .5, "x": .02}
                    on_release: 
                        app.arreter_audio()
                        root.manager.current = 'liste'

                MDLabel:
                    text: "usulus'salasa"
                    font_style: "H6"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .5, "center_y": .5}

        MDCard:
            size_hint: None, None
            size: "220dp", "220dp"
            pos_hint: {"center_x": .5, "center_y": .63}
            radius: [110,]
            elevation: 6
            md_bg_color: 1, 1, 1, 1

            FitImage:
                id: track_image
                source: "icon.png"
                radius: [110,]

        MDCard:
            size_hint: 1, 0.42
            pos_hint: {"bottom": 1}
            radius: [35, 35, 0, 0]
            md_bg_color: 0.18, 0.49, 0.20, 1
            elevation: 8

            MDFloatLayout:
                MDLabel:
                    id: track_title
                    text: "Darasi na 1"
                    font_style: "H6"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .5, "top": .92}

                MDSlider:
                    id: progress_bar
                    min: 0
                    max: 100
                    value: 0
                    color: 1, 1, 1, 1
                    hint: False
                    pos_hint: {"center_x": .5, "center_y": .58}
                    size_hint_x: 0.85
                    on_touch_up: if self.collide_point(*args[1].pos): app.seek_audio(self.value)

                MDLabel:
                    id: time_current
                    text: "00:00"
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"x": .08, "center_y": .48}

                MDLabel:
                    id: time_total
                    text: "00:00"
                    font_style: "Caption"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"right": .92, "center_y": .48}

                MDIconButton:
                    icon: "skip-previous"
                    user_font_size: "36sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .3, "center_y": .25}
                    on_release: app.play_prev()

                MDIconButton:
                    id: play_btn
                    icon: "play-circle"
                    user_font_size: "54sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .5, "center_y": .25}
                    on_release: app.toggle_play()

                MDIconButton:
                    icon: "skip-next"
                    user_font_size: "36sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .7, "center_y": .25}
                    on_release: app.play_next()
'''

class ListeScreen(MDScreen):
    pass

class PlayerScreen(MDScreen):
    pass

class MainAudioApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = None
        self.audio_files = []
        self.current_index = 0
        self.is_playing = False
        self.update_event = None

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        self.charger_liste()

    def charger_liste(self):
        container = self.root.get_screen('liste').ids.container
        container.clear_widgets()

        if os.path.exists(PROJECT_DIR):
            self.audio_files = sorted([
                f for f in os.listdir(PROJECT_DIR) 
                if f.endswith(('.mp3', '.wav', '.ogg')) and os.path.isfile(os.path.join(PROJECT_DIR, f))
            ])

        if not self.audio_files:
            self.audio_files = ["1.mp3", "2.mp3", "3.mp3", "4.mp3", "5.mp3"]

        for idx, file_name in enumerate(self.audio_files):
            card = MDCard(
                size_hint=(1, None),
                height="65dp",
                radius=[20,],
                md_bg_color=(0.18, 0.49, 0.20, 1),
                elevation=3,
                on_release=lambda x, i=idx: self.ouvrir_lecteur(i)
            )
            
            box = MDFloatLayout()
            title = MDLabel(
                text=f"Darasi na {idx + 1}",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                pos_hint={"center_y": .5, "x": .08}
            )
            btn_play = MDIconButton(
                icon="play-circle-outline",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                pos_hint={"center_y": .5, "right": .95}
            )
            
            box.add_widget(title)
            box.add_widget(btn_play)
            card.add_widget(box)
            container.add_widget(card)

    def ouvrir_lecteur(self, index):
        self.current_index = index
        self.root.current = 'player'
        self.load_audio(self.audio_files[index])

    def arreter_audio(self):
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None
        
        if self.player:
            try:
                self.player.stop()
                self.player.reset()
                self.player.release()
            except Exception:
                pass
            self.player = None
        
        self.is_playing = False
        player_screen = self.root.get_screen('player')
        player_screen.ids.play_btn.icon = "play-circle"
        player_screen.ids.progress_bar.value = 0
        player_screen.ids.time_current.text = "00:00"

    def load_audio(self, file_name):
        self.arreter_audio()
        
        chemin = os.path.join(PROJECT_DIR, file_name)
        player_screen = self.root.get_screen('player')
        player_screen.ids.track_title.text = f"Darasi na {self.current_index + 1}"

        if os.path.exists(IMAGE_PATH):
            player_screen.ids.track_image.source = IMAGE_PATH
            player_screen.ids.track_image.reload()

        if platform == 'android' and MediaPlayer and os.path.exists(chemin):
            try:
                self.player = MediaPlayer()
                self.player.setDataSource(chemin)
                self.player.prepare()
                duration = self.player.getDuration() // 1000
                player_screen.ids.progress_bar.max = duration
                player_screen.ids.time_total.text = self.format_time(duration)
                self.toggle_play()
            except Exception as e:
                toast(f"Erreur audio: {e}")

    def toggle_play(self):
        player_screen = self.root.get_screen('player')
        if not self.player and platform == 'android':
            self.load_audio(self.audio_files[self.current_index])
            return

        if self.player:
            if self.is_playing:
                self.player.pause()
                self.is_playing = False
                player_screen.ids.play_btn.icon = "play-circle"
                if self.update_event:
                    self.update_event.cancel()
                    self.update_event = None
            else:
                self.player.start()
                self.is_playing = True
                player_screen.ids.play_btn.icon = "pause-circle"
                self.update_event = Clock.schedule_interval(self.update_progress, 0.5)

    def update_progress(self, dt):
        if self.player and self.is_playing:
            try:
                pos = self.player.getCurrentPosition() // 1000
                player_screen = self.root.get_screen('player')
                player_screen.ids.progress_bar.value = pos
                player_screen.ids.time_current.text = self.format_time(pos)
            except Exception:
                pass

    def seek_audio(self, value):
        if self.player:
            try:
                self.player.seekTo(int(value * 1000))
            except Exception:
                pass

    def play_next(self):
        if self.current_index < len(self.audio_files) - 1:
            self.ouvrir_lecteur(self.current_index + 1)
        else:
            toast("Dernier audio atteint")

    def play_prev(self):
        if self.current_index > 0:
            self.ouvrir_lecteur(self.current_index - 1)
        else:
            toast("Premier audio atteint")

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

if __name__ == "__main__":
    MainAudioApp().run()
