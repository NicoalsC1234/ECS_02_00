import json
import math
import pygame
import esper
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_input_player import system_input_player

from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce

from src.create.prefab_creator import create_bullet_square, create_enemy_spawner, create_input_player, create_player
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.s_bounding_box import system_bounding_box

class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]), 
            pygame.SCALED)
        
        self.bullet_max = self.bullets_cfg["maximun_bullets"]

        self.bullets_left = self.bullet_max

        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])
        
        self.ecs_world = esper.World()

    def _load_config_files(self):
        with open("assets/cfg/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
        with open("assets/cfg/enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("assets/cfg/level_01.json") as level_01_file:
            self.level_01_cfg = json.load(level_01_file)
        with open("assets/cfg/player.json") as player_file:
            self.player_cfg = json.load(player_file)
        with open("assets/cfg/bullet.json") as bullets_file:
            self.bullets_cfg = json.load(bullets_file)

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    def _create(self):
        self._player_entity = create_player(self.player_cfg, self.ecs_world, self.level_01_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_p = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._cursor_entity = self.ecs_world.create_entity()
        self.ecs_world.add_component(self._cursor_entity, CTransform(pos=(0, 0)))
        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0
    
    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)
        bullet_bb = system_bounding_box(self.ecs_world, self.screen)
        if (bullet_bb > 0): self.bullets_left += bullet_bb
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_01_cfg)
        bul = system_collision_bullet_enemy(self.ecs_world)
        if (bul > 0): self.bullets_left += bul
        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input:CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_C":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_SPACE":
            self._bullets()
    
    def _bullets(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.bullets_left > 0:
            self.is_shooting = True
            self._bullet_entity = create_bullet_square(self.ecs_world, self.bullets_cfg, self.level_01_cfg["player_spawn"]["position"])
            self._bullet_c_v = self.ecs_world.component_for_entity(self._bullet_entity, CVelocity)
            bullet_c_p = self.ecs_world.component_for_entity(self._bullet_entity, CTransform)
            bullet_c_p.pos.x = self._player_c_p.pos.x + self.player_cfg["size"]["x"] /2
            bullet_c_p.pos.y = self._player_c_p.pos.y + self.player_cfg["size"]["y"] /2
            player_pos = self._player_c_p.pos
            direction = math.atan2(mouse_pos[1] - player_pos[1], mouse_pos[0] - player_pos[0])
            bullet_c_v = self.ecs_world.component_for_entity(self._bullet_entity, CVelocity)
            bullet_c_v.vel.x = self.bullets_cfg["velocity"] * math.cos(direction)
            bullet_c_v.vel.y = self.bullets_cfg["velocity"] * math.sin(direction)
            self.bullets_left -= 1
       
                

    
