import random

GRID_SIZE = 50
INITIAL_ZEBRAS = 20
INITIAL_LIONS = 5
YEARS = 20

EMPTY = '.'
ZEBRA = 'Z'
LION = 'L'

class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.hungry_years = 0
        self.alive = True

    def get_neighbors(self, grid, target):
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[nx][ny] == target:
                    neighbors.append((nx, ny))
        return neighbors

class Zebra(Animal):
    def move(self, grid):
        neighbors = self.get_neighbors(grid, EMPTY)
        if neighbors:
            nx, ny = random.choice(neighbors)
            grid[self.x][self.y] = EMPTY
            self.x, self.y = nx, ny
            grid[nx][ny] = ZEBRA

    def graze(self, grass_map):
        if grass_map[self.x][self.y]:
            self.hungry_years = 0
            grass_map[self.x][self.y] = False
        else:
            self.hungry_years += 1

    def check_death(self):
        if self.hungry_years >= 3:
            self.alive = False

    def can_breed(self):
        return self.age >= 3

class Lion(Animal):
    def move(self, grid):
        zebra_neighbors = self.get_neighbors(grid, ZEBRA)
        if zebra_neighbors:
            nx, ny = random.choice(zebra_neighbors)
            grid[self.x][self.y] = EMPTY
            self.x, self.y = nx, ny
            grid[nx][ny] = LION
            return (nx, ny)
        neighbors = self.get_neighbors(grid, EMPTY)
        if neighbors:
            nx, ny = random.choice(neighbors)
            grid[self.x][self.y] = EMPTY
            self.x, self.y = nx, ny
            grid[nx][ny] = LION
        return None

    def hunt(self, eaten_pos):
        if eaten_pos:
            self.hungry_years = 0
        else:
            self.hungry_years += 1

    def check_death(self):
        if self.hungry_years >= 5:
            self.alive = False

    def can_breed(self):
        return self.age >= 5

class Ecosystem:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.grass_map = [[True for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.zebras = []
        self.lions = []
        self.timestep = 0
        self.init_animals()

    def init_animals(self):
        positions = set()
        while len(self.zebras) < INITIAL_ZEBRAS:
            x, y = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)
            if (x, y) not in positions:
                self.zebras.append(Zebra(x, y))
                self.grid[x][y] = ZEBRA
                positions.add((x, y))
        while len(self.lions) < INITIAL_LIONS:
            x, y = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)
            if (x, y) not in positions:
                self.lions.append(Lion(x, y))
                self.grid[x][y] = LION
                positions.add((x, y))

    def year_pass(self):
        self.timestep += 1
        for z in self.zebras:
            if z.alive:
                z.age += 1
        for l in self.lions:
            if l.alive:
                l.age += 1

        for l in self.lions:
            if l.alive:
                eaten_pos = l.move(self.grid)
                l.hunt(eaten_pos)
                if eaten_pos:
                    for z in self.zebras:
                        if z.alive and (z.x, z.y) == eaten_pos:
                            z.alive = False
                            break

        for z in self.zebras:
            if z.alive:
                z.move(self.grid)

        for z in self.zebras:
            if z.alive:
                z.graze(self.grass_map)

        for z in self.zebras:
            if z.alive:
                z.check_death()
        for l in self.lions:
            if l.alive:
                l.check_death()

        new_zebras = []
        for z in self.zebras:
            if z.alive and z.can_breed():
                neighbors = z.get_neighbors(self.grid, EMPTY)
                if neighbors:
                    nx, ny = random.choice(neighbors)
                    new_zebras.append(Zebra(nx, ny))
                    self.grid[nx][ny] = ZEBRA
        self.zebras.extend(new_zebras)

        new_lions = []
        for l in self.lions:
            if l.alive and l.can_breed():
                neighbors = l.get_neighbors(self.grid, EMPTY)
                if neighbors:
                    nx, ny = random.choice(neighbors)
                    new_lions.append(Lion(nx, ny))
                    self.grid[nx][ny] = LION
        self.lions.extend(new_lions)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.grass_map[i][j] = True

    def stat(self):
        zebras_alive = sum(1 for z in self.zebras if z.alive)
        lions_alive = sum(1 for l in self.lions if l.alive)
        return zebras_alive, lions_alive

    def display(self, area=10):
        print(f'Clock: {self.timestep}')
        # 列号部分：每个两格+空格
        col_head = '   ' + ''.join(f'{coord:2} ' for coord in range(area))
        print(col_head)
        show_grid = [[EMPTY for _ in range(area)] for _ in range(area)]
        for z in self.zebras:
            if z.alive and z.x < area and z.y < area:
                show_grid[z.x][z.y] = ZEBRA
        for l in self.lions:
            if l.alive and l.x < area and l.y < area:
                show_grid[l.x][l.y] = LION
        for row in range(area):
            line = ''.join(f'{cell:2} ' for cell in show_grid[row])
            print(f'{row:2} {line}')
        key = input("enter [q] to quit (or Enter继续):")
        if key == 'q':
            exit()



if __name__ == '__main__':
    eco = Ecosystem()
    for year in range(1, YEARS+1):
        eco.year_pass()
        zebras, lions = eco.stat()
        print(f'Year {year:02d}: 斑马={zebras}, 狮子={lions}')
        # 只显示左上10*10，需全图显示可改area=50
        eco.display(area=50)
