import tkMessageBox
from Tkinter import *
from tkFont import Font

# App is the main class for gui. It takes in the tkinter root in order for the gui panel to show
# and several method parameters to connect the gui with server class and data class
# The method parameters are passed in from server class, each match with another
# call back in data class
# The method parameters include Flip Horizontaly, Enable Face, Enable Motiion,
# Reduce Noise, Blur Value, Blob Size, Motion Thread, and Merge Distance
class App():
    def __init__(self, root, flip, face, motion, reduce, blur, blob, mthread, merge): #, motionCallback, blurCallback, etc etc):
        self.root= root
        self.flip = flip
        self.face = face
        self.motion = motion
        self.reduce = reduce
        self.blur = blur
        self.blob = blob
        self.motion_thread = mthread
        self.merge = merge
        self.main_panel = MainPanel(self.root)
        self.upper_bar = UpperBar(self.root, self.main_panel, self.flip)
        self.slider = Slider(self.root, self.main_panel, self.face, self.motion,
                             self.reduce, self.blur, self.blob, self.motion_thread, self.merge)
        self.menu = MenuBar(self.root, self.main_panel)

    def update(self):
        self.root.update()

# MainPanel creates the gui frame
class MainPanel():
    def __init__(self, root):
        self.root = root
        self.custom_font = Font(family="Verdana", size=14)
        self.root.option_add("*Font", self.custom_font)
        self.root.title("iHart GUI Demo")
        self.default_width = 320
        self.default_height = 340
        self.ratio = 1
        self.frame_dimensions()
        # self.set_icon(os.path.join(os.getcwd(), "logo"))
        # root.wm_iconbitmap('logo_10_10.ico')
        # root.wm_title('iHart GUI Demo')
        self.root.resizable(0, 0)

    # def set_icon(self, iconName):
    #
    #     windowSystem = self.root.call("tk", "windowingsystem")
    #     if windowSystem == "win32":  # Windows
    #         print "hi"
    #         iconName += ".ico"
    #     elif windowSystem == "x11":  # Unix
    #         print "hi"
    #         iconName = "@" + iconName + ".xbm"
    #     if windowSystem != "aqua" and os.path.isfile(iconName):
    #         print(iconName)
    #         self.master.iconbitmap(iconName)
    #         # self.master.wm_iconbitmap(iconName) also works

    def frame_dimensions(self):
        self.frame_width = int(self.default_width * self.ratio)
        self.frame_height = int(self.default_height * self.ratio)
        self.root.geometry("%dx%d+%d+%d" % ((self.frame_width, self.frame_height) + (200,200)))

# UpperBar includes the Flip Horizontable button
class UpperBar():
    def __init__(self, root, main_panel, flip):
        self.root = root
        self.board = main_panel
        self.flip_call_back = flip
        # logo = PhotoImage(file="logo.gif")
        # logo = logo.subsample(10, 10)
        # logoLabel = Label(root, image=logo)

        # logoLabel.grid()
        # Style().configure('green/black.TLabel', foreground='green', background='black')

        flip_frame = Frame(self.root)
        flip_frame.pack(side="top", fill="x", expand=False)
        # flip_frame.config(width=self.board.default_width, height=2)
        flip_frame.grid(row=0, columnspan=10, sticky=W + E, pady=5)
        flipButton = Button(flip_frame, text="Flip Horizontal", command = self.flip)
        flipButton.pack()

    # When flip horizontal button is clicked, it will call the call back method in server
    # which will then call the actual method in data class
    def flip(self):
        self.flip_call_back()

