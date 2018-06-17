# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 19:09:49 2017

@author: andi
"""
import argparse
import LaserDriver
import matplotlib.pyplot as plt
import numpy as np
import time


args = None
fig = None
ax = None
current_steps_x = 0
current_steps_y = 0
min_x = min_y = np.inf
max_x = max_y = -np.inf

def execute_move(steps):
    global fig, ax, min_x, min_y, max_x, max_y
    
    for step in steps:
        if step[0] == 'x':
            step_mm = step[1]/LaserDriver.x_steps_per_mm
            if step_mm > max_x:
                max_x = step_mm
            if step_mm < min_x:
                min_x = step_mm
        if step[0] == 'y':
            step_mm = step[1]/LaserDriver.y_steps_per_mm
            if step_mm > max_y:
                max_y = step_mm
            if step_mm < min_y:
                min_y = step_mm
    if fig is None:
        fig  = plt.figure()
        
    if ax is None:
        ax = fig.add_subplot(111)
    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])
    axbackground = fig.canvas.copy_from_bbox(ax.bbox)
    last_x = current_steps_x
    last_y = current_steps_y
    counter = 0
    while True:
        if counter >= len(steps):
            break
        else:
            step = steps[counter]
            x = y = 0
            if step[0] == 'x':
                step_mm = step[1]/LaserDriver.x_steps_per_mm
                x = step_mm
                y = last_y
                last_x = x
            if step[0] == 'y':
                step_mm = step[1]/LaserDriver.y_steps_per_mm
                x = last_x
                y = step_mm
                last_y = y
            p = ax.scatter(x, y)#, 'bo')
            if counter == 0:
                fig.canvas.draw()
            #ax.draw_artist(p[0])
            fig.canvas.restore_region(axbackground)

            # redraw just the points
            ax.draw_artist(p)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)
            fig.canvas.flush_events()
        counter += 1
        #fig.canvas.draw()
        #fig.canvas.flush_events()
        #plt.pause(0.1)
    
def process_line(line: str):
    global current_steps_x, current_steps_y
    line = line.upper()
    line = line.strip()
    current_steps_x = LaserDriver.current_steps_x
    current_steps_y = LaserDriver.current_steps_y
        
    if line.startswith('G00'):
        position = LaserDriver.parse_line(line)
        steps = LaserDriver.move_linear(position, engrave=False)
        execute_move(steps)
    elif line.startswith('G01'):
        position = LaserDriver.parse_line(line)
        steps = LaserDriver.move_linear(position, engrave=True)
        execute_move(steps)
    elif line.startswith('G02'):
        position, center = LaserDriver.parse_line(line)
        steps = LaserDriver.move_circular(position, center, 'cw')
        execute_move(steps)
    elif line.startswith('G03'):
        position, center = LaserDriver.parse_line(line)
        steps = LaserDriver.move_circular(position, center, 'ccw')
        execute_move(steps)
    elif line.startswith('('):
        # Comments from inkscape Gcodetools are in paranthesis
        pass
    else:
        print('unrecognized command')
        
def process_file(path: str):
    with open(path) as gcodefile:
        for line in gcodefile:
            process_line(line)

def main(line=None, file=None):
    global args
    parser = argparse.ArgumentParser(description='GCode interpreter')
    parser.add_argument('-l', '--line', help='interprets a single line of GCode')
    parser.add_argument('-f', '--file', help='interprets a GCode File')
    args = parser.parse_args()
    if args.line is not None:
        process_line(args.line)
    elif args.file is not None:
        process_file(args.file)
    if line is not None:
        process_line(line)
    if file is not None:
        process_file(file)
        
if __name__ == '__main__':
    #main('G00 X0 Y30')
    #time.sleep(3)
    main('G01 X60 Y60')
    time.sleep(2)
    main('G02 X60 Y0 I-30 J-30')
    #main('G00 X67.582181 Y265.710450')
    #time.sleep(2)
    #main('G02 X66.273540 Y259.131469 Z-0.125000 I-17.191706 J0.000001 F400.000000')
    #time.sleep(2)
    #main('G02 X62.546846 Y253.554078 Z-0.125000 I-15.883065 J6.578982')
    #time.sleep(2)
    #main('G02 X56.969455 Y249.827385 Z-0.125000 I-12.156371 J12.156373')
    #main(file='/home/andi/output_0020.ngc')