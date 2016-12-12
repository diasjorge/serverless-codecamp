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

    @property
    def can_fire_on_enemy(self, enemy):
        if self.you['direction'] == 'top':
            return (
                enemy['position']['x'] == self.you['position']['x'] and
                enemy['position']['y'] >= self.you['position']['y'] - self.weaponRange
            )
        if self.you['direction'] == 'bottom':
            return (
                enemy['position']['x'] == self.you['position']['x'] and
                enemy['position']['y'] <= self.you['position']['y'] + self.weaponRange
            )
        if self.you['direction'] == 'left':
            return (
                enemy['position']['x'] >= self.you['position']['x'] - self.weaponRange and
                enemy['position']['y'] == self.you['position']['y']
            )
        if self.you['direction'] == 'right':
            return (
                enemy['position']['x'] <= self.you['position']['x'] + self.weaponRange and
                enemy['position']['y'] == self.you['position']['y']
            )
        raise Exception('Invalid direction for your tank')

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
        walls = self._map['walls']
        for wall in walls:
            if wall['x'] == position['x'] and wall['y'] == position['y']:
                return True

        return False

    def next_move(self):
        if self.is_any_enemies and self.can_fire_on_any_enemy:
            return 'fire'
        if self.outside_of_map(self.next_position):
            return 'turn-left'
        if self.wall_at(self.next_position):
            return 'fire'
        return 'forward'
