import pygame
import sys
from PIL import Image, ImageDraw

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        self.player_position = self.start

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self, method='bfs'):
        if method == 'bfs':
            frontier = QueueFrontier()
        elif method == 'dfs':
            frontier = StackFrontier()
        else:
            raise ValueError("Unknown method")

        start = Node(state=self.start, parent=None, action=None)
        frontier.add(start)
        self.num_explored = 0
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")
            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def move_player(self, direction):
        row, col = self.player_position
        if direction == "up":
            new_position = (row - 1, col)
        elif direction == "down":
            new_position = (row + 1, col)
        elif direction == "left":
            new_position = (row, col - 1)
        elif direction == "right":
            new_position = (row, col + 1)

        if 0 <= new_position[0] < self.height and 0 <= new_position[1] < self.width and not self.walls[new_position[0]][new_position[1]]:
            self.player_position = new_position


# Función para cargar imágenes y redimensionarlas
def load_and_scale_image(path, size):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, size)

# Función para dibujar el laberinto
def draw_maze(maze, screen, show_solution, show_explored, images, cell_size):
    wall_img, path_img, start_img, goal_img, player_img = images
    solution = maze.solution[1] if maze.solution is not None else None
    for i, row in enumerate(maze.walls):
        for j, col in enumerate(row):
            if col:
                screen.blit(wall_img, (j * cell_size, i * cell_size))
            elif (i, j) == maze.start:
                screen.blit(start_img, (j * cell_size, i * cell_size))
            elif (i, j) == maze.goal:
                screen.blit(goal_img, (j * cell_size, i * cell_size))
            elif solution is not None and show_solution and (i, j) in solution:
                screen.blit(path_img, (j * cell_size, i * cell_size))
            elif show_explored and (i, j) in maze.explored:
                screen.blit(path_img, (j * cell_size, i * cell_size))
            else:
                screen.blit(path_img, (j * cell_size, i * cell_size))

    player_x, player_y = maze.player_position
    screen.blit(player_img, (player_y * cell_size, player_x * cell_size))

# Función para mostrar la pantalla principal
def main_menu(screen):
    font = pygame.font.SysFont(None, 60)
    button_font = pygame.font.SysFont(None, 40)
    screen.fill((255, 255, 255))

    # Título
    title = font.render("Elige un Nivel", True, (0, 0, 0))
    screen.blit(title, (550, 100))

    # Botones de niveles
    levels = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
    buttons = []
    for i, level in enumerate(levels):
        button = pygame.Rect(550, 200 + i * 100, 200, 50)
        buttons.append(button)
        pygame.draw.rect(screen, (0, 0, 255), button)
        text = button_font.render(level, True, (255, 255, 255))
        screen.blit(text, (button.x + 50, button.y + 10))

    pygame.display.flip()
    return buttons

# Función principal del juego
def main():
    pygame.init()
    screen = pygame.display.set_mode((1300, 800))
    pygame.display.set_caption("Juego de Laberinto")

    cell_size = 30

    # Pantalla principal
    buttons = main_menu(screen)

    running = True
    selected_level = None

    # Bucle principal de la pantalla inicial
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Manejar clic en los botones de nivel
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.collidepoint(event.pos):
                        selected_level = f"laberinto{i+1}.txt"
                        running = False

    if selected_level:
        play_game(selected_level, screen, cell_size)

    pygame.quit()

def play_game(filename, screen, cell_size):
    # Instanciar el laberinto
    maze_bfs = Maze(filename)
    maze_dfs = Maze(filename)

    # Resolver los laberintos con BFS y DFS
    maze_bfs.solve(method='bfs')
    maze_dfs.solve(method='dfs')

    # Cargar imágenes
    wall_img = load_and_scale_image("pared.jpg", (cell_size, cell_size))
    path_img = load_and_scale_image("camino.jpg", (cell_size, cell_size))
    start_img = load_and_scale_image("portal.jpg", (cell_size, cell_size))
    goal_img = load_and_scale_image("meta.jpg", (cell_size, cell_size))
    player_img = load_and_scale_image("player3.jpg", (cell_size, cell_size))

    images = (wall_img, path_img, start_img, goal_img, player_img)

    show_solution = True
    show_explored = False
    button_font = pygame.font.SysFont(None, 40)
    button = pygame.Rect(900, 50, 280, 50)

    running = True
    while running:
        screen.fill((255, 255, 255))

        # Dibujar el laberinto BFS por defecto
        draw_maze(maze_bfs, screen, show_solution, show_explored, images, cell_size)

        pygame.draw.rect(screen, (0, 0, 255), button)
        button_text = button_font.render("Estados Explorados", True, (255, 255, 255))
        screen.blit(button_text, (button.x + 10, button.y + 10))

        # Mostrar el número de estados explorados por BFS y DFS
        estados_bfs_text = button_font.render(f"BFS Explorados: {maze_bfs.num_explored}", True, (0, 0, 0))
        estados_dfs_text = button_font.render(f"DFS Explorados: {maze_dfs.num_explored}", True, (0, 0, 0))
        screen.blit(estados_bfs_text, (button.x, button.y + 60))  # Posicionar debajo del botón
        screen.blit(estados_dfs_text, (button.x, button.y + 100))  # Posicionar debajo de BFS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    show_explored = not show_explored

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    maze_bfs.move_player("up")
                elif event.key == pygame.K_DOWN:
                    maze_bfs.move_player("down")
                elif event.key == pygame.K_LEFT:
                    maze_bfs.move_player("left")
                elif event.key == pygame.K_RIGHT:
                    maze_bfs.move_player("right")

        if maze_bfs.player_position == maze_bfs.goal:
            print("¡Has llegado a la meta!")
            running = False

        pygame.display.flip()



if __name__ == "__main__":
    main()
