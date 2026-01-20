import heapq
import math

import matplotlib.pyplot as plt

import cv2
import numpy as np
import pathlib

# priority queue
import heapq

show_animation = True

class AStarPlanner:

    def __init__(self, obs_list_x, obs_list_y, resolution, min_safety_dist):
        """
        obs_list_x: x list of obstacles
        obs_list_y: y list of obstacles
        resolution: grid map resolution
        min_safety_dist: minimum safety distance to obstacle
        """
        self.resolution = resolution
        self.min_safety_dist = min_safety_dist
        self.min_x, self.min_y = 0, 0
        self.max_x, self.max_y = 0, 0
        self.x_width, self.y_width = 0, 0
        # create 2d grid map
        self.obstacle_map = None
        self.get_obstacle_map(obs_list_x, obs_list_y)
        # create motion model
        self.motion_model = self.get_motion_model()


    class Node:
        def __init__(self, x_idx, y_idx, cost, parent_idx):
            self.x_idx = x_idx  # index of grid map
            self.y_idx = y_idx  # index of grid map
            self.cost = cost # g value
            self.parent_idx = parent_idx

        def __str__(self):
            return str(self.x_idx) + "," + str(self.x_idx) + "," + str(
                self.cost) + "," + str(self.parent_idx)
        def __lt__(self, other):
            return self.cost < other.cost

    def search(self, start_x, start_y, goal_x, goal_y):
        """
        input:
            start_x: start x position
            start_y: start y position
            goal_x: goal x position
            goal_y: goal y position

        output:
            path_x: x list of the final path
            path_y: y list of the final path
        """
        
        # construct start and goal node
        start_node = self.Node(*self.convert_coord_to_idx(start_x, start_y), 0.0, -1)
        goal_node = self.Node(*self.convert_coord_to_idx(goal_x, goal_y), 0.0, -1)
        self.goal_node = goal_node
        # DONE: create open_set and closed set
        # open_set is a priority queue implemented by heapq
        self.open_set = []
        # heapq 不能索引内部的元素，所以建立一个dict，用node.idx 索引 node，方便后续实施lazy deletion 和更新
        self.open_dict = {}

        # open_set 里保存的值是f函数值，即 g + h
        self.push_open_set(start_node)
        # closed_set is a dictionary
        self.closed_set = {}

        # this is the astar algorithm main loop, you should finish it!
        while (len(self.open_set) > 0):
            # DONE: 1. pop the node with lowest value of the f function from the open_set, and add it to the closed_set
            f_value, cur_node = self.pop_open_set()
            self.closed_set[self.get_vec_index(cur_node)] = cur_node

            # plot cur_node
            if show_animation:
                plt.plot(*self.convert_idx_to_coord(cur_node.x_idx, cur_node.y_idx), marker='s',
                    color='dodgerblue', alpha=0.2)
                # for stopping simulation with the esc key
                plt.gcf().canvas.mpl_connect('key_release_event',
                                             lambda event: [exit(
                                                 0) if event.key == 'escape' else None])
                if len(self.closed_set.keys()) % 10 == 0:
                    plt.pause(0.0000001)
            
            # DONE: 2. determine whether the current node is the goal, and if so, stop searching
            if (self.get_vec_index(cur_node)) == (self.get_vec_index(goal_node)):
                return self.backtracking(cur_node, self.closed_set)


            # DONE: 3. expand neighbors of the current node
            for dx, dy, move_cost in self.motion_model:
                next_node = self.Node(
                    cur_node.x_idx + dx,
                    cur_node.y_idx + dy,
                    cur_node.cost + move_cost,
                    self.get_vec_index(cur_node)
                )
                # 检查是否有效
                if (not self.check_node_validity(next_node) 
                    or self.get_vec_index(next_node) in self.closed_set):
                        continue
                # push_open_set 里会自动处理已经存在的节点以及cost更小的情况
                self.push_open_set(next_node)

        if len(self.open_set) == 0:
            print("open_set is empty, can't find path")
            return [], []

        # DONE: 4. backtrack to get the shortest path
        path_x, path_y = self.backtracking(goal_node, self.closed_set)

        return path_x, path_y

    def backtracking(self, goal_node, closed_set):
        goal_x, goal_y = self.convert_idx_to_coord(goal_node.x_idx, goal_node.y_idx)

        path_x, path_y = [goal_x], [goal_y]

        # DONE: 4.1 backtracking from goal node to start node to extract the whole path
        cur_node = goal_node
        while cur_node.parent_idx != -1:
            cur_node = closed_set[cur_node.parent_idx]
            x_coord, y_coord = self.convert_idx_to_coord(cur_node.x_idx, cur_node.y_idx)
            path_x.append(x_coord)
            path_y.append(y_coord)
        return path_x, path_y

    def cal_heuristic_func(self, node1, node2):
        # DONE: 5 implement heuristic function to estimate the cost between node 1 and node 2
        # eculidean distance
        dx = node1.x_idx - node2.x_idx
        dy = node1.y_idx - node2.y_idx
        h_value = math.hypot(dx, dy)
        return h_value

    def convert_idx_to_coord(self, x_idx, y_idx):
        x_coord = x_idx * self.resolution + self.min_x
        y_coord = y_idx * self.resolution + self.min_y
        return x_coord, y_coord

    def convert_coord_to_idx(self, x_pos, y_pos):
        x_idx = round((x_pos - self.min_x) / self.resolution)
        y_idx = round((y_pos - self.min_y) / self.resolution)
        return x_idx, y_idx

    def get_vec_index(self, node):
        return (node.y_idx - self.min_y) * self.x_width + (node.x_idx - self.min_x)

    # DONE: open_set 的 push 实现，采用 lazy deletion，即不删除过期节点，只在 pop 的时候检查
    def push_open_set(self, node):
        idx = self.get_vec_index(node)
        if not idx in self.open_dict or node.cost < self.open_dict[idx].cost:
            self.open_dict[idx] = node
            heapq.heappush(self.open_set, 
                           (node.cost + self.cal_heuristic_func(node, self.goal_node), 
                            node))
    # DONE: open_set 的 pop 实现，采用 lazy deletion; 期间要检查是不是过期节点,如果是就继续pop
    def pop_open_set(self):
        while self.open_set:
            f_value, node = heapq.heappop(self.open_set)
            idx = self.get_vec_index(node)
            if self.open_dict.get(idx) == node:
                self.open_dict.pop(idx)
                return f_value, node
        raise RuntimeError("All nodes in priority queue are stale - algorithm error")


    def check_node_validity(self, node):
        x_coord, y_coord = self.convert_idx_to_coord(node.x_idx, node.y_idx)
        # check if the current node exceeds the map range
        if x_coord < self.min_x or x_coord > self.max_x \
            or y_coord < self.min_y or y_coord > self.max_y:
            return False

        # collision check
        if self.obstacle_map[node.x_idx][node.y_idx]:
            return False

        return True

    # generate 2d grid map from obstacle list
    def get_obstacle_map(self, obs_list_x, obs_list_y):
        print("Grid Map Info: ")
        self.min_x = round(min(obs_list_x))
        self.min_y = round(min(obs_list_y))
        self.max_x = round(max(obs_list_x))
        self.max_y = round(max(obs_list_y))
        print("min_x:", self.min_x)
        print("min_y:", self.min_y)
        print("max_x:", self.max_x)
        print("max_y:", self.max_y)

        self.x_width = round((self.max_x - self.min_x) / self.resolution)
        self.y_width = round((self.max_y - self.min_y) / self.resolution)
        print("x_length:", self.x_width)
        print("y_length:", self.y_width)

        # initialize obstacle map
        self.obstacle_map = [[False for _ in range(self.y_width)]
                             for _ in range(self.x_width)]
        for x_idx in range(self.x_width):
            for y_idx in range(self.y_width):
                x_coord, y_coord = self.convert_idx_to_coord(x_idx, y_idx)
                for obs_x, obs_y in zip(obs_list_x, obs_list_y):
                    dist = math.hypot(obs_x - x_coord, obs_y - y_coord)
                    if dist <= self.min_safety_dist:
                        self.obstacle_map[x_idx][y_idx] = True
                        break

    def get_motion_model(self):
        # 8-connected motion model
        # dx, dy, cost
        motion_model = [[1, 0, 1],
                        [0, 1, 1],
                        [-1, 0, 1],
                        [0, -1, 1],
                        [-1, -1, math.sqrt(2)],
                        [-1, 1, math.sqrt(2)],
                        [1, -1, math.sqrt(2)],
                        [1, 1, math.sqrt(2)]]

        return motion_model

