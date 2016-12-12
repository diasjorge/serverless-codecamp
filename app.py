from chalice import Chalice

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
    def is_any_enemies(self):
        return len(self.enemies) > 0

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

    def outside_of_map(self, position):
        return position['x'] < 0 or position['x'] >= self._map['mapWidth'] or \
            position['y'] < 0 or position['y'] >= self._map['mapHeight']

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
        if self.outside_of_map(self.next_position):
            return 'turn-left'
        if self.wall_at(self.next_position):
            return 'fire'
        if self.dead_at(self.next_position):
            return 'turn-left'
        if self.is_any_enemies and self.can_fire_on_any_enemy:
            return 'fire'
        return 'forward'
