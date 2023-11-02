import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import networkx as nx
from collections import deque

class CityGrid:
    def __init__(self, rows, columns, range_R, probability=0.3):
        self.rows = rows
        self.columns = columns
        self.range_R = range_R
        self.grid = np.random.choice([1, 0], size=(rows, columns), p=[1 - probability, probability])
        self.towers = []
        
    def place_tower(self, row, col):
        if not self.grid[row][col]:
            print(f"Не могу разместить башню: ({row}, {col})")
            return

        for r in range(max(0, row - self.range_R), min(self.rows, row + self.range_R + 1)):
            if r>=0:
                for c in range(max(0, col - self.range_R), min(self.columns, col + self.range_R + 1)):
                    if c>=0:
                        self.grid[r][c] = 2
        self.grid[row][col] = 3
        self.towers.append((row, col))
    
    def optimize_tower_placement(self):
        # Создает список свободных участков
        non_obstructed_blocks = [(i, j) for i in range(self.rows) for j in range(self.columns) if self.grid[i][j] == 1]
    
        final_tower_locations = []
    
        # Цикл исполняется до того пока все свободные участки не покрыты
        while non_obstructed_blocks:
            # Расчет оптимального участка
            best_tower = None
            max_covered = 0
    
            for row, col in non_obstructed_blocks:
                # Подсчет количества покрытых участков
                coverage_count = 0
                for i in range(max(0, row - self.range_R), min(self.rows, row + self.range_R + 1)):
                    for j in range(max(0, col - self.range_R), min(self.columns, col + self.range_R + 1)):
                        if self.grid[i][j] == 1:
                            coverage_count += 1
    
                if coverage_count > max_covered:
                    best_tower = (row, col)
                    max_covered = coverage_count
    
            if best_tower is not None:
                # размещение башни на оптимальном участке
                row, col = best_tower
                final_tower_locations.append((row, col))
    
                # Обновление свободных участков
                for i in range(max(0, row - self.range_R), min(self.rows, row + self.range_R + 1)):
                    for j in range(max(0, col - self.range_R), min(self.columns, col + self.range_R + 1)):
                        if self.grid[i][j] == 1 and (i, j) in non_obstructed_blocks:
                            non_obstructed_blocks.remove((i, j))
    
        # Обновление матрицы города с башнями и покрытием
        for row, col in final_tower_locations:
            for r in range(max(0, row - self.range_R), min(self.rows, row + self.range_R + 1)):
                if r>=0:
                    for c in range(max(0, col - self.range_R), min(self.columns, col + self.range_R + 1)):
                        if c>=0:
                            self.grid[r][c] = 2
            self.grid[row][col] = 3
    
        self.towers.extend(final_tower_locations)


    def fill_obstacle_towers(self):
        # Заполняет башнями пустые участки
        while np.any(self.grid == 1):
            row, col = np.argwhere(self.grid == 1)[0]
            for i in range(row - self.range_R, row + self.range_R + 1):
                if i>=0:
                    for j in range(col - self.range_R, col + self.range_R + 1):
                        if j>=0:
                            if 0 <= i < self.rows and 0 <= j < self.columns:
                                if self.grid[i][j]!=3:
                                    self.grid[i][j] = 2 
            self.grid[row, col] = 3
            self.towers.append((row, col))

    def create_graph(self):
        # Создание графа с башнями и сетями
        G = nx.Graph()

        for i in range(self.rows):
            for j in range(self.columns):
                if self.grid[i, j] == 3:
                    G.add_node((i, j))

        for tower1 in G.nodes():
            for tower2 in G.nodes():
                if tower1 != tower2 and self.connected(tower1, tower2):
                    G.add_edge(tower1, tower2)

        return G

    def connected(self, tower1, tower2):
        # Проверяет связь между башнями
        i1, j1 = tower1
        i2, j2 = tower2
        distance = abs(i1 - i2) + abs(j1 - j2)
        return distance <= 2*self.range_R


    def find_most_reliable_path(self, tower1, tower2):
        graph = self.create_graph()

        # Проверяет есть ли путь напрямую
        if self.connected(tower1, tower2):
            try:
                shortest_path = nx.shortest_path(graph, source=tower1, target=tower2, weight='reliability')
                print(f"Самый надежный путь между башней {tower1} и башней {tower2} (Напрямую):")
                for i in range(len(shortest_path) - 1):
                    print(f"От башни {shortest_path[i]} к башни {shortest_path[i + 1]}")
                return shortest_path

            except nx.NetworkXNoPath:
                print(f"Не найден путь между башнями {tower1} и {tower2}. (Напрямую)")

        # Если прямой путь не найден ищем не напрямую
        indirect_path = self.find_indirect_path(tower1, tower2, graph)

        if indirect_path:
            print(f"Самый надежный путь между башней {tower1} и башней {tower2} (Не напрямую):")
            for i in range(len(indirect_path) - 1):
                print(f"От башни {indirect_path[i]} к башни {indirect_path[i + 1]}")
            return indirect_path
        else:
            print(f"Не найден путь между башнями {tower1} и {tower2}. (Не напрямую)")

    def find_indirect_path(self, tower1, tower2, graph):
        visited = set()
        queue = deque([(tower1, [tower1])])

        while queue:
            current_tower, path = queue.popleft()
            if current_tower == tower2:
                return path

            if current_tower not in visited:
                visited.add(current_tower)
                for neighbor in graph.neighbors(current_tower):
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))

        return None


    def visualize_obstacles(self):
        #Показывает город с препятсвиями и свободными участками
        plt.imshow(self.grid, cmap=ListedColormap(['black', 'white']), interpolation='none')
        plt.title("Город (Черный: препятствия; Белый: свободные)")
        plt.colorbar()
        plt.show()
        pass
    
    def display_tower_placement(self):
        # Показывает размещение башен и их покрытие
        plt.imshow(self.grid, cmap="jet", interpolation='none')
        plt.title("Карта башен и покрытия (Коричневый: Башни; Желтый/Синий: Покрытие)")
        plt.colorbar()
        plt.show()
        pass

    def visualize_data_paths(self, tower1, tower2, path):
        # Показывает связи
        cmap = ListedColormap(['black', 'white', 'brown', 'blue'])
        fig, ax = plt.subplots()
        ax.imshow(self.grid, cmap=cmap, interpolation='none')
        ax.set_title("Связь башен")
        
        for tower in self.towers:
            ax.add_patch(plt.Circle(tower, 0.2, color='brown'))
        
        try:
            
            for i in range(len(path) - 1):
                tower1 = path[i]
                tower2 = path[i + 1]
                plt.plot([tower1[1], tower2[1]], [tower1[0], tower2[0]], 'b-')
        
            plt.show()
        except TypeError:
            print("Не могу нарисовать график")



if __name__ == "__main__":
    city = CityGrid(rows=21, columns=21, range_R=3)
    city.visualize_obstacles()
    
    #Заполняет башнями пустые места
    city.optimize_tower_placement()
    city.display_tower_placement()
    
    #Размещает башню по указанным координатам
    #city.place_tower(2, 2)
    #city.display_tower_placement()
    
    for t in city.towers[1:]:
        path = city.find_most_reliable_path(city.towers[0],t)
        city.visualize_data_paths(city.towers[0], t, path)
    
