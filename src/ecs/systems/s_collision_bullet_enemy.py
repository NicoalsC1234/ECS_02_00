import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_collision_bullet_enemy(world:esper.World) -> int:
    enemys = world.get_components(CSurface, CTransform, CTagEnemy)
    bullets = world.get_components(CSurface, CTransform, CTagBullet)
    bullet = 0

    for enemy_entity, (c_s, c_t, _) in enemys:
        ene_rect = c_s.surf.get_rect(topleft = c_t.pos)
        for bullets_entity, (c_b_s, c_b_t, _) in bullets: 
            bullet_rect = c_b_s.surf.get_rect(topleft = c_b_t.pos)
            if ene_rect.colliderect(bullet_rect):
                bullet += 1
                world.delete_entity(enemy_entity)
                world.delete_entity(bullets_entity)
    return bullet