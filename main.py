# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter as tk
from tkinter import font
from tkinter import filedialog
import math
import json

class Motif:
    def __init__(self):
        self.scale = (1.0,1.0) # x and y scaling of motif
        self.translation = 0 # translation of motif
        self.modulo = 12
        self.points = []
        self.color = 'black'

        # GUI related member variables
        self.canvas = None
        self.frame = None
        self.parent_frame = None
        self.scale_entry = None

    def __del__(self):
        #self.frame.destroy()
        print('bkljsdfklsdjfklj')

    def set_color(self, new_color):
        self.color = new_color

    def set_scale(self, scale):
        '''
        Set the uniform scaling of the motif
        :param scale: positive float
        '''
        scale = float(scale)
        if scale <= 0.0:
            raise Exception('Scale must be positive')

        self.scale = (scale, scale)

    def set_translation(self, translation):
        '''
        Set the translation of the motif
        :param translation: arbitrary float
        '''
        self.translation = int(translation)

    def set_points_from_triangle(self, a, b, c):
        if a*b*c == 0.0:
            raise Exception('triangle side can not be zero')

        s = 1.0/(a+b+c)
        a = a*s
        b = b*s
        c = c*s

        A = math.acos((b*b+c*c-a*a)/(2.0*b*c))
        B = math.acos((a*a+c*c-b*b)/(2.0*a*c))
        C = math.acos((a*a+b*b-c*c)/(2.0*a*b))

        self.points = []
        self.points.append((0.0, 0.0))
        self.points.append((c*math.cos(B), c*math.sin(B)))
        self.points.append((a, 0.0))
        self.points.append((a + a*math.cos(C), a*math.sin(C)))
        self.points.append((a + b, 0.0))
        self.points.append((a + b + b*math.cos(A), b*math.sin(A)))
        self.points.append((a + b + c, 0.0))

    def set_points(self, points):
        self.points = []

    def interpolate(self, p0 ,p1, x):
        return (p1[1]-p0[1])/(p1[0]-p0[0])/self.scale[0]*(x - p0[0]*self.scale[0]) + p0[1]

    def get_transformed_points(self):
        return [(x*self.scale[0] + self.translation, y*self.scale[1]) for (x,y) in self.points]

    def get_value(self, n):
        x = (n - self.translation) % self.scale[0]
        x = float(x)

        for i in range(6):
            if x < self.points[i+1][0]*self.scale[0]:
                return self.interpolate(self.points[i], self.points[i+1], x)*self.scale[1]

    def gui_set_scale(self, value):
        self.set_scale(value)
        self.motif_scale.set(value)

    def gui_set_translation(self, value):
        self.set_translation(value)
        self.motif_translation.set(value)

    def gui_on_entry_submit(self, event, entry_variable, slider):
        '''
        Callback called when user hits <return> in entry fields
        :param event:
        :param slider: The slider to udpate
        '''
        new_value = float(entry_variable.get())

        if new_value < slider.cget('from'):
            slider.configure(from_=new_value)
        elif new_value > slider.cget('to'):
            slider.configure(to=new_value)
        elif slider.get() == slider.cget('from'):
            slider.configure(from_=new_value)
        elif slider.get() == slider.cget('to'):
            slider.configure(to=new_value)

        slider.set(new_value)

    def gui_initialize(self, parent_frame, canvas):
        self.parent_frame = parent_frame
        self.canvas = canvas

        self.frame = tk.Frame(self.parent_frame, relief=tk.RAISED, bd=4)

        # Create slider for scaling motif
        self.motif_scale_slider = tk.Scale(self.frame,
                                      command=self.gui_set_scale,
                                      from_=50.0,
                                      to=250.0,
                                      label='S',
                                      showvalue=0)

        self.motif_scale_slider.pack(side=tk.LEFT)

        # Create editable text label for slider value
        self.motif_scale = tk.StringVar()
        self.motif_scale.set(50)

        self.scale_entry = tk.Entry(self.frame,
                                    width=4,
                                    textvariable=self.motif_scale
                                    )
        self.scale_entry.bind('<Return>', lambda eff: self.gui_on_entry_submit(eff, self.motif_scale, self.motif_scale_slider))
        self.scale_entry.pack(side=tk.LEFT)

        # Create slider for translating motif
        self.motif_translation_slider = tk.Scale(self.frame,
                                            command=self.gui_set_translation,
                                            from_=0,
                                            to=1024,
                                            label='T')

        self.motif_translation_slider.pack(side=tk.LEFT)
        # Create editable text label for slider value
        self.motif_translation = tk.StringVar()
        self.motif_translation.set(0)

        self.translation_entry = tk.Entry(self.frame,
                                    width=4,
                                    textvariable=self.motif_translation
                                    )
        self.translation_entry.bind('<Return>', lambda eff: self.gui_on_entry_submit(eff, self.motif_translation, self.motif_translation_slider))
        self.translation_entry.pack(side=tk.LEFT)

        self.frame.pack(side=tk.LEFT)

    def gui_update_canvas(self):
        if self.canvas:
            s = []
            for i in range(self.canvas.winfo_width()):
                s.append(i)
                s.append(self.canvas.winfo_height() - int(self.get_value(i)))

            self.canvas.create_line(fill=self.color, width=2, *s)

