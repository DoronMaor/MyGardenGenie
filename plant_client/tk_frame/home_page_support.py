import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

import tk_frame.home_page as home_page

_debug = True  # False to eliminate debug printing from callback functions.


def main(garden_management, *args):
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = home_page.HomePage(garden_management, _top1)
    return _w1, root


if __name__ == '__main__':
    home_page.start_up()
