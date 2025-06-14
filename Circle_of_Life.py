# Circle of Life Simulation
"""
This module simulates a simple ecosystem with zebras and lions.
Zebras eat grass, and lions eat zebras. The simulation runs for a specified number of years, and the state of the ecosystem is displayed at each year.

Classes:
    Cell: Represents a cell in the ecosystem that can grow grass.
    Animal: Base class for animals in the ecosystem.
    Zebra: A zebra in the ecosystem.
    Lion: A lion in the ecosystem.
    Ecosystem: Represents the ecosystem with zebras and lions.

Functions:
    None

Constants:
    GRID_SIZE: The size of the ecosystem grid.
    INITIAL_ZEBRAS: The initial number of zebras in the ecosystem.
    INITIAL_LIONS: The initial number of lions in the ecosystem.
    YEARS: The number of years the simulation runs.

"""
import random
import os
import sys

# Parameters
GRID_SIZE = 50
INITIAL_ZEBRAS = 20
INITIAL_LIONS = 5
YEARS = 20

class Cell:
    """A cell in the ecosystem that can grow grass."""
    def __init__(self):
        """Initialize a cell with grass."""
        self.grass = True
        self.regrow_timer = 0

    def eaten(self):
        """A zebra eats the grass in this cell."""
        self.grass = False
        self.regrow_timer = 1

    def step(self):
        """Regrow grass if it has been eaten."""
        if not self.grass:
            self.regrow_timer -= 1
            if self.regrow_timer <= 0:
                self.grass = True

class Animal:
    """Base class for animals in the ecosystem."""
    def __init__(self, x, y):
        """Initialize an animal at position (x, y)."""
        self.x = x
        self.y = y
        self.age = 0
        self.hungry = 0
        self.alive = True

    def neighbors(self):
        """Yield coordinates of neighboring cells."""
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                yield nx, ny

    def move(self, ecosys):
        """Move the animal to a new position."""
        raise NotImplementedError

    def step(self, ecosys, newborns):
        """Perform a step in the ecosystem."""
        if not self.alive:
            return
        self.age += 1
        ate = self.move(ecosys)
        self.hungry = 0 if ate else self.hungry + 1
        if self.dead():
            self.alive = False
            return
        baby = self.breed()
        if baby:
            newborns.append(baby)

    def dead(self):
        """Check if the animal is dead."""
        raise NotImplementedError

    def breed(self):
        """Check if the animal can breed."""
        raise NotImplementedError

class Zebra(Animal):
    """A zebra in the ecosystem."""
    def move(self, ecosys):
        """Move the zebra to a neighboring cell with grass."""
        grass_cells = [(nx,ny) for nx,ny in self.neighbors()
                       if ecosys.cells[ny][nx].grass and not ecosys.occupied(nx,ny)]
        if grass_cells:
            nx, ny = random.choice(grass_cells)
            ecosys.move(self, nx, ny)
            ecosys.cells[ny][nx].eaten()
            return True
        empties = [(nx,ny) for nx,ny in self.neighbors() if not ecosys.occupied(nx,ny)]
        if empties:
            nx, ny = random.choice(empties)
            ecosys.move(self, nx, ny)
        return False

    def dead(self):
        """Check if the zebra is dead due to hunger."""
        return self.hungry >= 3

    def breed(self):
        """Check if the zebra can breed."""
        if self.age >= 3:
            self.age = 0
            return Zebra(self.x, self.y)
        return None

class Lion(Animal):
    """A lion in the ecosystem."""
    def move(self, ecosys):
        """Move the lion to a neighboring cell with a zebra."""
        prey = [(nx,ny) for nx,ny in self.neighbors()
                if any(isinstance(a, Zebra) for a in ecosys.animals_at(nx,ny))]
        if prey:
            nx, ny = random.choice(prey)
            victim = next(a for a in ecosys.animals_at(nx,ny) if isinstance(a, Zebra))
            victim.alive = False
            ecosys.move(self, nx, ny)
            return True
        empties = [(nx,ny) for nx,ny in self.neighbors() if not ecosys.occupied(nx,ny)]
        if empties:
            nx, ny = random.choice(empties)
            ecosys.move(self, nx, ny)
        return False

    def dead(self):
        """Check if the lion is dead due to hunger."""
        return self.hungry >= 5

    def breed(self):
        """Check if the lion can breed."""
        if self.age >= 5:
            self.age = 0
            return Lion(self.x, self.y)
        return None

class Ecosystem:
    """The ecosystem containing grid and animals."""
    def __init__(self):
        """Initialize the ecosystem with a grid and animals."""
        self.cells = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.zebras = []
        self.lions = []
        self._populate()

    @property
    def animals(self):
        """Return a list of all animals in the ecosystem."""
        return [*self.zebras, *self.lions]

    def _populate(self):
        """Populate the ecosystem with initial zebras and lions."""
        coords = [(x,y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        random.shuffle(coords)
        for _ in range(INITIAL_ZEBRAS):
            x,y = coords.pop()
            self.zebras.append(Zebra(x,y))
        for _ in range(INITIAL_LIONS):
            x,y = coords.pop()
            self.lions.append(Lion(x,y))

    def occupied(self, x, y):
        """Check if a cell at (x, y) is occupied by an animal."""
        return any(a.alive and a.x==x and a.y==y for a in self.animals)

    def animals_at(self, x, y):
        """Return a list of animals at the cell (x, y)."""
        return [a for a in self.animals if a.alive and a.x==x and a.y==y]

    def move(self, animal, nx, ny):
        """Move an animal to a new position (nx, ny)."""
        animal.x, animal.y = nx, ny

    def step(self):
        """Perform a step in the ecosystem."""
        newborns = []
        for a in list(self.animals):
            a.step(self, newborns)
        self.zebras = [z for z in self.zebras if z.alive]
        self.lions = [l for l in self.lions if l.alive]
        for baby in newborns:
            if isinstance(baby, Zebra): self.zebras.append(baby)
            else: self.lions.append(baby)
        for row in self.cells:
            for cell in row:
                cell.step()

    def stats(self):
        """Return the current statistics of zebras and lions."""
        return len(self.zebras), len(self.lions)

    def display(self, year):
        """Display the current state of the ecosystem."""
        try:
            os.system('cls' if os.name=='nt' else 'clear')
        except Exception:
            pass
        col_head = '  ' + ''.join(f'{i:3}' for i in range(1, GRID_SIZE+1))
        print(col_head)
        print('-' * len(col_head))
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                if any(z.x==x and z.y==y for z in self.zebras):
                    row.append('Z  ')
                elif any(l.x==x and l.y==y for l in self.lions):
                    row.append('L  ')
                else:
                    row.append('.  ')
            print(f'{y+1:2}|{"".join(row)}|')

        zs, ls = self.stats()
        print(f'Zebras: {zs} | Lions: {ls} | time step = {year}')
        try:
            cmd = input('press Enter to continue, other key to quit: ')
        except EOFError:
            cmd = ''
        if cmd != '':
            print('Simulation terminated.')
            sys.exit()


if __name__ == '__main__':
    eco = Ecosystem()
    for year in range(1, YEARS+1):
        eco.step()
        eco.display(year)
    print('Simulation complete.')