# Slider includes enable face and enable motion check boxes,
# and buttons and slide bars for other functions
class Slider():
    def __init__(self, root, main_panel, face, motion, reduce, blur, blob, mthread, merge):

        self.root = root
        self.board = main_panel
        self.face_cb = face
        self.motion_cb = motion
        self.reduce_cb = reduce
        self.blur_cb = blur
        self.blob_cb = blob
        self.mthread_cb = mthread
        self.merge_cb = merge

        # each checkbox matches to a BooleanVar
        # the initial value for enable face is false, and for enable motion is true
        self.FaceVar = BooleanVar()
        self.FaceVar.set(False)
        self.MotionVar = BooleanVar()
        self.MotionVar.set(True)

        checkbox_frame = Frame(self.root)
        checkbox_frame.grid(row=2, column=0, columnspan=2,
                            sticky=W + E + S)  # WE - stretch it horizontally but leave it centered vertically.

        self.enableface_checkbox = Checkbutton(checkbox_frame, text="Enable Face", variable=self.FaceVar, onvalue=True, offvalue=False, command  = self.enable_face)
        self.enablemotion_checkbox = Checkbutton(checkbox_frame, text="Enable Motion", variable=self.MotionVar, onvalue=True,
                                            offvalue=False, command = self.enable_motion)
        # self.enablemotion_checkbox.trace()

        self.enableface_checkbox.grid(row=0, column=0, sticky=N + S + W, padx=15)
        self.enablemotion_checkbox.grid(row=0, column=2, sticky=N + S + E)

        bottom_frame = Frame(self.root)
        bottom_frame.grid(row=3, column=0, columnspan=3, sticky=W + E + S)

        self.create_buttons(bottom_frame)

    # When user click on the checkbox, it will call the method in server class, which will then call
    # the actual functioning class in data class to enable or disable face
    def enable_face(self):
        self.face_cb()

    def enable_motion(self):
        self.motion_cb()

    # each of them can be adjust by both the slide bar and buttons
    #  - ======== +
    # create 5 rows of that for each of them
    def create_buttons(self, frame):

        self.label_text = ["Reduce Noise", "Blur Value", "Blob Size", "Motion Thread", "Merge Distance"]
        self.to_value = [20, 20, 20, 50, 10]
        num = self.label_text.__len__()
        self.inputs = [None for _ in range(num)]
        self.labels = [None for _ in range(num)]
        self.scales = [None for _ in range(num)]
        self.increases = [None for _ in range(num)]
        self.decreases = [None for _ in range(num)]
        self.vars = [0] *num

        for i in range(num):
            self.vars[i] = IntVar()
        initial = 10
        for r in range(num):
            self.labels[r] = Label(frame, text=self.label_text[r])
            self.inputs[r] = 10
            #, command = lambda r=r: self.update(r)
            # callback should be 0 for reduce noice(the first trackbar), but print out the trackbar value!!!!
            self.scales[r] = Scale(frame, from_=0, to_=self.to_value[r], variable=self.vars[r], orient=HORIZONTAL,command=lambda r=r: self.call_back(r))
            self.increases[r] = Button(frame, text="+", command=lambda r=r: self.increase_this(r))
            self.decreases[r] = Button(frame, text="-", command=lambda r=r: self.decrease_this(r))
            self.labels[r].grid(row=r + 3, column=0, sticky=W + N, ipadx=10, ipady=15)
            self.decreases[r].grid(row=r + 3, column=1, columnspan=3, sticky=N + S + E, ipady=13)
            self.scales[r].grid(row=r + 3, column=4, sticky=N)
            self.increases[r].grid(row=r + 3, column=5, columnspan=3, sticky=N + S + E, ipady=13)
            initial -= 1



        # self.root.bind('<Left>', self.keyDecrease)
        # self.root.bind('<Right>', self.keyIncrease)

    # def keyIncrease(self, event):
    #     self.increase_this(0)


    # def keyDecrease(self, event):
    #     self.decrease_this(0)

    # call_back takes in a number indicating which row that the user makes a change to
    # ex. row 0 = reduce noise
    # then based on the row number, get the value of that function and call the corresponding
    # methods in server class (which then call methods in data class to modify cv)
    def call_back(self, i):
        print "in call back"
        print i
        # reduce noise
        if i==0:
            self.reduce_cb(self.inputs[i])
        # blur value
        if i==1:
            self.blur_cb(self.inputs[i])
        # blob size
        if i==2:
            self.blob_cb(self.inputs[i])
        # motion thread
        if i==3:
            self.mthread_cb(self.inputs[i])
        # merge distance
        if i==4:
            self.merge_cb(self.inputs[i])

    # Increase the value when increase buttons are clicked
    # It takes in a parameter indicating which row/ function that user is modifying
    # Increase the value by 1 if it is within the range, and do nothing if it exceeds the range
    # then call call_back method
    def increase_this(self, i):
        # print "click button"
        self.inputs[i] = self.scales[i].get()
        input  = self.inputs[i]
        if (input + 1 <= self.to_value[i]):
            self.inputs[i] = input + 1
        self.scales[i].set(self.inputs[i])
        self.call_back(i)

    # Decrease the value when decrease buttons are clicked
    # It takes in a parameter indicating which row/ function that user is modifying
    # Decrease the value by 1 if it is within the range, and do nothing if it exceeds the range
    # then call call_back method
    def decrease_this(self, r):
        self.inputs[r] = self.scales[r].get()
        input = self.inputs[r]
        if (input - 1 >= 0):
            self.inputs[r] = input - 1
        self.scales[r].set(self.inputs[r])
        self.call_back(r)

    def getValues(self):
        for i in range(5):
            print self.label_text[i]
            print self.scales[i].get()

class MenuBar():
    def __init__(self, root, main_panel):
        self.root = root
        self.board = main_panel
        self.menubar = Menu(self.root)

        # file menu that contains open, save, create presents option
        fileMenu = Menu(self.menubar, tearoff=0)
        # fileMenu.add_command(label="Open Preset", command = self.load_present)
        # fileMenu.add_command(label="Save Preset", command = self.save_present)
        # fileMenu.add_command(label="Create Preset", command = self.create_present)
        self.menubar.add_cascade(label="File", menu=fileMenu)

        # about menu that contains About option and Info option
        aboutMenu = Menu(self.menubar, tearoff=0)
        aboutMenu.add_command(label="About", command=self.about)
        aboutMenu.add_command(label="Info", command=self.info)
        self.menubar.add_cascade(label="About", menu=aboutMenu)

        #
        # # #preference menu
        # prefMenu = Menu(self.menubar, tearoff=0)
        # prefMenu.add_command(label="Larger Font", command=self.board.larger_font)
        # prefMenu.add_command(label="Smaller Font", command=self.board.smaller_font)
        # self.menubar.add_cascade(label="Preference", menu=prefMenu)

        # quit menu
        quitMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Quit", menu=quitMenu)
        quitMenu.add_command(label="Quit!", command=self.quit)

        self.root.config(menu=self.menubar)

    def about(self):
        tkMessageBox.showinfo("About", "GUI demo for iHart 2017")

    def info(self):
        tkMessageBox.showinfo("Info", "GUI demo for iHart 2017")

    def quit(self):
        self.Quitbuttonvar.configure(state="disabled")
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def about(self):
        tkMessageBox.showinfo("About", "GUI demo for iHart 2017")

    def info(self):
        tkMessageBox.showinfo("Info", "GUI demo for iHart 2017")

    def quit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def load_present(self):
        pass

    def save_present(self):
        pass

    def create_present(self):
        pass


"""This is the code that is executed by python when we run this .py file"""
# if __name__ == '__main__':
#     root = Tk()  # creates an instance --> what we call the root window
#     App(root)
#     root.mainloop()
