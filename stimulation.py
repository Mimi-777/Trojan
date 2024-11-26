# Import necessary libraries
import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Set up the display window to fullscreen
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_surface().get_size()

# Load the background image
background_image = pygame.image.load('images/intersection.png')

# Load the red and green light images
red_light_image = pygame.image.load('images/redlight.png')
green_light_image = pygame.image.load('images/greenlight.png')

# Load the siren sound                          
siren_sound = pygame.mixer.Sound('sounds/siren2.wav')

# Set up the four traffic lights
traffic_lights = [
    {'position': (550, 250), 'state': 'red', 'line_position': 450},    # First traffic light initially red
    {'position': (770, 250), 'state': 'green', 'line_position': 450},  # Second traffic light initially green
    {'position': (550, 520), 'state': 'green', 'line_position': 650},  # Third traffic light initially green
    {'position': (770, 520), 'state': 'red', 'line_position': 650}     # Fourth traffic light initially red
]

# Define the distance threshold for obeying traffic lights
OBEDIENCE_DISTANCE_THRESHOLD = 40  # Adjust this value as needed

# Timer variables
last_light_change_time = pygame.time.get_ticks()
change_interval = 6000  # 6 seconds in milliseconds

# Car class
class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, image_file, speed, line_position):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()  # Load car image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.initial_speed = speed  # Store the initial speed
        self.line_position = line_position  # Line position for obeying traffic

    def update(self, all_sprites):
        pass  # This method will be overridden by subclasses

# TopCar class
class TopCar(Car):
    def update(self, all_sprites):
        # Move the car
        self.rect.y += self.speed

        # Check if the car reaches the bottom of the screen and reset its position
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0

        # Check if the car should obey traffic lights based on the second traffic light state
        second_light_state = traffic_lights[1]['state']
        if second_light_state == 'red':
            # Check if the car is above the line position
            if self.rect.centery == self.line_position:
                self.speed = 0  # Stop the car
            else:
                self.speed = self.initial_speed  # Set the car's speed back to its initial speed
        else:
            self.speed = self.initial_speed  # Set the car's speed back to its initial speed

# BottomCar class
class BottomCar(Car):
    def __init__(self, x, y, image_file, speed, line_position, direction):
        super().__init__(x, y, image_file, speed, line_position)
        self.direction = direction
        # Direction of the car

    def update(self, all_sprites):
        # Move the car
        self.rect.y -= self.speed * self.direction  # Adjust movement based on direction

        # Check if the car reaches the top/bottom of the screen and reset its position
        if self.direction == 1:
            if self.rect.bottom < 0:
                self.rect.top = WINDOW_HEIGHT
        else:
            if self.rect.top > WINDOW_HEIGHT:
                self.rect.bottom = 0

        # Check if the car should obey traffic lights based on the third traffic light state
        second_light_state = traffic_lights[1]['state']
        if second_light_state == 'red':
            # Check if the car is above the line position
            if self.rect.top == self.line_position:
                self.speed = 0  # Stop the car
            else:
                self.speed = self.initial_speed  # Set the car's speed back to its initial speed
        else:
            self.speed = self.initial_speed  # Set the car's speed back to its initial speed


# RightCar class
class RightCar(Car):
    def update(self, all_sprites):
        # Move the car
        self.rect.x -= self.speed  # Cars coming from the right move leftwards

        # Check if the car reaches the left edge of the screen and reset its position
        if self.rect.right < 0:
            self.rect.left = WINDOW_WIDTH

        # Check if the car should obey traffic lights based on the fourth traffic light state
        fourth_light_state = traffic_lights[3]['state']
        if fourth_light_state == 'red':
            # Check if the car is left of the line position
            if self.rect.left == self.line_position:
                self.speed = 0  # Stop the car
            else:
                self.speed = self.initial_speed  # Set the car's speed back to its initial speed
        else:
            self.speed = self.initial_speed  # Set the car's speed back to its initial speed

# LeftCar class
class LeftCar(Car):
    def update(self, all_sprites):
        # Move the car
        self.rect.x += self.speed  # Cars coming from the left move rightwards

        # Check if the car reaches the right edge of the screen and reset its position
        if self.rect.left > WINDOW_WIDTH:
            self.rect.right = 0

        # Check if the car should obey traffic lights based on the first traffic light state
        first_light_state = traffic_lights[0]['state']
        if first_light_state == 'red':
            # Check if the car is right of the line position
            if self.rect.left == self.line_position:
                self.speed = 0  # Stop the car
            else:
                self.speed = self.initial_speed  # Set the car's speed back to its initial speed
        else:
            self.speed = self.initial_speed  # Set the car's speed back to its initial speed

