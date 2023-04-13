import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import os.path
import mgg_functions as mgf

_script = sys.argv[0]
_location = os.path.dirname(_script)

import tk_frame.home_page_support as home_page_support

_bgcolor = '#d9d9d9'  # X11 color: 'gray85'
_fgcolor = '#000000'  # X11 color: 'black'
_compcolor = 'gray40'  # X11 color: #666666
_ana1color = '#c3c3c3'  # Closest X11 color: 'gray76'
_ana2color = 'beige'  # X11 color: #f5f5dc
_tabfg1 = 'black'
_tabfg2 = 'black'
_tabbg1 = 'grey75'
_tabbg2 = 'grey89'
_bgmode = 'light'
_font = "-family {Calibri} -size 14"

_style_code_ran = 0


def _style_code():
    global _style_code_ran
    if _style_code_ran:
        return
    style = ttk.Style()
    if sys.platform == "win32":
        style.theme_use('winnative')
    style.configure('.', background=_bgcolor)
    style.configure('.', foreground=_fgcolor)
    style.configure('.', font='TkDefaultFont')
    style.map('.', background=
    [('selected', _compcolor), ('active', _ana2color)])
    if _bgmode == 'dark':
        style.map('.', foreground=
        [('selected', 'white'), ('active', 'white')])
    else:
        style.map('.', foreground=
        [('selected', 'black'), ('active', 'black')])
    _style_code_ran = 1


