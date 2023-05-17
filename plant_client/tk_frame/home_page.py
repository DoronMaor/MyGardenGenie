from tkinter.constants import *
import mgg_functions as mgf
import os.path
import sys
import tkinter as tk
import tkinter.ttk as ttk

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
_font12 = "-family {Calibri} -size 14"
_font14 = "-family {Calibri} -size 14"
_font16 = "-family {Calibri} -size 14"

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
    style.configure('.', font=_font16)
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

        top.geometry("814x476+505+207")
        top.minsize(120, 1)
        top.maxsize(3604, 1061)
        top.resizable(1, 1)
        top.title("MyGardenGenie - Plant Client")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.top = top

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)
        top.configure(menu=self.menubar)

        self.menubar.add_command(compound='left', label='Test Routine', command=self.test_routine_action)
        self.bg_frame = tk.Frame(self.top)
        self.bg_frame.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.bg_frame.configure(relief='groove')
        self.bg_frame.configure(borderwidth="2")
        self.bg_frame.configure(relief="groove")
        self.bg_frame.configure(background="#ffffff")
        self.bg_frame.configure(highlightbackground="#d9d9d9")
        self.bg_frame.configure(highlightcolor="black")
        self.top_frame = tk.Frame(self.bg_frame)
        self.top_frame.place(relx=0.0, rely=0.0, relheight=0.149, relwidth=1.0)
        self.top_frame.configure(relief='flat')
        self.top_frame.configure(borderwidth="2")
        self.top_frame.configure(background="#FCFCFB")
        self.top_frame.configure(highlightbackground="#FCFCFB")
        self.top_frame.configure(highlightcolor="black")
        self.mgg_logo = tk.Label(self.top_frame)
        self.mgg_logo.place(relx=0.0, rely=0.0, height=71, width=356)
        self.mgg_logo.configure(activebackground="#FCFCFB")
        self.mgg_logo.configure(anchor='w')
        self.mgg_logo.configure(background="#FCFCFB")
        self.mgg_logo.configure(compound='left')
        self.mgg_logo.configure(disabledforeground="#a3a3a3")
        self.mgg_logo.configure(foreground="#000000")
        self.mgg_logo.configure(highlightbackground="#d9d9d9")
        self.mgg_logo.configure(highlightcolor="black")
        photo_location = os.path.join(_location, "LogoTK.png")
        global _img0
        _img0 = tk.PhotoImage(file=photo_location)
        self.mgg_logo.configure(image=_img0)
        self.mgg_logo.configure(text='''Label''')
        self.status_label = tk.Label(self.top_frame)
        self.status_label.place(relx=0.639, rely=0.0, height=72, width=304)
        self.status_label.configure(activebackground="#f9f9f9")
        self.status_label.configure(anchor='w')
        self.status_label.configure(background="#f3f3f3")
        self.status_label.configure(compound='left')
        self.status_label.configure(disabledforeground="#a3a3a3")
        self.status_label.configure(font=_font14)
        self.status_label.configure(foreground="#000000")
        self.status_label.configure(highlightbackground="#d9d9d9")
        self.status_label.configure(highlightcolor="black")
        self.status_label.configure(text='''Status:''')
        self.plant_A_label = tk.Label(self.bg_frame)
        self.plant_A_label.place(relx=0.012, rely=0.16, height=57, width=386)
        self.plant_A_label.configure(activebackground="#C8D496")
        self.plant_A_label.configure(background="#C8D496")
        self.plant_A_label.configure(compound='left')
        self.plant_A_label.configure(disabledforeground="#a3a3a3")
        self.plant_A_label.configure(foreground="#000000")
        self.plant_A_label.configure(highlightbackground="#d9d9d9")
        self.plant_A_label.configure(highlightcolor="black")
        self.plant_A_label.configure(text='''Plant A''')
        self.plant_B_label = tk.Label(self.bg_frame)
        self.plant_B_label.place(relx=0.516, rely=0.16, height=57, width=387)
        self.plant_B_label.configure(activebackground="#f9f9f9")
        self.plant_B_label.configure(background="#C8D496")
        self.plant_B_label.configure(compound='left')
        self.plant_B_label.configure(cursor="fleur")
        self.plant_B_label.configure(disabledforeground="#a3a3a3")
        self.plant_B_label.configure(foreground="#000000")
        self.plant_B_label.configure(highlightbackground="#d9d9d9")
        self.plant_B_label.configure(highlightcolor="black")
        self.plant_B_label.configure(text='''Plant B''')
        _style_code()
        self.TSeparator1 = ttk.Separator(self.bg_frame)
        self.TSeparator1.place(relx=0.5, rely=0.176, relheight=0.655)
        self.TSeparator1.configure(orient="vertical")
        self.plant_A_text = tk.Text(self.bg_frame)
        self.plant_A_text.place(relx=0.012, rely=0.294, relheight=0.55
                                , relwidth=0.473)
        self.plant_A_text.configure(background="white")
        self.plant_A_text.configure(font=_font14)
        self.plant_A_text.configure(foreground="black")
        self.plant_A_text.configure(highlightbackground="#d9d9d9")
        self.plant_A_text.configure(highlightcolor="black")
        self.plant_A_text.configure(insertbackground="black")
        self.plant_A_text.configure(selectbackground="#c4c4c4")
        self.plant_A_text.configure(selectforeground="black")
        self.plant_A_text.configure(wrap="word")
        self.plant_B_text = tk.Text(self.bg_frame)
        self.plant_B_text.place(relx=0.516, rely=0.294, relheight=0.55
                                , relwidth=0.473)
        self.plant_B_text.configure(background="white")
        self.plant_B_text.configure(cursor="fleur")
        self.plant_B_text.configure(font=_font14)
        self.plant_B_text.configure(foreground="black")
        self.plant_B_text.configure(highlightbackground="#d9d9d9")
        self.plant_B_text.configure(highlightcolor="black")
        self.plant_B_text.configure(insertbackground="black")
        self.plant_B_text.configure(selectbackground="#c4c4c4")
        self.plant_B_text.configure(selectforeground="black")
        self.plant_B_text.configure(wrap="word")
        self.plant_recog_btn = tk.Button(self.bg_frame)
        self.plant_recog_btn.place(relx=0.505, rely=0.861, height=62, width=395)
        self.plant_recog_btn.configure(activebackground="#a2b7c1")
        self.plant_recog_btn.configure(activeforeground="#000000")
        self.plant_recog_btn.configure(background="#557382")
        self.plant_recog_btn.configure(compound='left')
        self.plant_recog_btn.configure(disabledforeground="#a3a3a3")
        self.plant_recog_btn.configure(foreground="#ffffff")
        self.plant_recog_btn.configure(highlightbackground="#d9d9d9")
        self.plant_recog_btn.configure(highlightcolor="black")
        self.plant_recog_btn.configure(pady="0")
        self.plant_recog_btn.configure(relief="solid")
        self.plant_recog_btn.configure(text='''Plants Setup''')
        self.active_btn = tk.Button(self.bg_frame)
        self.active_btn.place(relx=0.011, rely=0.861, height=62, width=395)
        self.active_btn.configure(activebackground="#b5d7c0")
        self.active_btn.configure(activeforeground="black")
        self.active_btn.configure(background="#a0c2ab")
        self.active_btn.configure(compound='left')
        self.active_btn.configure(disabledforeground="#a3a3a3")
        self.active_btn.configure(foreground="#ffffff")
        self.active_btn.configure(highlightbackground="#d9d9d9")
        self.active_btn.configure(highlightcolor="black")
        self.active_btn.configure(pady="0")
        self.active_btn.configure(relief="solid")
        self.active_btn.configure(text='''Active''')

        self.active_btn.configure(command=lambda: self.toggle_active(garden_management))
        self.plant_recog_btn.configure(command=lambda: self.toggle_plant_recognition(garden_management))
        self.update_strings(garden_management)

    def format_plant_info(self, info_dict):
        if info_dict == {"PLANT_NAME": "No plant"} or info_dict == {"Error": None}:
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

    def set_status(self, status_str):
        self.status_label.configure(text='''Status: %s''' % status_str)

    def toggle_plant_recognition(self, garden_management):
        self.set_status("Plant Recognition")
        garden_management.do_plant_recognition = True
        self.update_strings(garden_management, status_change=False)

    def toggle_active(self, garden_management):
        current = garden_management.change_active()
        self.update_strings(garden_management)
        self.set_status("Active" if current else "Not Active")

    def update_strings(self, garden_management, status_change=True):
        if status_change:
            self.set_status(garden_management.status)

        plant_dict_A = mgf.get_plant_dict("A")
        plant_dict_B = mgf.get_plant_dict("B")
        if type(plant_dict_B) == bool:
            plant_dict_B = {"PLANT_NAME": "No plant"}
        if type(plant_dict_A) == bool:
            plant_dict_A = {"PLANT_NAME": "No plant"}
        self.plant_A_label.configure(text=plant_dict_A.get('PLANT_NAME', "No plant"))
        self.plant_B_label.configure(text=plant_dict_B.get('PLANT_NAME', "No plant"))

        self.plant_A_text.delete('1.0', END)
        self.plant_A_text.insert(INSERT, self.format_plant_info(plant_dict_A))
        self.plant_B_text.delete('1.0', END)
        self.plant_B_text.insert(INSERT, self.format_plant_info(plant_dict_B))

        self.active_btn.configure(text="Active" if garden_management.active_loop == True else "Not Active")
        self.active_btn.configure(background="#a0c2ab" if garden_management.active_loop == True else "#f57056")

    def test_routine_action(self):
        # Perform the desired action here
        print("Test Routine clicked!")


def start_up(garden_management):
    home_page_support.main(garden_management)


if __name__ == '__main__':
    home_page_support.main()
