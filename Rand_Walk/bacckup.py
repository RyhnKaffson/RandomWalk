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

    particle_num = int(input('How many particles you wanna to rand walk:\n'));
    print('Your have ',mp.cpu_count(),' cpu cores\n');
    cpu_num=os.cpu_count();
    cpu_num=int(cpu_num);
    #设定最大进程为16
    if cpu_num>16:
        cpu_num=16;


    foot_steps=int(input('How many foot steps you wanna run:\n'));
    walk_particles = [rw.RandomWalk(foot_steps) for _ in range(particle_num)]  # 创建n个 random walk 的 particles
    # 采用process对象进行多进程防止引用符号=阻塞进程池

    q_list=[queue_xy() for _ in range(particle_num)];#创建队列列表
    points_data = [{'x_val':[],'y_val':[]} for _ in range(particle_num)];

    process_group=[walk_particles[i:i+cpu_num] for i in range(0,len(walk_particles),cpu_num)];#以cpu_num对进程进行分组
    points_data_group=[points_data[i:i+cpu_num] for i in range(0,len(points_data),cpu_num)];#同样的方法对points_data分组
    queue_group=[q_list[i:i+cpu_num] for i in range(0,len(q_list),cpu_num)]
    print('Group separated\n');
    for i in range(len(process_group)):
        if len(process_group[i])<cpu_num:
            process_list = [mp.Process(target=process_group[i][_].fill_walk, args=(queue_group[i][_].q_x, queue_group[i][_].q_y,)) for _ in range(len(process_group[i]))];
            print('process created\n');
            for j in range(len(process_list)):
                process_list[j].start();
            for j in range(len(process_list)):
                process_list[j].join();
            print('Processes all done!\n');
        else:
            process_list = [
                mp.Process(target=process_group[i][_].fill_walk, args=(queue_group[i][_].q_x, queue_group[i][_].q_y,))
                for _ in range(cpu_num)];
            print('process created\n');
            for j in range(len(process_list)):
                process_list[j].start();
            for j in range(len(process_list)):
                process_list[j].join();
            print('Processes all done!\n');


    print('Calculation Finished')
#通过不同的队列读取对应大的数据
    # 再将不同组的数据进行合并
    points_data = [];
    for i in range(len(points_data_group)):
        for j in range(len(points_data_group[i])):
            while not queue_group[i][j].q_x.empty():

                points_data_group[i][j]['x_val'].append(queue_group[i][j].q_x.get());
                points_data_group[i][j]['y_val'].append(queue_group[i][j].q_y.get());

        points_data+=points_data_group[i];







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
