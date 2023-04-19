import random
import pygame
import esper
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_bullet import CTagBullet

def create_square(world:esper.World, size:pygame.Vector2,
                    pos:pygame.Vector2, vel:pygame.Vector2, col:pygame.Color) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity,
                CSurface(size, col))
    world.add_component(cuad_entity,
                CTransform(pos))
    world.add_component(cuad_entity, 
                CVelocity(vel))
    return cuad_entity

def create_enemy_square(world:esper.World, pos:pygame.Vector2, enemy_info:dict):
    size = pygame.Vector2(enemy_info["size"]["x"], 
                          enemy_info["size"]["y"])
    color = pygame.Color(enemy_info["color"]["r"],
                         enemy_info["color"]["g"],
                         enemy_info["color"]["b"])
    vel_max = enemy_info["velocity_max"]
    vel_min = enemy_info["velocity_min"]
    vel_range = random.randrange(vel_min, vel_max)
    velocity = pygame.Vector2(random.choice([-vel_range, vel_range]),
                              random.choice([-vel_range, vel_range]))
    enemy = create_square(world, size, pos, velocity, color)
    world.add_component(enemy, CTagEnemy())

def create_enemy_spawner(world:esper.World, level_data:dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity,
                        CEnemySpawner(level_data["enemy_spawn_events"]))
    
def create_player(player_data: dict, world:esper.World, level_data:dict) -> int:
    size = pygame.Vector2(player_data["size"]["x"], 
                          player_data["size"]["y"])
    color = pygame.Color(player_data["color"]["r"],
                         player_data["color"]["g"],
                         player_data["color"]["b"])
    pos = pygame.Vector2((level_data["position"]["x"] - (player_data["size"]["x"]/2)),
                        (level_data["position"]["y"] - (player_data["size"]["y"]/2)))
    vel = pygame.Vector2(0, 0)
    player = create_square(world, size, pos, vel, color)
    world.add_component(player, CTagPlayer())
    return player

def create_input_player(world: esper.World):
    input_left = world.create_entity()
    input_right = world.create_entity()
    input_up = world.create_entity()
    input_down = world.create_entity()
    input_space = world.create_entity()

    world.add_component(input_down, CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
    world.add_component(input_right, CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    world.add_component(input_up, CInputCommand("PLAYER_UP", pygame.K_UP))
    world.add_component(input_left, CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    world.add_component(input_space, CInputCommand("PLAYER_SPACE", pygame.K_SPACE))

def create_bullet_square(world: esper.World, bullet_data: dict, level_data:dict) -> int:
    size = pygame.Vector2(bullet_data["size"]["x"], bullet_data["size"]["y"])
    color = pygame.Color(bullet_data["color"]["r"], bullet_data["color"]["g"], bullet_data["color"]["b"])
    pos = pygame.Vector2(level_data["x"] - (size.x / 2), level_data["y"] - (size.y / 2))
    vel = pygame.Vector2(0, 0)
    bullet_entity = create_square(world, size, pos, vel, color)
    world.add_component(bullet_entity, CTagBullet())
    return bullet_entity