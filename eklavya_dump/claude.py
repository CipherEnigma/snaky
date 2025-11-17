def hamiltonian_cycle_heuristic(self, pos: List[int]) -> float:
    """Prefer moves that keep more space available"""
    x, y = pos
    open_spaces = 0
    for dx, dy in [(0, -self.block_size), (0, self.block_size), 
                   (-self.block_size, 0), (self.block_size, 0)]:
        check_pos = self.wrap_position([x + dx, y + dy])
        if check_pos not in self.snake:
            open_spaces += 1
    return open_spaces

def safe_a_star_pathfinding(self) -> List[List[int]]:
    """A* with safety check - ensures path doesn't trap snake"""
    start = tuple(self.snake[0])
    goal = tuple(self.food)

    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: self.manhattan_distance(self.snake[0], self.food)}

    while open_set:
        current = heappop(open_set)[1]

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(list(current))
                current = came_from[current]
            path.reverse()
            
            # Safety check: simulate eating food and check if tail is reachable
            if self.is_path_safe(path):
                return path
            else:
                # If unsafe, try to find path to tail instead
                return self.find_safe_move()

        for neighbor in map(tuple, self.get_neighbors(list(current))):
            tentative_g_score = g_score[current] + self.block_size
            
            # Add space preference to tie-breaking
            space_bonus = self.hamiltonian_cycle_heuristic(list(neighbor)) * 0.1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = (tentative_g_score + 
                                    self.manhattan_distance(list(neighbor), self.food) - 
                                    space_bonus)
                heappush(open_set, (f_score[neighbor], neighbor))

    return self.find_safe_move()

def is_path_safe(self, path: List[List[int]]) -> bool:
    """Check if following path to food leaves escape route"""
    if not path:
        return False
    
    # Simulate snake after eating food
    simulated_snake = [path[-1]] + self.snake[:-1]
    simulated_tail = simulated_snake[-1]
    simulated_head = simulated_snake[0]
    
    # Check if tail is reachable from new head position
    visited = {tuple(simulated_head)}
    queue = [simulated_head]
    
    while queue:
        current = queue.pop(0)
        if current == simulated_tail:
            return True
        
        for neighbor in self.get_neighbors_for_simulation(current, simulated_snake):
            neighbor_tuple = tuple(neighbor)
            if neighbor_tuple not in visited:
                visited.add(neighbor_tuple)
                queue.append(neighbor)
    
    return False

def get_neighbors_for_simulation(self, pos: List[int], snake: List[List[int]]) -> List[List[int]]:
    """Get neighbors excluding simulated snake body"""
    neighbors = []
    moves = [(0, -self.block_size), (0, self.block_size), 
            (-self.block_size, 0), (self.block_size, 0)]
    
    for dx, dy in moves:
        new_x = pos[0] + dx
        new_y = pos[1] + dy
        new_pos = self.wrap_position([new_x, new_y])
        
        if new_pos not in snake[:-1]:  # Tail will move
            neighbors.append(new_pos)
    
    return neighbors

def find_safe_move(self) -> List[List[int]]:
    """If no safe path to food, follow tail to stay alive"""
    if len(self.snake) > 3:
        tail = self.snake[-1]
        start = tuple(self.snake[0])
        goal = tuple(tail)
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        
        while open_set:
            current = heappop(open_set)[1]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path
            
            for neighbor in map(tuple, self.get_neighbors(list(current))):
                tentative_g_score = g_score[current] + self.block_size
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heappush(open_set, (tentative_g_score, neighbor))
    
    # Fallback: move to most open space
    neighbors = self.get_neighbors(self.snake[0])
    if neighbors:
        best_neighbor = max(neighbors, 
                          key=lambda n: self.hamiltonian_cycle_heuristic(n))
        return [best_neighbor]
    
    return []