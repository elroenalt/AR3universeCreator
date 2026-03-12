import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

default_json = None
definitions = None
dimensionProperties = []
dimensions_names = []

class dimension_Frame(ctk.CTkFrame):
    def __init__(self, master,properties,refrence, **kwargs):
        super().__init__(master, **kwargs)
        self.refrence = refrence + [0]
        self.properties = properties
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.buttons = []
        self.rows = 0
        for propertie in list(self.properties[0].items()):
            open = ctk.CTkButton(master=self, text=propertie[0],corner_radius=0,fg_color="#5F5F5F",hover_color="#505050", 
                                   command=lambda ref=list(self.refrence): self.click(ref))
            self.buttons.append((open,refrence))
            open.grid(sticky="ew",row=self.rows, column=1, padx=(20,0), pady=0)
            self.rows += 1
            self.refrence[1] += 1
    def reload(self):
        print("reload")
    def edit(self):
        print("edit")
    def delete(self):
        print("delete")
        app.leftFrame.dimesnion_Buttons[self.refrence[0]].destroy()
        app.leftFrame.dimesnion_Buttons[self.refrence[0]] = None
        dimensionProperties[self.refrence[0]] = None
        dimensions_names[self.refrence[0]] = None
        app.leftFrame.dimension_Frames[self.refrence[0]] = None
        self.destroy()
    def click(self,ref):
        app.rightFrame.display_refrence(ref)
        if self.properties[0]["name"] != app.focus:
            viewer = app.rightFrame.body_viewer
            scale = ((1/6)* viewer.old_size) / (self.properties[0]["earthRadiusMultiplier"] * viewer.AU_to_earthRadius )
            viewer.scale = scale
            x, y = 0, 0
            if not self.properties[0]["parentDimensionId"]:
                pos = self.properties[0]["position"]
                x = pos["x"]
                y = pos["y"]
            else:
                # get body pos
                body = self.properties[1]
                parent = dimensionProperties[dimensions_names.index(body)][0]
                while parent["parentDimensionId"]:
                    x -= parent["orbitalDistanceToParent"]
                    parent = dimensionProperties[dimensions_names.index(f'{parent["parentDimensionId"]["namespace"]}_{parent["parentDimensionId"]["path"]}')][0]
                else:
                    x += parent["position"]["x"]
                    y += parent["position"]["y"]
            viewer.camera = [x,y]
            viewer.draw()
            app.focus = self.properties[0]["name"]
        
    def toggle(self):
        if self.winfo_viewable():
            self.grid_remove() 
        else:
            self.grid()

class leftFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(self, text="Universe",font=("Arial", 18, "bold"))
        self.label.grid(row=0, column=0, padx=0, pady=10)
        self.grid_columnconfigure(0, weight=1)

        self.rows = 1 
        self.dimension_Frames = []
        self.dimesnion_Buttons = []
        self.refrence = [0]

        for dimension in dimensionProperties:
            self.load_dimension(dimension)
        
    def load_dimension(self,dimension):
        dimension = dimension
        frame = dimension_Frame(master=self, properties=dimension,refrence=self.refrence.copy())
        heading_frame = ctk.CTkFrame(self,width=100)

        heading_frame.grid_columnconfigure(0, weight=7, uniform="buttons")
        heading_frame.grid_columnconfigure((1, 2, 3), weight=1, uniform="buttons")

        open_btn = ctk.CTkButton(
            master=heading_frame, 
            text=dimension[0]["name"], 
            command=frame.toggle,
            font=("Arial", 16, "bold"),
            corner_radius=0,
            fg_color="#07052b",
            hover_color="#0b0840",
            anchor="w",
            width=0 
        )
        btn_params = {
            "master": heading_frame,
            "font": ("Arial", 16, "bold"),
            "corner_radius": 0,
            "fg_color": "#07052b",
            "hover_color": "#0b0840",
            "width": 40
        }
        edit = ctk.CTkButton(**btn_params, text="🖉", command=frame.edit)
        delete = ctk.CTkButton(**btn_params, text="🗑", command=frame.delete)
        reload = ctk.CTkButton(**btn_params, text="🗘", command=frame.reload)

        open_btn.grid(row=0, column=0, sticky="nsew")
        edit.grid(row=0, column=1, sticky="nsew")
        delete.grid(row=0, column=2, sticky="nsew")
        reload.grid(row=0, column=3, sticky="nsew")
        
        heading_frame.grid(sticky="ew", row=self.rows, column=0)

        self.rows += 1
        frame.grid(sticky="nsew",row=self.rows, column=0, padx=0, pady=0)
        frame.grid_remove() 
        self.rows += 1

        self.dimension_Frames.append(frame)
        self.dimesnion_Buttons.append(heading_frame)
        self.refrence[0] += 1

    def add_dimension(self,name,file_name):
        properties = default_json.copy()
        properties["name"] = name
        properties["dimensionId"]["path"] = file_name
        dimensionProperties.append((properties,name))
        dimensions_names.append(name)
        
        self.load_dimension((properties,name))

class rightFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=8)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew")

        self.name = ctk.CTkLabel(self.container, text="property name", font=("Arial", 16, "bold"))
        self.name.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        
        self.definition = ctk.CTkLabel(self.container, text="property definition", justify="left")
        self.definition.grid(row=1, column=0, padx=10, pady=0, sticky="ew")

        self._parent_canvas = self._parent_canvas
        self.bind("<Configure>", self._on_resize)

        self.cur_setting = 0
        self.settings = []

        #single input type
        frame_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_input.grid(row=3, column=1, padx=20, pady=5, sticky="ew")
        user_input_var = ctk.StringVar()
        user_input = ctk.CTkEntry(frame_input, textvariable=user_input_var)
        user_input_var.trace_add("write",lambda *args: self.edit(user_input_var))
        user_input.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        frame_input.grid_remove()
        self.settings.append((frame_input,user_input))
        
        #switch input type
        frame_switch = ctk.CTkFrame(self, fg_color="transparent")
        frame_switch.grid(row=3, column=1, padx=20, pady=5, sticky="ew")
        switch_var = ctk.StringVar(value="on")
        switch = ctk.CTkSwitch(frame_switch, text="True/False", command=lambda: self.edit(switch_var),variable=switch_var, onvalue=True, offvalue=False)
        switch.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        frame_switch.grid_remove()
        self.settings.append((frame_switch,switch))

        #vec3 input type
        vec3s = []
        frame_input3 = ctk.CTkFrame(self, fg_color="transparent")
        frame_input3.grid(row=3, column=1, padx=20, pady=5, sticky="ew")
        for i in range(3):
            axis_label = ("x", "y", "z")[i]
            axis = ctk.CTkLabel(frame_input3, text=axis_label, font=("Arial", 16, "bold"))
            axis.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            input_var = ctk.StringVar()
            input_field = ctk.CTkEntry(frame_input3, textvariable=input_var)
            input_var.trace_add("write", lambda *args, i=i, var=input_var: self.edit(value=var, i=i))
            input_field.grid(row=i, column=1, padx=20, pady=2, sticky="ew")
            vec3s.append(input_field)
        frame_input3.grid_remove()
        self.settings.append((frame_input3, vec3s))

        #path input type
        frame_path_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_path_input.grid(row=3, column=1, padx=2, pady=5, sticky="ew")
        user_path_input_var1 = ctk.StringVar()
        user_path_input1 = ctk.CTkEntry(frame_path_input, textvariable=user_path_input_var1)
        user_path_input_var1.trace_add("write",lambda *args: self.edit(user_path_input_var1,0))
        user_path_input1.grid(row=0, column=0, padx=(0,1), pady=5, sticky="ew")
        user_path_input_var2 = ctk.StringVar()
        user_path_input2 = ctk.CTkEntry(frame_path_input, textvariable=user_path_input_var2)
        user_path_input_var2.trace_add("write",lambda *args: self.edit(user_path_input_var2,1))
        user_path_input2.grid(row=0, column=1, padx=(1,0), pady=5, sticky="ew")
        frame_path_input.grid_remove()
        self.settings.append((frame_path_input,user_path_input1,user_path_input2))

        #body viewer
        self.body_viewer = body_Display(self,height=50)
        self.body_viewer.grid(row=4,column=1,sticky="s",pady=(5,10),padx=5)
        self.body_viewer.draw()
        
    def edit(self,value,i=0):
        if value.get() == "":
            return
        value = value.get() 
        match self.dataType:
            case "str" | "int" | "float":
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                if not value: return
                dimensionProperties[self.refrence[0]][0][key] = str(value) if self.dataType == "str" else int(float(value)) if self.dataType == "int" else float(value) 
            case "boolean":
                value = True if value == "1" else False
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                dimensionProperties[self.refrence[0]][0][key] = value
            case "Vec3":
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                dimensionProperties[self.refrence[0]][0][key][("x","y","z")[i]] = float(value)
            case "path":
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                dimensionProperties[self.refrence[0]][0][key][("namespace","path")[i]] = str(value)
            case __:
                print("not yet added")

    def _on_resize(self, event):
        available_width = self.container.winfo_width() - 100
        if available_width > 0:
            self.definition.configure(wraplength=available_width)

    def display_refrence(self,refrence):
        property = list(dimensionProperties[refrence[0]][0].items())[refrence[1]]
        definition = list(definitions[property[0]].values()) if property[0] in definitions else "eather not any possible property or not yet implemented into this editor"
        self.name.configure(text=property[0])
        self.definition.configure(text=definition[0])
        self.settings[self.cur_setting][0].grid_remove()
        self.dataType = definition[1]
        self.refrence = refrence
        match definition[1]:
            case "str" | "int" | "float":
                self.cur_setting = 0
                item = self.settings[0]
                item[1].delete("0", "end")
                item[1].insert("0", property[1])
                item[0].grid()
            case "boolean":
                self.cur_setting = 1
                item = self.settings[1]
                if property[1]: item[1].select()
                else: item[1].deselect()
                item[0].grid()
            case "Vec3":
                self.cur_setting = 2
                item = self.settings[2]
                for i in range(0,3):
                    item[1][i].delete("0", "end")
                    item[1][i].insert("0", str(list(property[1].values())[i]))
                item[0].grid()
            case "path":
                self.cur_setting = 3
                item = self.settings[3]
                for i in range(1,3):
                    item[i].delete("0", "end")
                    item[i].insert("0", str(list(property[1].values())[i-1]))
                item[0].grid()
            case __:
                print("not yet added")

