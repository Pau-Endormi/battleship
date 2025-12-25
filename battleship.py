from random import randint

class BoardException(Exception):
  pass

class BoardOutException(BoardException):
  """
    Used to identify a shot into a dot that is outside the board
  """
  def __str__(self):
    return "Недопустимо стрелять за игровое поле!"

class SameShotException(BoardException):
  """
    Used to identify a shot at the same dot
  """
  def __str__(self):
    return "Недопустимо стрелять в одну и ту же клетку!"

class AdditionShipException(BoardException):
  """
    Used to identify the addition of the ship to the busy dot or to the outside dot
  """
  pass


class Dot:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

  def __repr__(self):
    return f"({self.x}, {self.y})"


class Ship:
  def __init__(self, nose_dot, length, direction):
    self.nose_dot = nose_dot  # here will be an object of Dot
    self.length = length
    self.direction = direction
    self.lives = length
  
  @property
  def dots(self):
    """
      Creates dots of ship.
      output: a list of all dots of ship
    """
    ship_dots = []
    for i in range(self.length):
      cur_x = self.nose_dot.x
      cur_y = self.nose_dot.y
      if self.direction == 0:  # if will be horizontal
        cur_x += i
      elif self.direction == 1:  # if will be vertical
        cur_y += i
      ship_dots.append(Dot(cur_x, cur_y))
    return ship_dots

  def damaged(self, shot):  # shot is object of Dot
    return shot in self.dots


class Board:
  def __init__(self, hid=False):
    self.space = [["~"] * 6 for i in range(6)]
    self.ships = []
    self.hid = hid
    self.destroyed_ships = 0
    self.busy_dots = []

  def add_ship(self, ship):
    for dot in ship.dots:
      if self.out(dot) or dot in self.busy_dots:
        raise AdditionShipException()
    for dot in ship.dots:
      self.space[dot.y][dot.x] = "■"
      self.busy_dots.append(dot)
    self.ships.append(ship)
    self.contour(ship)

  def contour(self, ship, verb=False):
    """
      input: object of Ship
      near - contains the nearest coordinates around the point
      Views points around the ship,
      if the point is not outside the board and is not busy,
      then adds it to the list 'busy_dots'.
    """
    near = [
      (-1, -1), (-1, 0), (-1, 1),
      (0, -1), (0, 0), (0, 1),
      (1, -1), (1, 0), (1, 1)
    ]
    for dot in ship.dots:
      for dx, dy in near:
        cur = Dot(dot.x + dx, dot.y + dy)
        if 0 <= cur.x < 6 and 0 <= cur.y < 6:
          if not(self.out(cur)) and cur not in self.busy_dots:
            if verb:
              self.space[cur.y][cur.x] = "."
            self.busy_dots.append(cur)

  def show_board(self):
    board = "---------------------------"
    board += "\n_ | 1 | 2 | 3 | 4 | 5 | 6 |"
    for i in range(6):
      board += f"\n{i + 1} |"
      for j in range(6):
        board += f" {self.space[i][j]} |"
    board += "\n---------------------------"
    if self.hid:
      board = board.replace("■", "~")
    return board

  def out(self, dot):
    """
      output: True if 'dot' is outside the board, otherwise False
    """
    return not(0 <= dot.x < len(self.space)) and (0 <= dot.y < len(self.space))

  def shot(self, dot):
    """
      output: True if the enemy ship got damage
      output: False if the enemy ship is destroyed or miss
    """
    if self.out(dot):
      raise BoardOutException()
    if dot in self.busy_dots:
      raise SameShotException()
    self.busy_dots.append(dot)

    for ship in self.ships:
      if dot in ship.dots:
        ship.lives -= 1
        self.space[dot.y][dot.x] = "X"
        if ship.lives == 0:
          self.destroyed_ships += 1
          self.contour(ship, verb=True)
          print("Корабль уничтожен!")
          return False
        else:
          print("Корабль ранен!")
          return True  # repeat the move
    self.space[dot.y][dot.x] = "."  # busy dot
    print("Мимо!")
    return False

  def begin(self):
    self.busy_dots = []


class Player:
  def __init__(self, board, enemy_board):
    self.board = board
    self.enemy_board = enemy_board
  
  def ask(self):
    raise NotImplementedError()  # reports that this method should only be at the descendants

  def move(self):
    while True:
      try:
        target = self.ask()
        move = self.enemy_board.shot(target)
        return move
      except BoardException as x:
        print(x)


class AI(Player):
  def ask(self):
    """output: object of Dot"""
    dot = Dot(randint(0, 5), randint(0, 5))
    print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
    return dot


class User(Player):
  def ask(self):
    """output: object of Dot"""
    while True:
      cords = input("Ваш ход: ").split()
      if len(cords) != 2:
        print("Необходимо ввести 2 координаты!")
        continue

      x, y = cords
      if not (x.isdigit()) or not (y.isdigit()):
        print("Необходимо ввести числа!")
        continue
      x, y = int(x), int(y)
      return Dot(x - 1, y - 1)


class Game:
  def __init__(self):
    self.ship_lens = [3, 2, 2, 1, 1, 1, 1]
    user_board = self.random_board()
    ai_board = self.random_board()
    ai_board.hid = True
    self.user = User(user_board, ai_board)
    self.ai = AI(ai_board, user_board)
  
  def create_place(self):
    board = Board()
    attempts = 0
    for x in self.ship_lens:
      while True:
        attempts += 1
        if attempts > 2000:
          return None
        ship = Ship(Dot(randint(0, 5), randint(0, 5)), x, randint(0, 1))
        try:
          board.add_ship(ship)
          break
        except AdditionShipException:
          pass
    board.begin()
    return board

  def random_board(self):
    board = None
    while board is None:
      board = self.create_place()
    return board

  def greet(self):
    print("-------------■-------------")
    print("     Игра «Морской бой»    ")
    print("    ввод: ширина и длина   ")
  
  def loop(self):
    num = 0
    move_game = 1
    while True:
      if num % 2 == 0:
        print(f"-------------{move_game}-------------")
        print(f"ХОД: {move_game}.")
        move_game += 1
      print("Доска пользователя:")
      print(self.user.board.show_board())
      print("Доска компьютера:")
      print(self.ai.board.show_board())
      if num % 2 == 0:
        print("Ходит пользователь!")
        move = self.user.move()
      else:
        print("Ходит компьютер!")
        move = self.ai.move()
      if move:  # repeat the move
        num -= 1
      if self.ai.board.destroyed_ships == len(self.user.board.ships):
        print("-" * 27)
        print("Победа пользователя!")
        break
      if self.user.board.destroyed_ships == len(self.ai.board.ships):
        print("-" * 27)
        print("Победа компьютера!")
        break
      num += 1  # next move
  
  def start(self):
    self.greet()
    self.loop()

obj_game = Game()
obj_game.start()
