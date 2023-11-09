import rand_walk as rw
from matplotlib import pyplot as plt
import multiprocessing as mp
import numpy as np
import multiprocessing_win
import os
import sys
import pyformulas as pf
import time
from PIL import Image
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]));

#采用闭包的方法进行作图
def scatter_plot(x_val,y_val):
    global ax;
    global fig;
    global screen;
    #print(os.getpid());
    #print('access plot func successfully')

    col = (np.random.random(), np.random.random(), np.random.random());
    for i in range(len(x_val)):
        ax.scatter(x_val[i],y_val[i],s=15,c=col);
        fig.canvas.draw();
        image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        screen.update(image)


    return image;

class queue_xy():
    def __init__(self):
        m=mp.Manager();
        self.q_x=m.Queue();
        self.q_y=m.Queue();
        return;
if __name__ == '__main__':
    mp.freeze_support()
    print('Your have ', mp.cpu_count(), ' cpu cores\n');
    particle_num = int(input('How many particles you wanna to rand walk:\n'));

    cpu_num=mp.cpu_count();
    cpu_num=int(cpu_num);
    #设定最大进程为16
    if cpu_num>16:
        cpu_num=16;


    foot_steps=int(input('How many foot steps you wanna run:\n'));
    walk_particles = [rw.RandomWalk(foot_steps) for _ in range(particle_num)]  # 创建n个 random walk 的 particles
    # 采用process对象进行多进程防止引用符号=阻塞进程池

    points_data=[];
    for i in range(0,len(walk_particles),cpu_num):
        if len(walk_particles)-i<cpu_num:
            temp_core=len(walk_particles)-i;
            queue_group = [queue_xy() for _ in range(temp_core)];
            process_list = [
                mp.Process(target=walk_particles[i + _].fill_walk, args=(queue_group[_].q_x, queue_group[_].q_y,))
                for _ in range(temp_core)]
            print('Process Group ',i,' Created.\n');
            for j in range(len(process_list)):
                process_list[j].start();
            for j in range(len(process_list)):
                process_list[j].join();
            temp_data = [{'x_val': [], 'y_val': []} for _ in range(len(queue_group))];#将值临时储存在temp_data中
            for k in range(len(queue_group)):
                while not queue_group[k].q_x.empty():
                    temp_data[k]['x_val'].append(queue_group[k].q_x.get());
                    temp_data[k]['y_val'].append(queue_group[k].q_y.get());

            points_data += temp_data;
        else:

            temp_core = cpu_num;
            queue_group = [queue_xy() for _ in range(temp_core)];
            process_list = [
                mp.Process(target=walk_particles[i + _].fill_walk, args=(queue_group[_].q_x, queue_group[_].q_y,))
                for _ in range(temp_core)]
            print('Process Group ', i, ' Created.\n');
            for j in range(len(process_list)):
                process_list[j].start();
            for j in range(len(process_list)):
                process_list[j].join();
            temp_data = [{'x_val': [], 'y_val': []} for _ in range(len(queue_group))];  # 将值临时储存在temp_data中
            for k in range(len(queue_group)):
                while not queue_group[k].q_x.empty():
                    temp_data[k]['x_val'].append(queue_group[k].q_x.get());
                    temp_data[k]['y_val'].append(queue_group[k].q_y.get());

            points_data += temp_data;



    print('Calculation Finished')


    # 作图部分
    plt.style.use('classic');
    # 创建画布
    fig, ax = plt.subplots();
    screen = pf.screen(title='Random Walk Model');
    t_0=time.time();
    for i in range(len(points_data)):
        image=scatter_plot(points_data[i]['x_val'],points_data[i]['y_val']);
        im = Image.fromarray(image);

    im.show();
    fig.savefig(os.path.join(BASE_DIR, 'rand_walk.png'), dpi=600);
    screen.close()