class body_Display(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#000000", highlightthickness=0, **kwargs)
        self.old_size = 0
        self.bind("<Configure>", self.resize)
        self.speed = 3
        self.camera = [0, 0]
        self.scale = 2
        self.AU_to_earthRadius = 1/2343
        self.orbit_grad = ("#b6c60e","#4d2911","#5A5A5A")
        self.bind("<Button-1>", self.zoom)
        self.bind("<Button-3>", self.zoom)
        self.draw()

    def zoom(self, event):
        if event.num == 1:
            self.scale *= 2
        elif event.num == 3:
            self.scale *= 0.5
        self.draw()

    def move_cam(self,event = None):
        key = event.keysym.lower()
        if key == 'button-5':
            self.scale += 1
        elif key == 'up':
            self.camera[1] -= self.speed/self.scale
        elif key == 'down':
            self.camera[1] += self.speed/self.scale
        elif key == 'left':
            self.camera[0] -= self.speed/self.scale
        elif key == 'right':
            self.camera[0] += self.speed/self.scale
        self.draw()

    def draw(self):
        color = self.orbit_grad[0]
        self.delete("all")
        cx = self.winfo_width() / 2
        cy = self.winfo_height() / 2
        for dimension in dimensionProperties:
            if not dimension: continue
            parent_count = 0
            x = 0
            y = 0
            dimension_props = dimension[0]
            raw_radius = dimension_props["earthRadiusMultiplier"] * self.scale * self.AU_to_earthRadius
            radius = max(1, raw_radius+1) 
            if not dimension_props["parentDimensionId"]:
                pos = dimension_props["position"]
                x = pos["x"]
                y = pos["y"]
            else:
                # get body pos
                body = dimension[1]
                parent = dimensionProperties[dimensions_names.index(body)][0]
                while parent["parentDimensionId"]:
                    parent_count += 1
                    x -= parent["orbitalDistanceToParent"]
                    parent = dimensionProperties[dimensions_names.index(f'{parent["parentDimensionId"]["namespace"]}_{parent["parentDimensionId"]["path"]}')][0]
                else:
                    x += parent["position"]["x"]
                    y += parent["position"]["y"]
                #draw orbit
                orbit_radius = dimensionProperties[dimensions_names.index(body)][0]["orbitalDistanceToParent"]
                parentX = (x - self.camera[0]+ orbit_radius) * self.scale + cx
                parentY = (y - self.camera[1]) * self.scale + cy
                self.create_oval(parentX-orbit_radius*self.scale, parentY-orbit_radius*self.scale,
                                 parentX+orbit_radius*self.scale, parentY+orbit_radius*self.scale, 
                                 fill="", outline="#ffffff",width=1,dash=(1, 4))
            color = self.orbit_grad[parent_count]
            x = (x - self.camera[0]) * self.scale + cx
            y = (y - self.camera[1]) * self.scale + cy
            self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
            
    def resize(self, event):
        if event.width != self.old_size:
            self.old_size = event.width
            self.configure(height=event.width)
            self.draw()

class App(ctk.CTk,TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

        self.geometry("600x400")
        self.body_focus = None
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("AR3 dimensionCreator")
        self.leftFrame = leftFrame(master=self)
        self.leftFrame.grid(row=0, column=0, sticky="nsew",padx=10,pady=20)
        self.leftFrame.drop_target_register(DND_FILES)
        self.leftFrame.dnd_bind('<<Drop>>',self.handle_drop)
        
        self.rightFrame = rightFrame(master=self)
        self.rightFrame.grid(row=0, column=1, sticky="nsew",padx=10,pady=20)
        self.bind("<KeyPress>", self.rightFrame.body_viewer.move_cam)
    def handle_drop(self,event):
        file_path = event.data
        file_path = file_path.strip('{}')
        loadDrop(file_path)
def loadDrop(file_path):
    global dimensions_names
    if ".json" in file_path:
        dimension = (loadFile(os.path.join(file_path)),file_path.removesuffix(".json"))
        dimensionProperties.append(dimension)
        app.leftFrame.load_dimension(dimension)
    else:
        dP_names = os.listdir(file_path)
        for path in dP_names:
            dimension = (loadFile(os.path.join(file_path,path)),path.removesuffix(".json"))
            dimensionProperties.append(dimension)
            app.leftFrame.load_dimension(dimension)
    dimensions_names = [dim[1] for dim in dimensionProperties]
    app.rightFrame.body_viewer.draw()
def loadFile(path):
    file = open(path)
    json_con = json.load(file)
    file.close()
    return json_con

app = App()
default_json = loadFile('default.json')
definitions = loadFile('def.json')
app.mainloop()