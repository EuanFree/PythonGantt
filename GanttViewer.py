import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import timedelta
from matplotlib.widgets import Slider
import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.lines as lines
from sqlalchemy import false


class GanttViewer:
    def __init__(self, figsize=(10, 6)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.subplots_adjust(bottom=0.2, right=0.8)
        self.tasks = []
        self.arrows = []
        self.scrollbars = []

    def add_task(self, task):
        self.tasks.append(task)
        task.draw(self.ax)

    def remove_task(self, task):
        if task in self.tasks:
            task.remove(self.ax)
            self.tasks.remove(task)

    def add_arrow(self, arrow):
        self.arrows.append(arrow)
        arrow.set_viewer(self)
        arrow.draw(self.ax)

    def remove_arrow(self, arrow):
        if arrow in self.arrows:
            arrow.remove(self.ax)
            self.arrows.remove(arrow)

    def add_scrollbar(self, scrollbar):
        self.scrollbars.append(scrollbar)
        scrollbar.link(self)

    def remove_scrollbar(self, scrollbar):
        if scrollbar in self.scrollbars:
            scrollbar.unlink(self)
            self.scrollbars.remove(scrollbar)

    def show(self):
        # Set x-axis and y-axis limits to fit all tasks
        if self.tasks:
            min_start = min(task.start for task in self.tasks)
            max_end = max(task.end for task in self.tasks)
            self.ax.set_xlim(mdates.date2num(min_start) - 1, mdates.date2num(max_end) + 1)
            self.ax.set_ylim(-0.5, len(self.tasks) - 0.5)
        plt.tight_layout()
        plt.show()

class GScrollBar:
    def __init__(self, orientation='horizontal'):
        self.orientation = orientation
        self.slider = None

    def link(self, viewer):
        axcolor = 'lightgoldenrodyellow'
        if self.orientation == 'horizontal':
            ax_hscroll = viewer.fig.add_axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
            self.slider = Slider(ax_hscroll, 'Scroll X', mdates.date2num(viewer.tasks[0].start - timedelta(days=1)),
                                 mdates.date2num(viewer.tasks[-1].end + timedelta(days=1)),
                                 valinit=mdates.date2num(viewer.tasks[0].start - timedelta(days=1)))
            self.slider.on_changed(lambda val: self.update(val, viewer))
        elif self.orientation == 'vertical':
            ax_vscroll = viewer.fig.add_axes([0.85, 0.1, 0.03, 0.65], facecolor=axcolor)
            self.slider = Slider(ax_vscroll, 'Scroll Y', 0, len(viewer.tasks)-1, valinit=0, valstep=1, orientation='vertical')
            self.slider.on_changed(lambda val: self.update(val, viewer))

    def unlink(self, viewer):
        if self.slider:
            self.slider.disconnect_events()
            self.slider = None

    def update(self, val, viewer):
        if self.orientation == 'horizontal':
            x_offset = mdates.num2date(val)
            viewer.ax.set_xlim(x_offset, x_offset + timedelta(days=10))
        elif self.orientation == 'vertical':
            y_offset = int(val)
            viewer.ax.set_ylim(y_offset - 0.5, y_offset + len(viewer.tasks) - 0.5)
        viewer.fig.canvas.draw_idle()

class GTask:
    def __init__(self, name, start, end, progress=0):
        self.name = name
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
        self.progress = progress
        self.duration = (self.end - self.start).days
        self.rect_patch = None
        self.progress_patch = None
        self.hover = False

    def draw(self, ax):
        y_pos = len(ax.patches) // 2  # Adjust for both full and progress bars
        rect = patches.FancyBboxPatch((mdates.date2num(self.start), y_pos - 0.25), self.duration, 0.5,
                                      boxstyle="round,pad=0.1", edgecolor='none', facecolor='skyblue', linewidth=0)
        progress_width = self.duration * self.progress
        progress_rect = patches.FancyBboxPatch((mdates.date2num(self.start), y_pos - 0.25), progress_width, 0.5,
                                               boxstyle="round,pad=0.1", edgecolor='none', facecolor='darkblue', alpha=0.7)
        ax.add_patch(rect)
        ax.add_patch(progress_rect)
        self.rect_patch = rect
        self.progress_patch = progress_rect

        # Connect event for hover and clicks
        self.connect_events(ax)

    def remove(self, ax):
        if self.rect_patch:
            ax.patches.remove(self.rect_patch)
        if self.progress_patch:
            ax.patches.remove(self.progress_patch)

    def connect_events(self, ax):
        def on_hover(event):
            if self.rect_patch.contains(event)[0]:
                if not self.hover:
                    self.hover = True
                    self.rect_patch.set_edgecolor('black')
                    self.rect_patch.set_linewidth(1.5)
                    self.rect_patch.set_facecolor('lightgreen')  # Change color on hover
                    ax.figure.canvas.draw_idle()
            else:
                if self.hover:
                    self.hover = False
                    self.rect_patch.set_edgecolor('none')
                    self.rect_patch.set_linewidth(0)
                    self.rect_patch.set_facecolor('skyblue')  # Revert color when not hovering
                    ax.figure.canvas.draw_idle()

        def on_click(event):
            if self.rect_patch.contains(event)[0]:
                if event.button == 1:  # Left click
                    self.rect_patch.set_facecolor('yellow')
                elif event.button == 2:  # Middle click
                    self.rect_patch.set_facecolor('red')
                elif event.button == 3:  # Right click
                    self.rect_patch.set_facecolor('orange')
                ax.figure.canvas.draw_idle()

        def on_release(event):
            if self.rect_patch.contains(event)[0]:
                # If still hovering after release, set to hover color
                self.rect_patch.set_facecolor('lightgreen')
            else:
                # Revert to original color when mouse button is released
                self.rect_patch.set_facecolor('skyblue')
            ax.figure.canvas.draw_idle()

        self.rect_patch.figure.canvas.mpl_connect('motion_notify_event', on_hover)
        self.rect_patch.figure.canvas.mpl_connect('button_press_event', on_click)
        self.rect_patch.figure.canvas.mpl_connect('button_release_event', on_release)

    def get_positions(self):
        """
        Returns the positions of the middle of each side of the rectangle (start, top, bottom, end).
        """
        x_start = mdates.date2num(self.start)
        x_end = mdates.date2num(self.end)
        y_start = self.rect_patch.get_y()
        y_end = y_start + self.rect_patch.get_height()
        return {
            'start': (x_start, y_start + 0.25),
            'end': (x_end, y_start + 0.25),
            'top': ((x_start + x_end) / 2, y_end),
            'bottom': ((x_start + x_end) / 2, y_start)
        }

class GDependencyArrow:
    def __init__(self, start_task: GTask, end_task: GTask):
        """ Arrow that shows the dependency of one task to the next

        :param start_task: Starting task
        :param end_task: End task
        """
        self._start_task = start_task
        self._end_task = end_task
        self._viewer = None


    def set_viewer(self, viewer: GanttViewer):
        """ Sets the viewer for the arrow

        :param viewer: Gantt chart viewer
        :return:
        """
        self._viewer = viewer
        # Calculate the minimum spacing between bars
        _first_task = self._viewer.tasks[0]
        _first_task_top = _first_task.get_positions()['top']
        _first_task_bot = _first_task.get_positions()['bottom']
        self._task_gap = 200000000
        # Cycle through all the bars in the viewer to find the smallest gap
        for tsk in self._viewer.tasks:
            if abs(_first_task_top[1] - tsk.get_positions()['bottom'][1]) < self._task_gap:
                self._task_gap = abs(_first_task_top[1] - tsk.get_positions()['bottom'][1])
            if abs(_first_task_bot[1] - tsk.get_positions()['top'][1]) < self._task_gap:
                self._task_gap = abs(_first_task_bot[1] - tsk.get_positions()['top'][1])
        self.arrow_patch = None

    @staticmethod
    def add_curved_corner_to_path(path_list: list, radius: float, start_point: tuple, rotation_direction: int, quadrant: int):
        """ Add the curved corner to the provided path

        :param path_list: List of the path
        :param radius: Radius of the curved corner
        :param start_point: Starting point for the corner
        :param rotation_direction: Clockwise = 0, Anti-clockwise = -1
        :param quadrant: Quadrant of the circle, 0 = 12-3, 1 = 3-6, 2 = 6-9, 3 = 9-12
        :return: Updated path list
        """

        radius_factor = 0.75  # 0.552284749831
        curve_offset = radius * radius_factor  # Approximation for circular arcs using Bezier curves

        if rotation_direction == 0:  # Clockwise
            # print('rot 0')
            if quadrant == 0:
                # print('quad 0')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + curve_offset, start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] - radius)))
            elif quadrant == 1:
                # print('quad 1')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0], start_point[1] - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius + curve_offset, start_point[1] - radius)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] - radius)))
            elif quadrant == 2:
                # print('quad 2')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - curve_offset, start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] + radius - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] + radius)))
            elif quadrant == 3:
                # print('quad 3')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0], start_point[1] + curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius - curve_offset, start_point[1] + radius)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] + radius)))
        else:  # Anti-clockwise
            # print('rot 1')
            if quadrant == 0:
                # print('quad 0')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0], start_point[1] + curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius + curve_offset, start_point[1] + radius)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] + radius)))
            elif quadrant == 1:
                # print('quad 1')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + curve_offset, start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] + radius - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] + radius)))
            elif quadrant == 2:
                # print('quad 2')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0], start_point[1] - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius - curve_offset, start_point[1] - radius)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] + radius, start_point[1] - radius)))
            elif quadrant == 3:
                # print('quad 3')
                path_list.append((mpath.Path.LINETO, (start_point[0], start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - curve_offset, start_point[1])))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] - curve_offset)))
                path_list.append((mpath.Path.CURVE4, (start_point[0] - radius, start_point[1] - radius)))
        return path_list

    def draw(self, ax):
        """ Function to draw the dependency arrow

        :param ax: Axes to draw the dependency arrow
        :return:
        """
        # Get the start and end positions
        start_pos = self._start_task.get_positions()['end']
        # print(self._start_task.name)
        # print(self._end_task.name)
        end_pos = self._end_task.get_positions()['start']

        # Draw the dependency path with rounded corners using Bezier curves
        control_offset = 0.25
        radius = control_offset * 0.5
        radius_factor = 0.75  # 0.552284749831
        curve_offset = radius * radius_factor  # Approximation for circular arcs using Bezier curves

        arrow_path = [(mpath.Path.MOVETO, (start_pos[0], start_pos[1]))]

        # Create an intelligent path based on the start and finish positions
        # print("Start")
        # print(start_pos)
        # print(start_pos[0] + control_offset)
        # print("End")
        # print(end_pos[0] - control_offset)
        # print(end_pos)
        if start_pos[0] + control_offset > end_pos[0] - control_offset and start_pos[1] > end_pos[1]:
            # print('Opt 0')
            # Theoretical position when the end of the start task is after the start of the end task in the pair
            # Start position is above the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        0,
                                                        0)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         self._start_task.get_positions()['bottom'][1] - (self._task_gap / 2) + radius),
                                                        0,
                                                        1)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (end_pos[0] - control_offset + radius,
                                                         self._start_task.get_positions()['bottom'][1] - (
                                                                     self._task_gap / 2)),
                                                        1,
                                                        3)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (end_pos[0] - control_offset,
                                                         end_pos[1] + control_offset - radius),
                                                        1,
                                                        2)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        elif start_pos[0] + control_offset > end_pos[0] - control_offset and start_pos[1] < end_pos[1]:
            # print('Opt 1')
            # Theoretical position when the end of the start task is after the start of the end task in the pair
            # Start position is below the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        1,
                                                        1)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         self._start_task.get_positions()['top'][1] + (self._task_gap / 2) - radius),
                                                        1,
                                                        0)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (end_pos[0] - control_offset + radius,
                                                         self._start_task.get_positions()['top'][1] + (
                                                                     self._task_gap / 2)),
                                                        0,
                                                        2)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (end_pos[0] - control_offset,
                                                         end_pos[1] - control_offset + radius),
                                                        0,
                                                        3)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        elif start_pos[0] + control_offset < end_pos[0] - control_offset and start_pos[1] > end_pos[1]:
            # print('Opt 2')
            # The end of the start task is before the start of the end task in the pair
            # Start position is above the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        0,
                                                        0)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         end_pos[1] + control_offset - radius),
                                                        1,
                                                        2)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        elif start_pos[0] + control_offset < end_pos[0] - control_offset and start_pos[1] < end_pos[1]:
            # print('Opt 3')
            # The end of the start task is before the start of the end task in the pair
            # Start position is below the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        1,
                                                        1)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         end_pos[1] -  radius),
                                                        0,
                                                        3)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        elif start_pos[0] + control_offset == end_pos[0] - control_offset and start_pos[1] > end_pos[1]:
            # print('Opt 4')
            # The end of the start task is aligned with the start of the end task in the pair
            # Start position is above the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        0,
                                                        0)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         end_pos[1] + control_offset - radius),
                                                        0,
                                                        2)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        elif start_pos[0] + control_offset == end_pos[0] - control_offset and start_pos[1] < end_pos[1]:
            # print('Opt 5')
            # The end of the start task is aligned with the start of the end task in the pair
            # Start position is below the end position
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset - radius, start_pos[1]),
                                                        0,
                                                        0)
            arrow_path = self.add_curved_corner_to_path(arrow_path,
                                                        radius,
                                                        (start_pos[0] + control_offset,
                                                         end_pos[1] - control_offset + radius),
                                                        0,
                                                        3)
            arrow_path.append((mpath.Path.LINETO, end_pos))

        # Run through the path and check that none of the vertical lines pass through any task bars
        found_clash = False
        for i in range(len(arrow_path) - 1):
            start_vert = arrow_path[i][1]
            end_vert = arrow_path[i + 1][1]

            if start_vert[0] == end_vert[0]:  # Vertical line
                task_clash = [False for tsk in self._viewer.tasks]
                clash_found = False
                j = 0
                for task in self._viewer.tasks:
                    task_start = task.get_positions()['start']
                    task_end = task.get_positions()['end']
                    task_top = task.get_positions()['top']
                    task_bot = task.get_positions()['bottom']
                    if task_start[0] < start_vert[0] < task_end[0]:
                        print('Checking')
                        if task_bot[1] > min(start_vert[1], end_vert[1]) and \
                           max(start_vert[1], end_vert[1]) > task_top[1]:
                            task_clash[j] = True
                            clash_found = True
                    j += 1
                # if not clash_found:
                #     break
                #Create a buffer list for additional points in the line path
                corners = []
                # Upwards vertical
                if end_vert[1] > start_vert[1]:
                    for j in range(len(self._viewer.tasks)):
                        if task_clash[j]:
                            task_start = self._viewer.tasks[j].get_positions()['start']
                            task_top = self._viewer.tasks[j].get_positions()['top']
                            task_bot = self._viewer.tasks[j].get_positions()['bottom']
                            #Scrolling through the tasks will be correct with the path of the arrow
                            prev_clash = False
                            next_clash = False
                            move_left = False
                            move_right = False
                            if j > 0:
                                prev_clash = task_clash[j - 1]
                            if j < len(task_clash) - 1:
                                next_clash = task_clash[j + 1]
                            #Add additional corners into the path as appropriate
                            if not prev_clash:
                                move_left = True
                            elif self._viewer.tasks[j-1].get_positions()['start'][0] < task_start[0]:
                                move_left = True
                            if not next_clash:
                                move_right = True
                            elif self._viewer.tasks[j+1].get_positions()['start'][0] > task_start[0]:
                                move_right = True
                            if move_left:
                                #Corner to move left
                                if not prev_clash:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             ((start_vert[0]),
                                                                              task_bot[1]-control_offset-radius),
                                                                             0,
                                                                             1
                                                                             )
                                elif self._viewer.tasks[j - 1].get_positions()['start'][0] > task_start[0]:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             (self._viewer.tasks[j - 1].get_positions()[
                                                                                  'start'][0] - control_offset,
                                                                              task_top[1] + control_offset + radius),
                                                                             0,
                                                                             1
                                                                             )
                                corners = self.add_curved_corner_to_path(corners,
                                                                         radius,
                                                                         (task_start[0] - control_offset + radius,
                                                                          task_bot[1] - control_offset),
                                                                         1,
                                                                         3
                                                                         )
                            if move_right:
                                corners = self.add_curved_corner_to_path(corners,
                                                                         radius,
                                                                         (task_start[0] - control_offset,
                                                                          task_top[1] + control_offset - radius),
                                                                         1,
                                                                         2
                                                                         )
                                if not next_clash:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             (start_vert[0] - radius,
                                                                              task_top[1] + control_offset),
                                                                             0,
                                                                             0
                                                                             )
                                elif self._viewer.tasks[j + 1].get_positions()['start'][0] > task_start[0]:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             (self._viewer.tasks[j + 1].get_positions()[
                                                                                  'start'][0] - control_offset - radius,
                                                                              task_top[1] + control_offset),
                                                                             0,
                                                                             0
                                                                             )
                elif end_vert[1] < start_vert[1]:
                    for j in reversed(range(len(self._viewer.tasks))):
                        if task_clash[j]:
                            task_start = self._viewer.tasks[j].get_positions()['start']
                            task_top = self._viewer.tasks[j].get_positions()['top']
                            task_bot = self._viewer.tasks[j].get_positions()['bottom']
                            # Scrolling through the tasks will be correct with the path of the arrow
                            prev_clash = False
                            next_clash = False
                            move_left = False
                            move_right = False
                            if j > 0:
                                next_clash = task_clash[j - 1]
                            if j < len(task_clash) - 1:
                                prev_clash = task_clash[j + 1]
                            # Add additional corners into the path as appropriate
                            if not prev_clash:
                                move_left = True
                            elif self._viewer.tasks[j+1].get_positions()['start'][0] > task_start[0]:
                                move_left = True
                            if not next_clash:
                                move_right = True
                            elif self._viewer.tasks[j-1].get_positions()['start'][0] > task_start[0]:
                                move_right = True
                            if move_left:
                                #Corners to move left
                                if not prev_clash:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                              radius,
                                                                              ((start_vert[0]),
                                                                               task_top[1] + control_offset + radius),
                                                                              0,
                                                                              1
                                                                              )
                                elif self._viewer.tasks[j+1].get_positions()['start'][0] > task_start[0]:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             (self._viewer.tasks[j+1].get_positions()['start'][0]-control_offset,
                                                                              task_top[1] + control_offset + radius),
                                                                             0,
                                                                             1
                                                                             )
                                corners = self.add_curved_corner_to_path(corners,
                                                                          radius,
                                                                          (task_start[0] - control_offset + radius,
                                                                           task_top[1] + control_offset),
                                                                          1,
                                                                          3
                                                                          )
                            if move_right:
                                corners = self.add_curved_corner_to_path(corners,
                                                                          radius,
                                                                          (task_start[0] - control_offset,
                                                                           task_bot[1] - control_offset + radius),
                                                                          1,
                                                                          2
                                                                          )
                                if not next_clash:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                              radius,
                                                                              (start_vert[0] - radius,
                                                                               task_bot[1] - control_offset),
                                                                              0,
                                                                              0
                                                                              )
                                elif self._viewer.tasks[j-1].get_positions()['start'][0] > task_start[0]:
                                    corners = self.add_curved_corner_to_path(corners,
                                                                             radius,
                                                                             (self._viewer.tasks[j-1].get_positions()['start'][0] - control_offset - radius,
                                                                              task_bot[1] - control_offset),
                                                                             0,
                                                                             0
                                                                             )
                for j in range(len(corners)):
                    arrow_path.insert(i+1+j,corners[j])

        codes, verts = zip(*arrow_path)
        path = mpath.Path(verts, codes)
        patch = patches.PathPatch(path, edgecolor='gray', linewidth=1.5, facecolor='none')
        ax.add_patch(patch)

        # Add arrow head
        arrow = patches.FancyArrowPatch((end_pos[0] - control_offset, end_pos[1]), end_pos,
                                        mutation_scale=20, color='gray', arrowstyle='->')
        ax.add_patch(arrow)

        self.arrow_patch = (patch, arrow)

        # Connect hover event for the arrow
        self.connect_hover_event(ax)

    def connect_hover_event(self, ax):
        def on_hover(event):
            if self.arrow_patch[0].contains(event)[0]:
                self.arrow_patch[0].set_linewidth(3.0)  # Increase line thickness on hover
                ax.figure.canvas.draw_idle()
            else:
                self.arrow_patch[0].set_linewidth(1.5)  # Revert line thickness when not hovering
                ax.figure.canvas.draw_idle()

        self.arrow_patch[0].figure.canvas.mpl_connect('motion_notify_event', on_hover)

    def remove(self, ax):
        if self.arrow_patch:
            patch, arrow = self.arrow_patch
            ax.patches.remove(patch)
            ax.patches.remove(arrow)