# Ambulance class
class Ambulance(pygame.sprite.Sprite):
    def __init__(self, x, y, image_file, speed, pass_limit):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()  # Load ambulance image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.pass_limit = pass_limit
        self.pass_count = 0
        self.direction = 'right'  # Initial direction
        self.passing = False
        self.playing_siren = False
        self.passes = 0
        self.last_move_time = time.time()
        self.move_interval = 25
        self.siren_duration = 5

        self.reset_position()

    def update(self, all_sprites):
        if time.time() - self.last_move_time >= self.move_interval:
            if self.passes >= 2:  # Check if ambulance has passed twice
                self.kill()  # Remove ambulance from all sprite groups
            else:
                self.reset_position()
            self.last_move_time = time.time()

        self.rect.x += self.speed

        # Check if ambulance is passing
        if self.rect.right >= WINDOW_WIDTH:
            self.passing = True
            if self.playing_siren:  # Stop siren sound if it's playing
                self.stop_siren()
        else:
            self.passing = False
            if not self.playing_siren:  # Play siren sound if it's not already playing
                self.play_siren()

    def reset_position(self):
        self.rect.left = 0
        self.rect.centery = WINDOW_HEIGHT // 3 + 100
        self.passes += 1  # Increment pass counter

    def play_siren(self):
        siren_sound.play(-1)  # Play the siren sound indefinitely (-1)
        self.playing_siren = True

    def stop_siren(self):
        siren_sound.stop()
        self.playing_siren = False

# Function to generate cars
def generate_cars(all_sprites):
    # Generate top cars
    top_car_data = [
        {'x': 700, 'y': 750, 'image_file': 'images/blueCarDown.png', 'speed': 5, 'line_position': 310},
    ]
    for car_data in top_car_data:
        top_car = TopCar(car_data['x'], car_data['y'], car_data['image_file'], car_data['speed'], car_data['line_position'])
        all_sprites.add(top_car)

    # Generate bottom cars
    bottom_car_data = [
        {'x': 650, 'y': 100, 'image_file': 'images/OrangeCarUp.png', 'speed': 4, 'line_position': 500, 'direction': 1},
    ]
    for car_data in bottom_car_data:
        bottom_car = BottomCar(car_data['x'], car_data['y'], car_data['image_file'], car_data['speed'], car_data['line_position'], car_data['direction'])
        all_sprites.add(bottom_car)

    # Generate right cars
    right_car_data = [

        {'x': WINDOW_WIDTH, 'y': 460, 'image_file': 'images/OrangeCarOpposite.png', 'speed': 4, 'line_position': 770},
    ]
    for car_data in right_car_data:
        right_car = RightCar(car_data['x'], car_data['y'], car_data['image_file'], car_data['speed'], car_data['line_position'])
        all_sprites.add(right_car)

    # Generate left cars
    left_car_data = [
        {'x': -50, 'y': 370, 'image_file': 'images/redBlueCar.png', 'speed': 4, 'line_position': 570}
    ]
    for car_data in left_car_data:
        left_car = LeftCar(car_data['x'], car_data['y'], car_data['image_file'], car_data['speed'], car_data['line_position'])
        all_sprites.add(left_car)

# Main game loop
all_sprites = pygame.sprite.Group()  # Create a sprite group
generate_cars(all_sprites)  # Generate cars

# Variables for ambulance appearance
ambulance_appeared = False
ambulance_interval = 6000  # 6 seconds in milliseconds
ambulance_last_appearance = pygame.time.get_ticks()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Check if it's time to change the traffic light states
    current_time = pygame.time.get_ticks()
    if current_time - last_light_change_time >= change_interval:
        # Change the state of the traffic lights
        for light in traffic_lights:
            if light['state'] == 'red':
                light['state'] = 'green'
            else:
                light['state'] = 'red'
        # Update the last light change time
        last_light_change_time = current_time

    # Check if it's time for the ambulance to appear
    if not ambulance_appeared and current_time - ambulance_last_appearance >= ambulance_interval:
        # Create ambulance sprite if it has not passed the limit
        ambulance = Ambulance(0, 700, 'images/ambulance.png', 8, 5)  # Starting from the left
        all_sprites.add(ambulance)
        ambulance_appeared = True
        ambulance_last_appearance = current_time

    # Update all sprites
    all_sprites.update(all_sprites)  # Pass all_sprites group to update method

    # Draw the background image
    window.blit(background_image, (0, 0))

    # Draw the traffic lights
    for light in traffic_lights:
        x, y = light['position']
        if light['state'] == 'red':
            window.blit(red_light_image, (x, y))
        else:
            window.blit(green_light_image, (x, y))

    # Draw all sprites
    all_sprites.draw(window)
    pygame.display.flip()
