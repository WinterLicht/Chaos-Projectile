"""
.. module:: combatsystem
    :platform: Unix, Windows
    :synopsis: Handles collision between characters and projectiles, handles attacks etc.
"""

import events


class CombatSystem():
    """Handles collision between characters and projectiles, handles attacks etc.
    
    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
    """

    def __init__(self, event_manager, world):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

        self.world = world

    def notify(self, event):
        """Notify, when event occurs. 
        
        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.update()
        if isinstance(event, events.EntityAttackRequest):
            if self.world.active_entity(event.entity_ID):
                self.execute_attack(event.entity_ID, event.attack_Nr, event.spawn_attack_pos, event.attack_dir)
        if isinstance(event, events.RemoveEntityFromTheGame):
            self.world.to_remove.append(event.entity_ID)

    def update(self):
        """Update all particle emitters, remove dead objects and execute attacks."""
        for attacks in self.world.attacks.itervalues():
            for attack in attacks:
                dead_particles = attack.update()
                for projectile in dead_particles:
                    ev_die = events.EntityDies(projectile.entity_ID)
                    self.event_manager.post(ev_die)
        #Check for collision
        self.check_projectile_collision()
        self.remove_dead_entities()

    def check_projectile_collision(self):
        """Checks for collision between projectiles and other objects."""
        player_ID = self.world.player
        for attacks_ID in self.world.attacks:
            for attack in self.world.attacks[attacks_ID]:
                for projectile in attack.particles:
                    #First update projectiles grafic position
                    self.world.appearance[projectile.entity_ID].rect.center = projectile.position
                    projectile_rect = self.world.appearance[projectile.entity_ID].rect
                    for collider_ID in self.world.collider:
                        #Check overlapping
                        if self.world.collider[collider_ID].colliderect(projectile_rect):
                            #Enemy hits player
                            if collider_ID == player_ID and attacks_ID in self.world.ai:
                                if self.world.hp[self.world.players[player_ID].hp_ID].points > 0:
                                    players_health = self.world.hp[self.world.players[player_ID].hp_ID]
                                    #Decrease HP 
                                    players_health.points -= attack.damage
                                    #Update players hp gui
                                    hp_image_index = players_health.points // (players_health.max // len(players_health.hp_sprites))
                                    players_health.current_image = players_health.hp_sprites[hp_image_index]
                                    self.world.appearance[self.world.players[player_ID].hp_ID] = players_health.current_image
                                else:
                                    #No more Hp left
                                    #print("player is dead")
                                    pass
                                projectile.life = -1
                                ev_die = events.EntityDies(projectile.entity_ID)
                                self.event_manager.post(ev_die)
                            #Player hits enemy
                            elif collider_ID in self.world.ai and attacks_ID == player_ID:
                                if self.world.hp[collider_ID].points > 0:
                                    enemys_health = self.world.hp[collider_ID]
                                    #Decrease HP 
                                    enemys_health.points -= attack.damage
                                else:
                                    ev_die = events.EntityDies(collider_ID)
                                    self.event_manager.post(ev_die)
                                projectile.life = -1
                                ev_die = events.EntityDies(projectile.entity_ID)
                                self.event_manager.post(ev_die)
                    #Collision between walls
                    hit_items = self.world.tree.hit(projectile_rect)
                    if hit_items:
                        projectile.life = -1
                        ev_die = events.EntityDies(projectile.entity_ID)
                        self.event_manager.post(ev_die)

    def remove_dead_entities(self):
        for entity_ID in self.world.to_remove:
            self.world.destroy_entity(entity_ID)
        self.world.to_remove = list()

    def execute_attack(self, entity_ID, attack_Nr, spawn_attack_pos=None, attack_dir=None):
        """Entity executes one of its possible attacks if cooldown is ready.

        :param entity_ID: entity
        :type entity_ID: int
        :param attack_Nr: number of the attacks that is executed
        :type attack_Nr: int
        """
        if spawn_attack_pos:
            position = spawn_attack_pos
        else:
            position = (self.world.collider[entity_ID].center[0],
                        self.world.collider[entity_ID].center[1])
            if entity_ID in self.world.players:
                orb_ID = self.world.players[entity_ID].orb_ID
                position = self.world.appearance[orb_ID].rect.center
        if attack_dir:
            direction = attack_dir
        else:
            direction = self.world.direction[entity_ID]
        velocity = [direction[0] * 3,
                    direction[1] * 3]
        spawned = self.world.attacks[entity_ID][attack_Nr].spawn_particles(velocity, position)
        if spawned:
            #Post attack event
            ev = events.EntityAttacks(entity_ID, attack_Nr)
            self.event_manager.post(ev)
            #Show effect
            effect_ID = self.world.attacks[entity_ID][attack_Nr].effect_ID
            if effect_ID:
                if entity_ID == self.world.player:
                    #Calculate position and angle of effect
                    player = self.world.players[entity_ID]
                    #Get the orb position of the player
                    eff_position = self.world.appearance[player.orb_ID].rect.center
                    rot_angle = self.world.appearance[player.orb_ID].angle
                else:
                    eff_position = position
                    rot_angle = 0
                #Update position and rotation of the attack effect
                self.world.appearance[effect_ID].rect.center = eff_position
                self.world.appearance[effect_ID].angle = rot_angle
                self.world.appearance[effect_ID].play_animation = True

#    def handle_collision(self, collider_ID, collidee_ID):
#        pass