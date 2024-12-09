import tkinter as tk

from utils.vector2 import Vector2
from gameobjects.gameobject_physics_base import * 
from utils.audioplayer import SoundManager
from utils.soundthreadmanager import sound_thread
from utils.math_extensions import *

class Player(GameObject_Physics_Base):
    # Constants
    PLAYER_SIZE = 25

    def __init__(self, canvas: tk.Canvas, spawn_x: int, spawn_y: int):
        super().__init__(GameObjectType.PLAYER, canvas, Vector2(spawn_x, spawn_y), Vector2(Player.PLAYER_SIZE, Player.PLAYER_SIZE))
        self.energy = tk.DoubleVar(value=100)
        self.health = 3

    def draw(self) -> int:
        top_left = self.position - self.size
        bot_right = self.position + self.size
        return self.canvas.create_oval(top_left.x, top_left.y, bot_right.x, bot_right.y, fill='yellow', outline='white')
    
    '''
    Checks if a collision has occured between this object and another object
    Returns a boolean if this is True or False
    '''
    def check_collision(self, other: GameObject_Base) -> bool:
        match other.go_type: # Switch case based on other object's type
            # Star!
            case GameObjectType.STAR:
                dis_diff = other.position - self.position

                # Perpendicular! Always return false 
                if self.velocity.dot(dis_diff) <= 0:
                    return False

                # Else just check if the distance is less than the sum of the size of the two objects
                return dis_diff.length_squared() <= (self.size.x+ other.size.x) * (self.size.y + other.size.y)
            
            # Walls/Spaceship
            # Python has no fall-through switch case :(
            case GameObjectType.SPACESHIP:
                projected_dist = (self.position - other.position).dot(other.normal)
                return projected_dist < 0
                
            
            case _: # If nothing matches, no collision!
                return False
    
    '''
    After a collision has occured, this function is called to resolve the collision
    Basically, all the logic pertaining to what happens after a collision (gain score, velocity change, gain/lose hp, powerups, etc.) resides here!
    '''
    def collision_response(self, other: GameObject_Base):
        match other.go_type:
            case GameObjectType.STAR:
                sound_thread.play_sfx("./assets/sounds/sfx/item_star.wav")
                self.elastic_collision(other) # Collision response
                self.canvas.delete(other.canvas_object) # Remove star
                other.canvas_object = None
                self.modify_energy(ENERGY_GAIN_FROM_STAR) # Increase energy!

            case GameObjectType.SPACESHIP:
                sound_thread.play_sfx("./assets/sounds/sfx/item_spaceship.wav")
                direction = (self.position - other.normal).normalized()
                self.velocity = -self.velocity.absolute_vector() * direction * WALL_VELOCITY_DIMINISH_MULTIPLIER
                self.modify_energy(100 - self.energy.get()) # Set directly to 100

            case _:
                pass # do nothing

    def modify_energy(self, energy_to_add: float):
        self.energy.set(clamp(self.energy.get() + energy_to_add, 0, 100))

