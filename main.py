""" Main

Euan Freeman - 07/11/2024
Setups up the database schema in PostgreSQL to replicate the database side of the "Tuesday" spreadsheet

"""
from inspect import get_annotations

# from nextTuesdayPG import *
# # from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean, Enum, Float, Text
from sqlalchemy.orm import relationship, sessionmaker, Session
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import date, datetime
# import enum

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.widgets import Slider
import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.lines as lines

from GanttViewer import *

if __name__ == '__main__':
    # Database setup
    # engine = create_engine('postgresql://username:password@localhost/project_management')
    # Session = sessionmaker(bind=engine)
    # # Creating the tables in the database
    # Base.metadata.create_all(engine)
    # session = Session()

    # Sample data for Gantt chart
    # data = [
    #     {'Task': 'Task A', 'Start': '2024-11-01', 'End': '2024-11-05', 'Progress': 0.6, 'DependsOn': None},
    #     {'Task': 'Task B', 'Start': '2024-11-03', 'End': '2024-11-10', 'Progress': 0.3, 'DependsOn': 'Task A'},
    #     {'Task': 'Task C', 'Start': '2024-11-08', 'End': '2024-11-12', 'Progress': 0.8, 'DependsOn': 'Task B'},
    #     {'Task': 'Task D', 'Start': '2024-11-06', 'End': '2024-11-15', 'Progress': 0.5, 'DependsOn': None},
    #     {'Task': 'Task E', 'Start': '2024-11-10', 'End': '2024-11-18', 'Progress': 0.2, 'DependsOn': 'Task D'},
    #     {'Task': 'Task F', 'Start': '2024-11-15', 'End': '2024-11-25', 'Progress': 0.7, 'DependsOn': 'Task E'},
    #     {'Task': 'Task G', 'Start': '2024-11-20', 'End': '2024-11-28', 'Progress': 0.4, 'DependsOn': None},
    #     {'Task': 'Task H', 'Start': '2024-11-25', 'End': '2024-12-05', 'Progress': 0.1, 'DependsOn': 'Task G'}
    # ]
    #
    # # Convert data to DataFrame
    # df = pd.DataFrame(data)
    # df['Start'] = pd.to_datetime(df['Start'])
    # df['End'] = pd.to_datetime(df['End'])
    # df['Duration'] = (df['End'] - df['Start']).dt.days
    #
    #
    # # Plotting Gantt chart
    # def plot_gantt_chart(df):
    #     fig, ax = plt.subplots(figsize=(10, 6))
    #     fig.subplots_adjust(bottom=0.2, right=0.8)  # Adjust for sliders
    #
    #     # Assign a y position to each task
    #     y_pos = range(len(df))
    #     task_positions = {task: i for i, task in enumerate(df['Task'])}
    #
    #     for i, (task, start, duration, progress) in enumerate(
    #             zip(df['Task'], df['Start'], df['Duration'], df['Progress'])):
    #         # Full task bar
    #         rect = patches.FancyBboxPatch((mdates.date2num(start), i - 0.25), duration, 0.5,
    #                                       boxstyle="round,pad=0.1", edgecolor='black', facecolor='skyblue')
    #         ax.add_patch(rect)
    #
    #         # Progress bar
    #         progress_width = duration * progress
    #         progress_rect = patches.FancyBboxPatch((mdates.date2num(start), i - 0.25), progress_width, 0.5,
    #                                                boxstyle="round,pad=0.1", edgecolor='none', facecolor='darkblue',
    #                                                alpha=0.7)
    #         ax.add_patch(progress_rect)
    #
    #         # Draw arrows for dependencies
    #         if df.at[i, 'DependsOn'] is not None:
    #             dependent_task = df.at[i, 'DependsOn']
    #             if dependent_task in task_positions:
    #                 dep_index = task_positions[dependent_task]
    #                 dep_end = mdates.date2num(df.at[dep_index, 'End'])
    #                 x_start = dep_end
    #                 y_start = dep_index
    #                 x_end = mdates.date2num(start)
    #                 y_end = i
    #
    #                 # Draw the dependency path outside of the bars with no overlap
    #                 control_offset = 0.5
    #                 path_data = [
    #                     (mpath.Path.MOVETO, (x_start, y_start)),
    #                     (mpath.Path.LINETO, (x_start + control_offset, y_start)),
    #                     (mpath.Path.LINETO, (x_start + control_offset, (y_start + y_end) / 2)),
    #                     (mpath.Path.LINETO, (x_end - control_offset, (y_start + y_end) / 2)),
    #                     (mpath.Path.LINETO, (x_end - control_offset, y_end)),
    #                     (mpath.Path.LINETO, (x_end, y_end))
    #                 ]
    #                 codes, verts = zip(*path_data)
    #                 path = mpath.Path(verts, codes)
    #                 patch = patches.PathPatch(path, edgecolor='gray', linewidth=1.5, facecolor='none')
    #                 ax.add_patch(patch)
    #
    #                 # Add arrow head
    #                 arrow = patches.FancyArrowPatch((x_end - control_offset, y_end), (x_end, y_end),
    #                                                 mutation_scale=20, color='gray', arrowstyle='->')
    #                 ax.add_patch(arrow)
    #
    #     # Format x-axis as dates
    #     ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    #     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #     ax.set_xlim(df['Start'].min() - timedelta(days=1), df['End'].max() + timedelta(days=1))
    #
    #     # Set labels and title
    #     ax.set_yticks(y_pos)
    #     ax.set_yticklabels(df['Task'])
    #     ax.set_xlabel('Date')
    #     ax.set_title('Gantt Chart')
    #     plt.xticks(rotation=45)
    #
    #     # Display grid for better visualization
    #     plt.grid(axis='x', linestyle='--')
    #
    #     # Add scrollbars using sliders
    #     axcolor = 'lightgoldenrodyellow'
    #     ax_vscroll = plt.axes([0.85, 0.1, 0.03, 0.65], facecolor=axcolor)
    #     ax_hscroll = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
    #
    #     vscroll = Slider(ax_vscroll, 'Scroll Y', 0, len(df) - 1, valinit=0, valstep=1, orientation='vertical')
    #     hscroll = Slider(ax_hscroll, 'Scroll X', mdates.date2num(df['Start'].min() - timedelta(days=1)),
    #                      mdates.date2num(df['End'].max() + timedelta(days=1)),
    #                      valinit=mdates.date2num(df['Start'].min() - timedelta(days=1)))
    #
    #     def update(val):
    #         y_offset = int(vscroll.val)
    #         x_offset = mdates.num2date(hscroll.val)
    #         ax.set_ylim(y_offset - 0.5, y_offset + len(y_pos) - 0.5)
    #         ax.set_xlim(x_offset, x_offset + timedelta(days=10))
    #         fig.canvas.draw_idle()
    #
    #     vscroll.on_changed(update)
    #     hscroll.on_changed(update)
    #
    #     plt.tight_layout()
    #     plt.show()
    #
    #
    # # Plot the Gantt chart
    # plot_gantt_chart(df)
    # Example usage
    gantt = GanttViewer()

    # Adding tasks
    task_a = GTask('Task A', '2024-11-07', '2024-11-12', progress=0.6)
    task_b = GTask('Task B', '2024-11-03', '2024-11-10', progress=0.3)
    task_c = GTask('Task C', '2024-11-14', '2024-11-18', progress=0.3)
    task_d = GTask('Task D', '2024-11-06', '2024-11-14', progress=0.3)
    task_e = GTask('Task E', '2024-11-07', '2024-11-14', progress=0.3)
    gantt.add_task(task_c)
    gantt.add_task(task_a)
    gantt.add_task(task_d)
    gantt.add_task(task_e)
    gantt.add_task(task_b)

    # Adding dependency
    # arrow = GDependencyArrow(task_b, task_a)
    arrow2 = GDependencyArrow(task_b, task_c)
    # gantt.add_arrow(arrow)
    gantt.add_arrow(arrow2)

    # Adding scrollbars
    h_scroll = GScrollBar(orientation='horizontal')
    v_scroll = GScrollBar(orientation='vertical')
    gantt.add_scrollbar(h_scroll)
    gantt.add_scrollbar(v_scroll)

    # Display Gantt chart
    gantt.show()