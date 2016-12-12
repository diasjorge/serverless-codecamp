from chalice import Chalice
import random

app = Chalice(app_name='serverless-codecamp')
app.debug = True

@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/info', cors=True)
def info():
    return {
        'name': 'python-destroyer',
        'owner': 'python-haters'
    }


@app.route('/command', methods=['POST'], cors=True)
def command():
    map = app.current_request.json_body

    print(map)

    tank = Tank(map)
    next_move = tank.next_move()

    print("NEXT MOVE")
    print(next_move)

    return {
        'command': next_move
    }


class Tank(object):

    MOVEMENTS = {
        'top':    {'x': 0, 'y': -1},
        'left':   {'x': -1, 'y': 0},
        'bottom': {'x': 0, 'y': 1},
        'right':  {'x': 1, 'y': 0}
    }

    def __init__(self, map):
        self._map = map

    @property
    def weapon_range(self):
        return self._map['weaponRange']

    @property
    def you(self):
        return self._map['you']

    @property
    def enemies(self):
        return self._map['enemies']

    @property
    def closest_enemy(self):
        return self.enemies[0]

    @property
    def is_any_enemies(self):
        return any([self.is_enemy_visible(enemy) for enemy in self.enemies])

    @property
    def can_fire_on_any_enemy(self):
        return any([self.can_fire_on_enemy(enemy) for enemy in self.enemies])

    def can_fire_on_enemy(self, enemy):
        return enemy['strength'] > 0 and self.is_enemy_on_range(enemy)

    def is_enemy_on_range(self, enemy):
        if not self.is_enemy_visible(enemy):
            return False

        if self.you['direction'] == 'top':
            return (
                enemy['x'] == self.you['x'] and
                enemy['y'] >= self.you['y'] - self.weapon_range
            )
        if self.you['direction'] == 'bottom':
            return (
                enemy['x'] == self.you['x'] and
                enemy['y'] <= self.you['y'] + self.weapon_range
            )
        if self.you['direction'] == 'left':
            return (
                enemy['x'] >= self.you['x'] - self.weapon_range and
                enemy['y'] == self.you['y']
            )
        if self.you['direction'] == 'right':
            return (
                enemy['x'] <= self.you['x'] + self.weapon_range and
                enemy['y'] == self.you['y']
            )

    def is_enemy_visible(self, enemy):
        if enemy.get('x', None):
            return True
        return False


    @property
    def next_position(self):
        direction = self.you['direction']
        next_movement = self.MOVEMENTS[direction]
        return {
            'x': self.you['x'] + next_movement['x'],
            'y': self.you['y'] + next_movement['y']
        }

    def soon_outside_of_map(self, next_position):
        boundary = random.randint(1, 3)
        now_x = self.you['x']
        now_y = self.you['y']
        next_x = next_position['x']
        next_y = next_position['y']
        min_x = boundary
        max_x = self._map['mapWidth'] - boundary
        min_y = boundary
        max_y = self._map['mapHeight'] - boundary
        return (
            (next_x < now_x and next_x < min_x) or
            (next_y < now_y and next_y < min_y) or
            (next_x > now_x and next_x > max_x) or
            (next_y > now_y and next_y > max_y)
        )

    def wall_at(self, position):
        return any(self.object_at(wall, position) for wall in self._map['walls'])

    def dead_at(self, position):
        for enemy in self._map['enemies']:
            if self.is_enemy_visible(enemy) and self.object_at(enemy, position) and enemy['strength'] == 0:
                return True

        return False

    def object_at(self, obj, position):
        return obj['x'] == position['x'] and obj['y'] == position['y']

    def next_move(self):
        if self.soon_outside_of_map(self.next_position):
            return 'turn-left'
        if self.wall_at(self.next_position):
            return 'fire'
        if self.dead_at(self.next_position):
            return 'turn-left'
        if self.is_any_enemies:
            if self.can_fire_on_any_enemy:
                return 'fire'
            else:
                chase_move = self.get_chase_move()
                print("CHASEMOVE", chase_move)
                return chase_move
        return 'forward'

    def get_chase_move(self):
        min_x = 0
        max_x = self._map['mapWidth']
        min_y = 0
        max_y = self._map['mapHeight']
        you_x = self.you['x']
        you_y = self.you['y']
        you_direction = self.you['direction']
        enemy_x = self.closest_enemy['x']
        enemy_y = self.closest_enemy['y']
        left_positions = [{'x': x, 'y': you_y} for x in range(min_x, you_x)]
        right_positions = [{'x': x, 'y': you_y} for x in range(you_x + 1, max_x)]
        top_positions = [{'x': you_x, 'y': y} for y in range(min_y, you_y)]
        bottom_positions = [{'x': you_x, 'y': y} for y in range(you_y + 1, max_y)]
        print('left positions:', left_positions)
        print('right positions:', right_positions)
        print('top positions:', top_positions)
        print('bottom positions:', bottom_positions)
        enemy_future_positions = []
        if self.closest_enemy['direction'] == 'left':
            enemy_future_positions = [{'x': x, 'y': enemy_y} for x in range(min_x, enemy_x)]
        elif self.closest_enemy['direction'] == 'left':
            enemy_future_positions = [{'x': x, 'y': enemy_y} for x in range(you_x + 1, max_x)]
        elif self.closest_enemy['direction'] == 'left':
            enemy_future_positions = [{'x': enemy_x, 'y': y} for y in range(min_y, enemy_y)]
        elif self.closest_enemy['direction'] == 'left':
            enemy_future_positions = [{'x': enemy_x, 'y': y} for y in range(enemy_y + 1, max_y)]
        print('enemy future positions:', enemy_future_positions)
        left_intersections = [
            left_position
            for left_position in left_positions
            for enemy_future_position in enemy_future_positions
            if (
                left_position['x'] == enemy_future_position['x'] and
                left_position['y'] == enemy_future_position['y']
            )
        ]
        right_intersections = [
            right_position
            for right_position in right_positions
            for enemy_future_position in enemy_future_positions
            if (
                right_position['x'] == enemy_future_position['x'] and
                right_position['y'] == enemy_future_position['y']
            )
        ]
        top_intersections = [
            top_position
            for top_position in top_positions
            for enemy_future_position in enemy_future_positions
            if (
                top_position['x'] == enemy_future_position['x'] and
                top_position['y'] == enemy_future_position['y']
            )
        ]
        bottom_intersections = [
            bottom_position
            for bottom_position in bottom_positions
            for enemy_future_position in enemy_future_positions
            if (
                bottom_position['x'] == enemy_future_position['x'] and
                bottom_position['y'] == enemy_future_position['y']
            )
        ]
        print("LEFT I", left_intersections)
        print("RIGHT I", right_intersections)
        print("TOP I", top_intersections)
        print("BOTTOM I", bottom_intersections)

        if any(left_intersections):
            left_intersection = left_intersections[0]
            if you_direction == 'left':
                if you_x - left_intersection['x'] <= self.weapon_range:
                    return 'pass'
                else:
                    return 'forward'
            if you_direction == 'top':
                return 'turn-left'
            if you_direction == 'right':
                return 'turn-left'
            if you_direction == 'bottom':
                return 'turn-right'
        if any(right_intersections):
            right_intersection = right_intersections[0]
            if you_direction == 'right':
                if right_intersection['x'] - you_x <= self.weapon_range:
                    return 'pass'
                else:
                    return 'forward'
            if you_direction == 'top':
                return 'turn-right'
            if you_direction == 'left':
                return 'turn-left'
            if you_direction == 'bottom':
                return 'turn-left'
        if any(top_intersections):
            top_intersection = top_intersections[0]
            if you_direction == 'left':
                if you_y - top_intersection['y'] <= self.weapon_range:
                    return 'pass'
                else:
                    return 'forward'
            if you_direction == 'left':
                return 'turn-right'
            if you_direction == 'right':
                return 'turn-left'
            if you_direction == 'bottom':
                return 'turn-left'
        if any(bottom_intersections):
            bottom_intersection = bottom_intersections[0]
            if you_direction == 'bottom':
                if bottom_intersection['y'] - you_y <= self.weapon_range:
                    return 'pass'
                else:
                    return 'forward'
            if you_direction == 'top':
                return 'turn-left'
            if you_direction == 'right':
                return 'turn-right'
            if you_direction == 'left':
                return 'turn-left'
        return 'forward'