class Trio:
    def __init__(self):
        self.motif_list = []

        self.root = tk.Tk()
        self.root.configure(bg='gray40')

        # Create menubar
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label='Load From File...', command=self.load_from_file)
        filemenu.add_command(label='Save To File', command=self.save_to_file)
        self.menubar.add_cascade(label='File', menu=filemenu)
        self.root.config(menu=self.menubar)

        # Create canvas
        self.main_canvas = tk.Canvas(self.root, bg='white', height=512, width=1024)
        self.main_canvas.pack(anchor='n')

        # Create slider frame
        self.slider_frame = tk.Frame(self.root)
        self.slider_frame.pack(anchor='s')
        self.helv = font.Font(family='Helvetica', size=6)

    def load_from_file(self):
        filename = filedialog.askopenfilename()
        self.import_from_file(filename)

    def save_to_file(self):
        filename = filedialog.asksaveasfilename()
        self.export_to_file(filename)

    def update_gui(self):
        self.main_canvas.delete('all')

        # Draw grid
        grid_width = 15
        for i in range(int(self.main_canvas.winfo_width() / grid_width)):
            self.main_canvas.create_line(i * grid_width, 0, i * grid_width, self.main_canvas.winfo_height(), fill='gray90')
            self.main_canvas.create_text(i * grid_width + grid_width / 2, grid_width / 2, text=str(i), font=self.helv)
            self.main_canvas.create_text(i * grid_width + grid_width / 2, grid_width / 2 + grid_width, text=str(i % 12),
                                    font=self.helv)
        for motif in self.motif_list:
            motif.gui_update_canvas()

        self.root.after(50, self.update_gui)

    def import_from_file(self, filename):

        read_object = None
        if filename:
            with open(filename, 'r') as f:
                s = f.read()
                read_object = json.loads(s)

        if read_object:
            self.motif_list = []
            widget_list = self.slider_frame.winfo_children()
            for w in widget_list:
                w.destroy()

            for o in read_object:
                m = Motif()
                m.scale = o['scale']
                m.translation = o['translation']
                m.color = o['color']
                m.points = o['points']
                self.motif_list.append(m)
                m.gui_initialize(self.slider_frame, self.main_canvas)


    def export_to_file(self, filename):
        e = []
        for m in self.motif_list:
            d = {}
            d['points'] = m.points
            d['scale'] = m.scale
            d['translation'] = m.translation
            d['color'] = m.color

            e.append(d)

        if filename:
            with open(filename, 'w') as f:
                json.dump(e, f, indent=4)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = Trio()
    app.root.after(50, app.update_gui)
    app.root.mainloop()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