class HomePage:
    def __init__(self, garden_management, top=None):
        """This class configures and populates the toplevel window.
           top is the toplevel containing window."""

        top.geometry("850x550+531+284")
        top.minsize(850, 550)
        top.maxsize(850, 550)
        top.resizable(1, 1)
        top.title("MyGardenGenie - Plant Client")
        top.configure(background="#fffffe")

        self.top = top

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)
        top.configure(menu=self.menubar)

        self.header_frame = tk.Frame(self.top)
        self.header_frame.place(relx=0.0, rely=0.0, relheight=0.1, relwidth=1.0)
        self.header_frame.configure(relief='solid')
        self.header_frame.configure(borderwidth="2")
        self.header_frame.configure(relief="solid")
        self.header_frame.configure(background="#ffffff")
        self.status_label = tk.Label(self.header_frame)
        self.status_label.place(relx=0.755, rely=0.171, height=40, width=195)
        self.status_label.configure(anchor='w')
        self.status_label.configure(background="#ffffff")
        self.status_label.configure(compound='left')
        self.status_label.configure(disabledforeground="#a3a3a3")
        self.status_label.configure(font=_font)
        self.status_label.configure(foreground="#000000")
        self.status_label.configure(text='''Status: Active/Not Active/Remote''')
        self.Label1 = tk.Label(self.header_frame)
        self.Label1.place(relx=0.004, rely=0.145, height=41, width=244)
        self.Label1.configure(anchor='w')
        self.Label1.configure(background="#ffffff")
        self.Label1.configure(compound='left')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''MyGardenGenie''')
        self.plants_frame = tk.Frame(self.top)
        self.plants_frame.place(relx=0.0, rely=0.1, relheight=0.1, relwidth=1.0)
        self.plants_frame.configure(relief='groove')
        self.plants_frame.configure(borderwidth="2")
        self.plants_frame.configure(relief="groove")
        self.plants_frame.configure(background="#d9d9d9")
        self.plants_frame.configure(highlightbackground="#fffffe")
        self.plants_frame.configure(highlightcolor="black")
        self.plant_A_label = tk.Label(self.plants_frame)
        self.plant_A_label.place(relx=0.0, rely=-0.036, height=61, width=434)
        self.plant_A_label.configure(background="#f5f5f5")
        self.plant_A_label.configure(compound='center')
        self.plant_A_label.configure(disabledforeground="#a3a3a3")
        self.plant_A_label.configure(font=_font)
        self.plant_A_label.configure(foreground="#000000")
        self.plant_A_label.configure(relief="groove")
        self.plant_A_label.configure(text='''Plant A''')
        self.plant_B_label = tk.Label(self.plants_frame)
        self.plant_B_label.place(relx=0.506, rely=0.0, height=61, width=423)
        self.plant_B_label.configure(activebackground="#f9f9f9")
        self.plant_B_label.configure(background="#f5f5f5")
        self.plant_B_label.configure(compound='center')
        self.plant_B_label.configure(disabledforeground="#a3a3a3")
        self.plant_B_label.configure(font=_font)
        self.plant_B_label.configure(foreground="#000000")
        self.plant_B_label.configure(highlightbackground="#d9d9d9")
        self.plant_B_label.configure(highlightcolor="black")
        self.plant_B_label.configure(text='''Plant B''')
        _style_code()
        self.TSeparator1 = ttk.Separator(self.top)
        self.TSeparator1.place(relx=0.5, rely=0.109, relheight=0.073)
        self.TSeparator1.configure(orient="vertical")
        self.plant_A_text = tk.Text(self.top)
        self.plant_A_text.place(relx=0.012, rely=0.218, relheight=0.571
                                , relwidth=0.475)
        self.plant_A_text.configure(background="white")
        self.plant_A_text.configure(font="-family {Calibri} -size 15")
        self.plant_A_text.configure(foreground="black")
        self.plant_A_text.configure(highlightbackground="#d9d9d9")
        self.plant_A_text.configure(highlightcolor="black")
        self.plant_A_text.configure(insertbackground="black")
        self.plant_A_text.configure(relief="raised")
        self.plant_A_text.configure(selectbackground="#c4c4c4")
        self.plant_A_text.configure(selectforeground="black")
        self.plant_A_text.configure(wrap="word")
        self.plant_B_text = tk.Text(self.top)
        self.plant_B_text.place(relx=0.515, rely=0.218, relheight=0.571
                                , relwidth=0.474)
        self.plant_B_text.configure(background="white")
        self.plant_B_text.configure(font="-family {Calibri} -size 15")
        self.plant_B_text.configure(foreground="black")
        self.plant_B_text.configure(highlightbackground="#d9d9d9")
        self.plant_B_text.configure(highlightcolor="black")
        self.plant_B_text.configure(insertbackground="black")
        self.plant_B_text.configure(relief="raised")
        self.plant_B_text.configure(selectbackground="#c4c4c4")
        self.plant_B_text.configure(selectforeground="black")
        self.plant_B_text.configure(wrap="word")
        self.low_seperator = ttk.Separator(self.top)
        self.low_seperator.place(relx=0.012, rely=0.825, relwidth=0.966)
        self.low_seperator.configure(cursor="fleur")
        self.log_out_btn = tk.Button(self.top)
        self.log_out_btn.place(relx=0.007, rely=0.849, height=74, width=276)
        self.log_out_btn.configure(activebackground="beige")
        self.log_out_btn.configure(activeforeground="#414141")
        self.log_out_btn.configure(background="#a7bc5b")
        self.log_out_btn.configure(compound='left')
        self.log_out_btn.configure(disabledforeground="#a3a3a3")
        self.log_out_btn.configure(font=_font)
        self.log_out_btn.configure(foreground="#000000")
        self.log_out_btn.configure(highlightbackground="#d9d9d9")
        self.log_out_btn.configure(highlightcolor="black")
        self.log_out_btn.configure(pady="0")
        self.log_out_btn.configure(text='''Logout''')
        self.active_btn = tk.Button(self.top)
        self.active_btn.place(relx=0.339, rely=0.849, height=74, width=276)
        self.active_btn.configure(activebackground="beige")
        self.active_btn.configure(activeforeground="#414141")
        self.active_btn.configure(background="#48d946")
        self.active_btn.configure(compound='left')
        self.active_btn.configure(disabledforeground="#a3a3a3")
        self.active_btn.configure(font=_font)
        self.active_btn.configure(foreground="#000000")
        self.active_btn.configure(highlightbackground="#d9d9d9")
        self.active_btn.configure(highlightcolor="black")
        self.active_btn.configure(pady="0")
        self.active_btn.configure(text='''Active/Not active''')
        self.plant_recog_btn = tk.Button(self.top)
        self.plant_recog_btn.place(relx=0.668, rely=0.849, height=74, width=276)
        self.plant_recog_btn.configure(activebackground="beige")
        self.plant_recog_btn.configure(activeforeground="#414141")
        self.plant_recog_btn.configure(background="#a7bc5b")
        self.plant_recog_btn.configure(compound='left')
        self.plant_recog_btn.configure(cursor="fleur")
        self.plant_recog_btn.configure(disabledforeground="#a3a3a3")
        self.plant_recog_btn.configure(font=_font)
        self.plant_recog_btn.configure(foreground="#000000")
        self.plant_recog_btn.configure(highlightbackground="#d9d9d9")
        self.plant_recog_btn.configure(highlightcolor="black")
        self.plant_recog_btn.configure(pady="0")
        self.plant_recog_btn.configure(command=lambda: toggle_plant_recognition(garden_management, self))
        self.plant_recog_btn.configure(text='''Recognize Plants''')
        self.top_seperator = ttk.Separator(self.top)
        self.top_seperator.place(relx=-0.012, rely=0.2, relwidth=1.518)

        update_strings(garden_management, self)


def format_plant_info(info_dict):
    if info_dict == {"PLANT_NAME": "No plant"}:
        return ""
    plant_name = info_dict['PLANT_NAME']
    plant_type = info_dict['PLANT_TYPE']
    light_lvl = info_dict['LIGHT_LVL']
    light_hours = info_dict['LIGHT_HOURS']
    moisture_lvl = info_dict['MOISTURE_LVL']
    mode = info_dict['MODE']

    formatted_str = f"Plant name: {plant_name}\n"
    formatted_str += f"Plant type: {plant_type}\n"
    formatted_str += f"Light level: {light_lvl}\n"
    formatted_str += f"Light hours: {light_hours}\n"
    formatted_str += f"Moisture level: {moisture_lvl}\n"
    formatted_str += f"Mode: {mode}\n"

    return formatted_str


def set_status(home_page_obj, status_str):
    home_page_obj.status_label.configure(text='''Status: %s''' % status_str)


def toggle_plant_recognition(garden_management, home_page_obj):
    set_status(home_page_obj, "Plant Recognition")
    garden_management.do_plant_recognition = True


def toggle_active(garden_management):
    garden_management.active_loop = not garden_management.active_loop


def update_strings(garden_management, home_page_obj):
    set_status(home_page_obj, garden_management.status)
    plant_dict_A = mgf.get_plant_dict("A")
    plant_dict_B = mgf.get_plant_dict("B")
    if type(plant_dict_A) == bool:
        plant_dict_B = {"PLANT_NAME": "No plant"}
    if type(plant_dict_A) == bool:
        plant_dict_A = {"PLANT_NAME": "No plant"}
    home_page_obj.plant_A_label.configure(text=plant_dict_A["PLANT_NAME"])
    home_page_obj.plant_B_label.configure(text=plant_dict_B["PLANT_NAME"])

    home_page_obj.plant_A_text.insert(INSERT, format_plant_info(plant_dict_A))
    home_page_obj.plant_B_text.insert(INSERT, format_plant_info(plant_dict_B))


def start_up(garden_management):
    home_page_support.main(garden_management)


if __name__ == '__main__':
    home_page_support.main()