def preprocess_image(image, threshold):
    # convert to gray image
    gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # binarization
    _, binary_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY)
    return binary_img

def extract_obstacle_list_from_img(binary_img):
    obstacle_x_list = []
    obstacle_y_list = []
    # get the size of binary image
    rows, cols = binary_img.shape[:2]

    for i in range(rows):
        for j in range(cols):
            if binary_img[i, j] == 0:
                # convert image frame to world frame
                obstacle_x_list.append(j)
                obstacle_y_list.append(rows - i - 1)

    return obstacle_x_list, obstacle_y_list

def main():

    # start and goal position
    start_x = 20.0  # [m]
    start_y = 40.0  # [m]
    goal_x = 140.0  # [m]
    goal_y = 40.0  # [m]
    grid_res = 2.0  # [m]
    min_safety_dist = 1.0  # [m]

    # read map
    image = cv2.imread(str(pathlib.Path.cwd()) + "/maps/" + "map1.png")
    # cv2.imshow('image', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    binary_img = preprocess_image(image, 127)
    
    obs_list_x, obs_list_y = extract_obstacle_list_from_img(binary_img)

    # plot map info
    if show_animation:
        plt.figure(figsize=(12, 12))
        plt.axis("equal")
        plt.plot(obs_list_x, obs_list_y, 'sk', markersize=2)
        plt.plot(start_x, start_y, marker='*', color='lime', markersize=8)
        plt.plot(goal_x, goal_y, marker='*', color='r', markersize=8)

    a_star = AStarPlanner(obs_list_x, obs_list_y, grid_res, min_safety_dist)
    path_x, path_y = a_star.search(start_x, start_y, goal_x, goal_y)
    
    # plot searched path
    if show_animation:
        plt.plot(path_x, path_y, ".-", color="royalblue")
        plt.show()

if __name__ == '__main__':
    main()