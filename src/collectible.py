import events

class Collectible():
    
    def __init__(self, world, event_manager, entity_ID=None):
        self.world = world
        self.event_manager = event_manager
        self.entity_ID = entity_ID
    
    def handle_collision_event(self, entity_ID):
        pass

    def remove_item(self):
        ev_remove_ent = events.RemoveEntityFromTheGame(self.entity_ID)
        self.event_manager.post(ev_remove_ent)

class HealPotion(Collectible):
    
    def __init__(self, world, event_manager, recovery):
        Collectible.__init__(self, world, event_manager)
        self.recovery = recovery
    
    def handle_collision_event(self, collider_ID):
        if collider_ID == self.world.player:
            players_health = self.world.hp[self.world.players[collider_ID].hp_ID]
            #Increase HP
            new_health = players_health.points + self.recovery
            if new_health >= players_health.max:
                players_health.points = players_health.max
            else:
                players_health.points = new_health
            update_ui_ev = events.UpdatePlayersHpUI(collider_ID)
            self.event_manager.post(update_ui_ev)
            #Destroy collectible
            self.remove_item()
            
class SkillUp(Collectible):
    
    def __init__(self, world, event_manager):
        Collectible.__init__(self, world, event_manager)
    
    def handle_collision_event(self, collider_ID):
        if collider_ID == self.world.player:
            attack = self.world.attacks[collider_ID][0]
            attack.amount += 1
            #Destroy collectible
            self.remove_item()

class Portal(Collectible):
    
    def __init__(self, world, event_manager, x_pos, y_pos):
            Collectible.__init__(self, world, event_manager)
            self.port_position = [x_pos, y_pos]
    
    def handle_collision_event(self, collider_ID):
        if collider_ID == self.world.player:
            self.world.collider[collider_ID].center = self.port_position
            #Update image position of moved object
            ev = events.UpdateImagePosition(collider_ID, self.world.collider[collider_ID].center)
            self.event_manager.post(ev)
            #When moving object was a player
            if self.world.player == collider_ID:
                #Update orb direction correspondent aim direction and
                #player position
                orb_ID = self.world.players[collider_ID].orb_ID
                directionX = self.world.direction[collider_ID][0]
                directionY = self.world.direction[collider_ID][1]
                self.world.appearance[orb_ID].rect.center = (directionX*64 + self.world.collider[self.world.player].center[0] ,
                                                        directionY*64 + self.world.collider[self.world.player].center[1])
                #Update hp gui
                hp_ID = self.world.players[collider_ID].hp_ID
                self.world.appearance[hp_ID].rect.center = self.world.appearance[orb_ID].rect.center

