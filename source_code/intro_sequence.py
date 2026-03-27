import pygame
import math
from megaman_object import Megaman_object
from sprite import Collision_box
from timer import Timer
from bit_text import Bit_text
import universal_var

class Celery_rocket(Megaman_object):
   _img = None

   @classmethod
   def _load_img(cls):
      if cls._img is None:
         try:
            raw = pygame.image.load('resources/enemies/concrete_man/celery_enemy.png')
            orig_w, orig_h = raw.get_size()
            target_h = 34
            target_w = max(1, int(orig_w * target_h / max(1, orig_h)))
            scaled = pygame.transform.scale(raw, (target_w, target_h))
            cls._img = pygame.transform.flip(scaled, True, False)
         except Exception:
            cls._img = False

   def __init__(self, x, y, vel, wobble_offset=0.0):
      Celery_rocket._load_img()
      img = Celery_rocket._img
      width = img.get_width() if img else 34
      height = 34
      super().__init__('celery_rocket', x=x, y=y, width=width, height=height, display_layer=3)
      self._vel = vel
      self._base_y = float(y)
      self._wobble_offset = wobble_offset
      self._elapsed = 0

   def display(self, surf):
      img = Celery_rocket._img
      if img:
         surf.blit(img, (int(self.x), int(self.y)))

   def update(self):
      self.x -= self._vel
      self.y = self._base_y + math.sin(self._elapsed * 0.14 + self._wobble_offset) * 9
      self._elapsed += 1
      if self.x + self.width < 0:
         self.is_active = False
      Megaman_object.update(self)


#---------------------------------------------------------------------


class Stage_rectangle(Megaman_object):
   def __init__(self, y, stage_name=''):
      super().__init__('stage_rectangle', x=0, y=y, width=600, height=0, display_layer=2)
      self.stage_name = Bit_text(stage_name, 150, self.y + self.height//2 + 8*12-4, 3, 3, pattern_interval=10)
      self.all_timers = Timer()
      self.all_timers.add_ID('time_till_start_sequence', 40)
      self.all_timers.add_ID('show_stage_name', 60)
      self.y_offset = self.y - self.height//2

      self._rockets_spawned = False
      self._rocket_delay = 0

      stage_platform_collbox = [Collision_box(universal_var.hitbox, 0, 0, 600, 100)]
      stage_platform = Megaman_object('platform', 0, 340, sprites=None, coll_boxes=stage_platform_collbox,
                     width=600, height=100, display_layer=5)
      Megaman_object.add_to_class_lst(stage_platform, Megaman_object.platforms, stage_platform.ID)

   def display(self, surf):
      if self.all_timers.is_finished('time_till_start_sequence'):
         pygame.draw.rect(surf, (0, 33, 180), (self.x, self.y_offset, self.width, self.height))
      pygame.draw.rect(surf, (0, 43, 190), (self.x, self.y_offset - 8, self.width, 4))
      pygame.draw.rect(surf, (43, 199, 255), (self.x, self.y_offset - 8*2, self.width, 4))
      pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y_offset - 8*3, self.width, 4))
      pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y_offset - 8*7, self.width, 4))

      pygame.draw.rect(surf, (0, 43, 190), (self.x, self.y + self.height//2 + 4, self.width, 4))
      pygame.draw.rect(surf, (43, 199, 255), (self.x, self.y + self.height//2 + 8*2-4, self.width, 4))
      pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y + self.height//2 + 8*3-4, self.width, 4))
      pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y + self.height//2 + 8*7-4, self.width, 4))

      if self.height >= 130:
         if self.all_timers.is_finished('show_stage_name') != True:
            self.all_timers.countdown('show_stage_name')
         else:
            self.stage_name.display(surf, pattern='letter_sequence', pattern_interval=15)

   def update(self):
      if self.all_timers.is_finished('time_till_start_sequence') != True:
         self.all_timers.countdown('time_till_start_sequence')
      elif self.height < 130:
         self.height += 3
         self.y_offset = self.y - self.height//2
      else:
         self.height = 130

      # Spawn rockets shortly after the stage name text is fully revealed
      if (not self._rockets_spawned and
            self.all_timers.is_finished('show_stage_name') and
            self.stage_name.show_letters_up_to >= len(self.stage_name.string)):
         self._rocket_delay += 1
         if self._rocket_delay >= 25:
            self._rockets_spawned = True
            configs = [
               (630,  260, 11, 0.0), (710,  360, 13, 1.1), (790,  300, 9,  2.2),
               (870,  420, 12, 0.6), (950,  270, 10, 1.7), (1030, 390, 14, 2.8),
               (1110, 320, 11, 3.4), (1190, 450, 9,  0.9), (1270, 285, 13, 1.9),
               (1350, 410, 10, 2.4), (1430, 340, 12, 0.4), (1510, 375, 11, 1.5),
            ]
            for x, y, vel, wobble in configs:
               Celery_rocket(x, y, vel, wobble)

      Megaman_object.update(self)


#---------------------------------------------------------------------


class Star(Megaman_object):
   init = False
   star_types = {
                  1: [[0], []],
                  2: [[0,1], []],
                  3: [[0,1], [0,1]]
                }

   def __init__(self, x, y, vel, size=1, colour=(255,255,255)):
      width = 3
      height = 3
      super().__init__('star', x=x, y=y, width=width, height=height, display_layer=1)
      self.vel = vel
      self.size = size
      self.colour = colour

   @staticmethod
   def init_star_background():
      Star.init = True
      vel_1 = 2
      vel_2 = 3
      vel_3 = 5
      vel_4 = 7
      all_stars = [
                     [(300,20), vel_2, 3], [(450,20), vel_2, 3], [(20,70), vel_3, 1], [(300,90), vel_3, 1], [(500,70), vel_3, 2],
                     [(250,90), vel_2, 1], [(550,90), vel_2, 1], [(350,100), vel_1, 2],
                     [(40,130), vel_4, 1], [(240,130), vel_4, 1], [(50,122), vel_3, 2],
                     [(200,140), vel_3, 1], [(250,140), vel_3, 2], [(400,160), vel_2, 1], [(400,160), vel_3, 2],

                     [(400,440), vel_4, 3], [(300,460), vel_3, 3],
                     [(140,490), vel_2, 1], [(380,490), vel_2, 1], [(220,500), vel_4, 1],
                     [(380,520), vel_3, 1], [(380,530), vel_2, 2], [(580,530), vel_3, 2],
                     [(180,550), vel_2, 2], [(100,550), vel_2, 1], [(500,560), vel_3, 1]
                  ]

      for lst in all_stars:
         x, y, vel, size = lst[0][0], lst[0][1], lst[1], lst[2]
         Star(x, y, vel, size)

   def display(self, surf):
      y = self.y
      for pixel_array in Star.star_types[self.size]: # going through every pixel_array in characters and making a rectangle at each number in the pixel_array
         if len(pixel_array) != 0:
            for i in range(len(pixel_array)):
               x = self.x + (pixel_array[i] * self.width)
               pygame.draw.rect(surf, self.colour, (x, y, self.width, self.height))
         y += self.height

   def update(self):
      if self.is_on_screen():
         self.is_active = True
      else:
         if self.x < 0:
            self.x = universal_var.screen_width
      self.move(-self.vel)