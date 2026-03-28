from sprite import Sprite_surface, Collision_box
import universal_var
from megaman_object import Megaman_object
from timer import Timer
from megaman import Megaman
import camera
import pygame
import math
from bit_text import Bit_text


class Boss_room(Megaman_object):
   battle_has_end = False
   _celery_img = None

   @classmethod
   def _load_celery(cls):
      if cls._celery_img is None:
         try:
            raw = pygame.image.load('resources/enemies/concrete_man/celery_enemy.png')
            orig_w, orig_h = raw.get_size()
            target_h = 80
            target_w = max(1, int(orig_w * target_h / max(1, orig_h)))
            cls._celery_img = pygame.transform.scale(raw, (target_w, target_h))
         except Exception:
            cls._celery_img = False

   def __init__(self, boss, x, y, width, height):
      c = [Collision_box(universal_var.hitbox, x, y, width, height, (130, 190, 140))]
      super().__init__('Boss_room', x, y, sprites=None, coll_boxes=c,
                        width=width, height=height, display_layer=5)

      self.battle_has_init = False
      self.battle_has_end = False
      self.all_timers = Timer()
      self.all_timers.add_ID('time_till_start', 40)
      self.all_timers.add_ID('time_till_boss_spawn', 60)
      self.all_timers.add_ID('time_till_refill_bar', 130)
      self.all_timers.add_ID('time_till_end', 550)
      self.all_timers.add_ID('time_till_end_song', 160)
      self.boss = boss
      self._reward_elapsed = 0
      self._celery_delay = 0


   def check_player_collision(self):
      if len(Megaman.all_sprite_surfaces) != 0:
         trigger_box_collision = self.check_collision_lst(Megaman.all_sprite_surfaces, universal_var.hitbox, universal_var.hitbox)
         if trigger_box_collision.is_empty() != True:
            return True
      return False


   def spawn_boss(self):
      if self.all_timers.is_finished('time_till_start') != True:
         self.all_timers.countdown('time_till_start')
         self.music_lock = False

      else:
         self.boss.health_bar.is_active = True
         universal_var.songs.play_list(song_number=5)
         if self.all_timers.is_finished('time_till_boss_spawn') != True:
            self.all_timers.countdown('time_till_boss_spawn')
         elif self.battle_has_init != True and self.boss.is_active != True:
            self.boss.spawn()

         if self.boss.is_active:
            if self.all_timers.is_finished('time_till_refill_bar') != True:
               self.all_timers.countdown('time_till_refill_bar')
            elif self.boss.health_bar.is_full() != True:
               self.boss.health_bar.refill(11)


   def _draw_sparkles(self, surf, cx, cy):
      """Rotating sparkle rings and pulsing star bursts around the celery."""
      elapsed = self._reward_elapsed
      colors = [(255, 220, 50), (255, 255, 255), (80, 220, 255)]

      # Outer ring: 8 sparks rotating clockwise
      for i in range(8):
         angle = math.radians((elapsed * 3 + i * 45) % 360)
         sx = cx + int(68 * math.cos(angle))
         sy = cy + int(68 * math.sin(angle))
         color = colors[(elapsed // 5 + i) % 3]
         pygame.draw.rect(surf, color, (sx - 2, sy - 2, 5, 5))

      # Inner ring: 6 sparks rotating counter-clockwise
      for i in range(6):
         angle = math.radians((-elapsed * 4 + i * 60) % 360)
         sx = cx + int(50 * math.cos(angle))
         sy = cy + int(50 * math.sin(angle))
         color = colors[(elapsed // 5 + i + 1) % 3]
         pygame.draw.rect(surf, color, (sx - 1, sy - 1, 3, 3))

      # 4 pulsing star points that expand and contract
      pulse = abs(math.sin(elapsed * 0.12)) * 22 + 32
      for i, angle_deg in enumerate([0, 90, 180, 270]):
         angle = math.radians(angle_deg + elapsed * 1.5)
         bx = cx + int(pulse * math.cos(angle))
         by = cy + int(pulse * math.sin(angle))
         color = colors[(elapsed // 4 + i) % 3]
         pygame.draw.rect(surf, color, (bx - 2, by - 2, 5, 5))
         pygame.draw.rect(surf, (255, 255, 255), (bx - 1, by - 1, 2, 2))

      # Flash bursts every 20 frames
      if elapsed % 20 < 8:
         burst_r = 42 + (elapsed % 20) * 2
         for i in range(8):
            angle = math.radians(i * 45 + elapsed * 6)
            bx = cx + int(burst_r * math.cos(angle))
            by = cy + int(burst_r * math.sin(angle))
            pygame.draw.rect(surf, (255, 255, 200), (bx - 1, by - 1, 3, 3))


   def _draw_speech_bubble(self, surf, cx, img_bottom_y):
      """8-bit Megaman-style speech bubble with typewriter text reveal."""
      bub_w, bub_h = 238, 54
      bub_x = cx - bub_w // 2
      bub_y = img_bottom_y + 18

      # Pixelated tail pointing upward toward the celery image
      for j in range(8):
         pw = max(2, 14 - j * 2)
         pygame.draw.rect(surf, (255, 255, 255), (cx - pw // 2 - 1, bub_y - 8 + j, pw + 2, 1))
      for j in range(7):
         pw = max(1, 12 - j * 2)
         pygame.draw.rect(surf, (0, 0, 0), (cx - pw // 2, bub_y - 7 + j, pw, 1))

      # Black fill
      pygame.draw.rect(surf, (0, 0, 0), (bub_x, bub_y, bub_w, bub_h))
      # White outer border (3px thick — classic NES Megaman look)
      pygame.draw.rect(surf, (255, 255, 255), (bub_x, bub_y, bub_w, bub_h), 3)
      # Black inner border (1px — creates the double-border 8-bit effect)
      pygame.draw.rect(surf, (0, 0, 0), (bub_x + 3, bub_y + 3, bub_w - 6, bub_h - 6), 1)

      # Typewriter text reveal: 1 char every 6 frames
      full_text = "celery get!!!"
      chars_to_show = min(len(full_text), self._reward_elapsed // 6)
      if chars_to_show > 0:
         Bit_text.display_text(surf, (bub_x + 14, bub_y + 17), full_text[:chars_to_show], 2, 2)


   def display(self, surf):
      """Called by World_camera.follow() during the draw phase — renders on top of all world sprites."""
      if not self.battle_has_end:
         return

      if self._celery_delay < 240:
         if universal_var.game_pause != True:
            self._celery_delay += 1
         return

      Boss_room._load_celery()

      # Dark semi-transparent overlay so the reward pops
      overlay = pygame.Surface((600, 600))
      overlay.fill((0, 0, 0))
      overlay.set_alpha(145)
      surf.blit(overlay, (0, 0))

      cx, cy = 300, 200  # screen-space center for the celery

      self._draw_sparkles(surf, cx, cy)

      # Celery image with a gentle bob
      celery = Boss_room._celery_img
      if celery:
         bob_y = int(math.sin(self._reward_elapsed * 0.08) * 6)
         img_w = celery.get_width()
         img_h = celery.get_height()
         img_x = cx - img_w // 2
         img_y = cy - img_h // 2 + bob_y
         surf.blit(celery, (img_x, img_y))
         self._draw_speech_bubble(surf, cx, img_y + img_h)
      else:
         # No image — still show the speech bubble centered
         self._draw_speech_bubble(surf, cx, cy + 40)

      if universal_var.game_pause != True:
         self._reward_elapsed += 1


   def end_level(self):
      if self.all_timers.is_finished('time_till_end') != True:
         self.all_timers.countdown('time_till_end')
      else:
         Boss_room.battle_has_end = True

      if self.all_timers.is_finished('time_till_end_song') != True:
         self.all_timers.countdown('time_till_end_song')
      if self.all_timers.get_ID('time_till_end_song')['curr_state'] == 1:
         universal_var.songs.play_list(song_number=6)


   def update(self):
      if len(Megaman.all_sprite_surfaces) != 0:
         m = Megaman.all_sprite_surfaces[0]

         # Unconditionally lock movement during death cutscene and celery reward
         if self.boss._death_cutscene_active or self.battle_has_end:
            m.disable_keys()

         if self.check_player_collision():
            if self.battle_has_init != True and camera.camera_transitioning() != True:
               m.disable_keys()
               self.spawn_boss()
            elif self.battle_has_init and self.battle_has_end != True:
               if not self.boss._death_cutscene_active:
                  m.enable_keys()

            if self.battle_has_end:
               self.end_level()

            if (self.battle_has_init and self.battle_has_end != True) and self.boss.is_alive() != True and self.boss.is_active != True:
               self.battle_has_end = True
               universal_var.songs.stop()

         if universal_var.game_reset:
            self.battle_has_init = False
            self.battle_has_end = False
            self._reward_elapsed = 0
            self._celery_delay = 0
            self.boss.health_bar.points = 0
            m.enable_keys()
            for ID in self.all_timers:
               self.all_timers.replenish_timer(ID)
      Sprite_surface.update(self)
