import numpy as np
from random import choice
import os


class RandomWalk:
    def __init__(self,num):
        self.number_steps = num;
        self.x_vals = [0];
        self.y_vals = [0];
        return;

    # 储存随机漫步的点和随机的动力学设定
    def fill_walk(self,q_x,q_y):
        print(os.getpid());
        q_x.put(self.x_vals[0]);
        q_y.put(self.y_vals[0]);
        while (len(self.x_vals)) < self.number_steps:
            x_direction = choice([-1, 1]);
            y_direction = choice([-1, 1]);
            x_distance = choice(list(range(5)));
            y_distance = choice(list(range(5)));
            x_foot = x_distance * x_direction;
            y_foot = y_direction * y_distance;
            if (x_foot == 0) & (y_foot == 0):
                continue;

            x = self.x_vals[-1] + x_foot;  # 计算出来的foot要加上以前走的路程
            y = self.y_vals[-1] + y_foot;
            q_x.put(x);
            q_y.put(y);
            self.x_vals.append(x);
            self.y_vals.append(y);

        self.x_vals = np.array(self.x_vals);
        self.y_vals = np.array(self.y_vals);
        self.points = {};
        self.points['x_val'] = self.x_vals;
        self.points['y_val'] = self.y_vals;
        print('Process ',os.getpid(),' is done.\n')

