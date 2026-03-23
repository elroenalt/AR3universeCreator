import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import os
from pathlib import Path

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

default_json = None
definitions = None
dimensionProperties = {}

class dimension_Frame(ctk.CTkFrame):
    def __init__(self, master,properties,refrence, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.refrence = refrence
        self.dimension = properties
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)

        self.load()

    def load(self):
        self.buttons = []
        self.rows = 0
        for propertie in list(self.dimension["properties"].items()):
            open = ctk.CTkButton(master=self, text=propertie[0],corner_radius=0,fg_color="#5F5F5F",hover_color="#505050", 
                                   command=lambda ref=(self.refrence,self.rows): self.click(ref))
            open.grid(sticky="ew",row=self.rows, column=1, padx=(20,0), pady=0)

            self.buttons.append({
                "open":open,
                "id":(self.refrence,self.rows)
                })
            self.rows += 1  

    def reload(self):
        dimension = default_json.copy()

        for prop in dimension:
            if prop in self.dimension["properties"].keys():
                dimension[prop] = self.dimension["properties"][prop]

        self.dimension["properties"] = dimension
        dimensionProperties[self.refrence]["properties"] = dimension
        dimensionProperties[self.refrence]["dimensionId"] = dimension["dimensionId"].values()
        self.master.dimension_Frames[self.refrence]["file_name"].configure(text="_".join(dimension["dimensionId"].values()) )
        self.master.dimension_Frames[self.refrence]["open_btn"].configure(text=dimension["name"])
        for button in self.buttons:
            button["open"].destroy()
        
        self.load()
    def open_edit(self):
        app.toplevel_window.open_edit(self.refrence)

    def delete(self):
        dimensionProperties.pop(self.refrence)
        self.master.reload()

    def toggle_view(self):
        self.dimension["render"] = not self.dimension["render"]
        dimensionProperties[self.refrence]["render"] = self.dimension["render"]
        app.leftFrame.dimension_Frames[self.refrence]["toggle_view"].configure(text="☑" if self.dimension["render"] else "☐")
        app.rightFrame.body_viewer.draw()
    def fucus_viewer(self):
        viewer = app.rightFrame.body_viewer
        scale = int(((1/6)* int(viewer.winfo_width())) / (self.dimension["properties"]["earthRadiusMultiplier"] * viewer.AU_to_earthRadius ))
        viewer.scale = scale
        x, y = 0, 0
        if not self.dimension["properties"]["parentDimensionId"]:
            pos = self.dimension["properties"]["position"]
            x = pos["x"]
            y = pos["y"]
            viewer.camera = [x,y]
            viewer.draw()
        else:
            # get body pos
            try:
                names = [path for path in dimensionProperties.keys()]
                parent = self.dimension["properties"]
                while parent["parentDimensionId"]:
                    if not self.dimension["properties"]["parentDimensionId"] in [dim["path"] for dim in dimensionProperties]:
                        return
                    x -= parent["orbitalDistanceToParent"]
                    parent = dimensionProperties[f'{parent["parentDimensionId"]["namespace"]}_{parent["parentDimensionId"]["path"]}']["properties"]
                else:
                    x += parent["position"]["x"]
                    y += parent["position"]["y"]
                viewer.camera = [x,y]
                viewer.draw()
                print("Hi")
            except Exception as e:
                print(f"Viewer Error: {e}")
    def click(self,ref):
        app.rightFrame.display_refrence(ref)
        self.fucus_viewer()
        app.focus = self.dimension["properties"]["name"]

    def toggle(self):
        if self.winfo_viewable():
            self.grid_remove() 
        else:
            self.grid()

class leftFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.btn_params = {
            "font": ("Arial", 16, "bold"),
            "corner_radius": 0,
            "fg_color": "transparent",
            "hover_color": "#0b0840",
            "width": 40
        }

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=0, pady=5, sticky="ew")
        
        self.grid_columnconfigure(0, weight=1) 
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.edit_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.edit_frame.grid(row=0, column=0, sticky="ew") 
        self.edit_frame.grid_columnconfigure(0, weight=1)

        self.download = ctk.CTkButton(self.edit_frame, text="🖫", font=("Arial", 18, "bold"), 
                                       command=download, corner_radius=0, fg_color="transparent", 
                                       hover=False, width=40)
        self.create = ctk.CTkButton(self.edit_frame, text="+", font=("Arial", 18, "bold"), 
                                     command=master.toplevel_window.open_create, corner_radius=0, fg_color="transparent", 
                                     hover=False, width=40)
        
        self.download.grid(row=0, column=1, padx=2)
        self.create.grid(row=0, column=2, padx=(2, 10))

        self.title = ctk.CTkLabel(self.top_frame, text="Universe", font=("Arial", 22, "bold"))
        self.title.grid(row=1, column=0, padx=15, pady=(0, 5))

        self.rows = 1 
        self.dimension_Frames = {}
        self.refrence = 0
    def reload(self):
        for frame in self.dimension_Frames:
            for item in frame.values():
                item.destroy()
        self.rows = 1 
        self.refrence = 0
        frame = []
        for dimension in dimensionProperties.items():
            self.load_dimension(dimension)
        app.rightFrame.body_viewer.draw()
    def load_dimension(self,dimension):
        path = dimension[0]
        self.refrence = path
        dimension = dimension[1]

        frame = dimension_Frame(master=self, properties=dimension,refrence=self.refrence)
        heading_frame = ctk.CTkFrame(self,width=100,fg_color="#07052b",corner_radius=0)
        heading_frame.grid_columnconfigure(0, weight=7, uniform="buttons")
        heading_frame.grid_columnconfigure((1, 2, 3), weight=1, uniform="buttons")

        elements = {
            "frame": frame,
            "heading_frame": heading_frame,
            "delete": ctk.CTkButton(command=frame.delete, **self.btn_params, master=heading_frame, text="🗑"),
            "reload": ctk.CTkButton(command=frame.reload, **self.btn_params, master=heading_frame, text="🗘"),
            "toggle_view": ctk.CTkButton(command=frame.toggle_view, **self.btn_params, master=heading_frame, text="☑", ),
            "file_name": ctk.CTkLabel(master=heading_frame, text=dimension["path"], font=("Arial", 10, "bold"),fg_color=self.btn_params["fg_color"],anchor="w"),
            "open_btn": ctk.CTkButton(command=frame.toggle, master=heading_frame, text=dimension["properties"]["name"], font=self.btn_params["font"],corner_radius=0,fg_color=self.btn_params["fg_color"],hover_color=self.btn_params["hover_color"],anchor="w",width=0 )
        }
        

        elements["open_btn"].grid(row=0, column=0, sticky="nsew")
        elements["file_name"].grid(row=1, column=0, sticky="nsew",padx=(10,0))
        elements["toggle_view"].grid(row=0, column=1, sticky="nsew")
        elements["delete"].grid(row=0, column=3, sticky="nsew")
        elements["reload"].grid(row=0, column=4, sticky="nsew")

        elements["heading_frame"].grid(sticky="ew", row=self.rows, column=0)

        self.rows += 1
        elements["frame"].grid(sticky="nsew",row=self.rows, column=0, padx=0, pady=0)
        elements["frame"].grid_remove() 

        self.dimension_Frames[path] = elements

        self.rows += 1

    def add_dimension(self,file_name):
        properties = default_json.copy()
        properties["name"] = file_name
        properties["dimensionId"]["path"] = file_name
        path = file_name
        dimension = {
            "properties": properties,
            "render": True,
            "path": path
        }
        dimensionProperties[path] = dimension
        self.load_dimension(dimension)

class rightFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        #body viewer
        self.body_viewer_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_viewer_container.grid(row=0, column=0,sticky="nsew")
        self.body_viewer_container.grid_columnconfigure(0, weight=1)
        
        self.body_viewer = Display(self.body_viewer_container)
        self.body_viewer.grid(row=0,column=0,sticky="nsew")
        self.body_viewer.draw()

        #body editor
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew")

        self.name = ctk.CTkLabel(self.container, text="property name", font=("Arial", 16, "bold"))
        self.name.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        
        self.definition = ctk.CTkLabel(self.container, text="property definition", justify="left")
        self.definition.grid(row=1, column=0, padx=10, pady=0, sticky="ew")

        self._parent_canvas = self._parent_canvas
        self.bind("<Configure>", self._on_resize)

        self.settings = []

        #single input type
        frame_input = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_input.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        user_input_var = ctk.StringVar()
        user_input_var.trace_add("write",lambda *_, v=user_input_var: self.edit(v))
        user_input = ctk.CTkEntry(frame_input, textvariable=user_input_var)
        user_input.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        frame_input.grid_remove()

        single_input = {
            "frame": frame_input,
            "var": user_input_var,
            "input": user_input
        }
        self.settings.append(single_input)
        
        #switch input type
        frame_switch = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_switch.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        switch_var = ctk.BooleanVar(value=True)
        switch = ctk.CTkSwitch(frame_switch, text="True/False", command=lambda: self.edit(switch_var),variable=switch_var)
        switch.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        frame_switch.grid_remove()

        switch_input = {
            "frame": frame_switch,
            "var": switch_var,
            "input": switch
        }
        self.settings.append(switch_input)

        #vec3 input type
        frame_input3 = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_input3.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        vec3_input = {
            "frame": frame_input3,
            "vars": [],
            "inputs": [],
            "labels": []
        }
        for i in range(3):
            axis = ctk.CTkLabel(frame_input3, text=("x", "y", "z")[i], font=("Arial", 16, "bold"))
            axis.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            vec3_input["labels"].append(axis)

            input_var = ctk.StringVar()
            input_var.trace_add("write",lambda *args, i=i,value=input_var: self.edit(value=value, i=i))

            input_field = ctk.CTkEntry(frame_input3, textvariable=input_var)
            vec3_input["vars"].append(input_var)

            input_field.grid(row=i, column=0, padx=20, pady=2, sticky="ew")
            vec3_input["inputs"].append(input_field)

        frame_input3.grid_remove()
        self.settings.append(vec3_input)

        #path input type
        frame_path_input = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_path_input.grid(row=5, column=0, padx=2, pady=5, sticky="ew")

        user_path_input_var1 = ctk.StringVar()
        user_path_input_var1.trace_add("write",lambda *args, v=user_path_input_var1: self.edit(v, 0))
        user_path_input1 = ctk.CTkEntry(frame_path_input, textvariable=user_path_input_var1)
        user_path_input1.grid(row=0, column=0, padx=(0,1), pady=5, sticky="ew")

        user_path_input_var2 = ctk.StringVar()
        user_path_input_var2.trace_add("write",lambda *args, v=user_path_input_var2: self.edit(v, 1))
        user_path_input2 = ctk.CTkEntry(frame_path_input, textvariable=user_path_input_var2)
        user_path_input2.grid(row=0, column=1, padx=(1,0), pady=5, sticky="ew")

        frame_path_input.grid_remove()
        path_input = {
            "frame": frame_path_input,
            "vars": [user_path_input_var1,user_path_input_var2],
            "inputs": [user_path_input1,user_path_input2]
        }
        self.settings.append(path_input)
        
    def edit(self, value, i=0):
        value = value.get() 
        key = self.property[0]
        dataType = self.data[1]
        
        # FIX: self.refrence is now a string, not a list/tuple
        current_key = self.refrence[0] if isinstance(self.refrence, tuple) else self.refrence

        match dataType:
            case "str" | "int" | "float":
                if not value: return
                processed_value = str(value) if dataType == "str" else int(float(value)) if dataType == "int" else float(value)
                dimensionProperties[current_key]["properties"][key] = processed_value
            case "boolean":
                dimensionProperties[current_key]["properties"][key] = value
            case "Vec3":
                dimensionProperties[current_key]["properties"][key][("x","y","z")[i]] = float(value) if value else 0.0
            case "path":
                if key in ("parentDimensionId","dayTimeReference"):
                    switch_val = self.settings[1]["var"].get()
                    if switch_val and not self.property[1]:
                        pass
                    elif not switch_val:
                        dimensionProperties[self.refrence[0]]["properties"][key] = None
                        value = None
                dimensionProperties[current_key]["properties"][key][("namespace","path")[i]] = str(value)

        match key:
            case "name":
                app.leftFrame.dimension_Frames[current_key]["open_btn"].configure(text=value)
            
            case "dimensionId":
                dim_id = dimensionProperties[current_key]["properties"]["dimensionId"]
                new_key = f"{dim_id['namespace']}_{dim_id['path']}"
                
                if new_key != current_key:
                    data = dimensionProperties.pop(current_key)
                    data["path"] = new_key
                    dimensionProperties[new_key] = data
                    
                    ui_elements = app.leftFrame.dimension_Frames.pop(current_key)
                    ui_elements["file_name"].configure(text=new_key)
                    ui_elements["frame"].load()
                    app.leftFrame.dimension_Frames[new_key] = ui_elements
                    ui_elements["frame"].refrence = new_key
                    self.refrence = new_key

    def _on_resize(self, event):
        return
        available_width = self.container.winfo_width() - 100
        if available_width > 0:
            self.definition.configure(wraplength=available_width)

    def display_refrence(self,refrence):
        property = list(dimensionProperties[refrence[0]]["properties"].items())[refrence[1]]
        definition = list(definitions[property[0]].values()) if property[0] in definitions else "eather not any possible property or not yet implemented into this editor"
        self.name.configure(text=property[0])
        self.definition.configure(text=definition[0])

        for setting in self.settings:
            setting["frame"].grid_remove()

        self.data = definition
        self.refrence = refrence
        self.property = property

        match definition[1]:
            case "str" | "int" | "float":
                try:
                    item = self.settings[0]
                    item["var"].set(property[1])
                    item["frame"].grid()
                except:
                    item["var"].set("0.0")
            case "boolean":
                try:
                    item = self.settings[1]
                    item["var"].set(property[1])
                    item["frame"].grid()
                except:
                    item["var"].set(True)
            case "Vec3":
                self.cur_setting = 2
                item = self.settings[2]
                values = list(property[1].values())
                for i in range(0,3):
                    try:
                        item["vars"][i].set(str(values[i]))
                    except:
                        item["vars"][i].set("0.0")
                item["frame"].grid()
            case "path":
                if property[0] in ("parentDimensionId","dayTimeReference"):
                    value = property[1] is not None
                    toggle_item = self.settings[1]
                    toggle_item["var"].set(value)
                    toggle_item["frame"].grid()
                    if not value: return
                item = self.settings[3]
                values = list(property[1].values())
                for i in range(0,2):
                    try:
                        item["vars"][i].set(str(values[i]))
                    except:
                        item["vars"][i].set("None")

                item["frame"].grid()
            case __:
                print("not yet added")

class Display(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#000000", highlightthickness=0, **kwargs)
        self.old_width = 0
        #self.bind("<Configure>", self.resize)
        self.speed = 3
        self.camera = [0, 0]
        self.scale = 3
        self.AU_to_earthRadius = 1/2343
        self.orbit_col = ("#b6c60e","#4d2911","#5A5A5A")
        self.bind("<Button-1>", self.zoom)
        self.bind("<Button-3>", self.zoom)
        self.mode = "draw"
        self.focus_color = False
        self.ring_width = 0.05
        self.ring_dist = 0.1
    def switch_mode(self,mode = "draw"):
        self.mode = mode
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
    def draw_universe(self):
        self.cx = self.winfo_width() / 2
        self.cy = self.winfo_height() / 2
        for dimension in dimensionProperties.values():
            if dimension and dimension["render"]:
                self.draw_body(dimension)
        
    def draw_body(self,dimension):
        parent_count = 0
        x = 0
        y = 0
        dimension_props = dimension["properties"]
        raw_radius = dimension_props["earthRadiusMultiplier"] * self.scale * self.AU_to_earthRadius
        radius = max(1, raw_radius+1) 
        if not dimension_props["parentDimensionId"]:
            pos = dimension_props["position"]
            x = pos["x"]
            y = pos["y"]
        else:
            # get body pos
            names = dimensionProperties.keys()
            parent = dimension["properties"]
            while parent["parentDimensionId"]:
                parent_count += 1
                try:
                    x -= parent["orbitalDistanceToParent"]
                except:
                    print("no orbitalDistanceToParent given")
                    continue
                try:
                    parent = dimensionProperties[f'{parent["parentDimensionId"]["namespace"]}_{parent["parentDimensionId"]["path"]}']["properties"]
                except:
                    print("parent not found")
                    return
            else:
                try:
                    x += parent["position"]["x"]
                    y += parent["position"]["y"]
                except:
                    print("no position x or y given")
            #draw orbit
            try: 
                orbit_radius = dimension["properties"]["orbitalDistanceToParent"]
                parentX = (x - self.camera[0]+ orbit_radius) * self.scale + self.cx
                parentY = (y - self.camera[1]) * self.scale + self.cy
                self.create_oval(parentX-orbit_radius*self.scale, parentY-orbit_radius*self.scale,
                                parentX+orbit_radius*self.scale, parentY+orbit_radius*self.scale, 
                                fill="", outline="#ffffff",width=1,dash=(1, 4))
            except:
                print("no orbitalDistanceToParent given")
        color = self.orbit_col[parent_count]
        x = (x - self.camera[0]) * self.scale + self.cx
        y = (y - self.camera[1]) * self.scale + self.cy
        self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        if dimension["properties"]["hasRingSystem"]: 
            gap = max(2, self.ring_dist * self.scale* self.AU_to_earthRadius / radius)
            thickness = max(1, self.ring_width * self.scale* self.AU_to_earthRadius / radius)
            ring_r = radius + gap
            self.create_oval(x - radius - ring_r, y - radius - ring_r, 
                            x + radius + ring_r, y + radius + ring_r, 
                            fill="", outline="gray", width=thickness)
    def draw_color(self):
        if not self.focus_color: return
        values1 = [v/(1+v) for v in self.focus_color.values()]
        values2 = [v**1/2.2 for v in values1]
        value = "#"+"".join([f"{int(v*255):02x}" for v in values2])
        self.configure(bg=value)
    def draw(self):
        self.configure(bg="#000000")
        self.delete("all")
        match self.mode:
            case "draw":
                self.draw_universe()
            case "color":
                self.draw_color()
            case __:
                print("not a valid type")
            
    def resize(self, event):
        return
        current_width = self.master.winfo_width()
        
        if current_width != self.old_width:
            self.configure(width=current_width)
            self.old_width = current_width

class App(ctk.CTk,TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

        self.geometry("600x500")
        self.body_focus = None
        
        self.toplevel_window = popUpWindow()
        self.toplevel_window.focus()
        self.toplevel_window.withdraw()

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
        self.rightFrame.body_viewer.draw()

def loadDrop(file_path):
    try:
        if ".json" in file_path:
            dimension = loadFile(os.path.join(file_path))
            path = Path(file_path).name.removesuffix(".json")
            x = {
                "properties": dimension,
                "render": True,
                "path": path
            }
            dimensionProperties[path] = x
            app.leftFrame.load_dimension((path,x))
        else:
            dP_names = os.listdir(file_path)
            for path in dP_names:
                dimension = loadFile(os.path.join(file_path,path))
                path = path.removesuffix(".json")
                x = {
                    "properties": dimension,
                    "render": True,
                    "path": path
                }
                dimensionProperties[path] = x
                app.leftFrame.load_dimension((path,x))
        app.rightFrame.body_viewer.draw()
    except:
        print("error during import")
def loadFile(path):
    file = open(path)
    json_con = json.load(file)
    file.close()
    return json_con
def download():
    downloads_path = str(Path.home() / "Downloads")
    folder_name = "dimensionProperties"
    folder_path = os.path.join(downloads_path, folder_name)
    i = 0
    while os.path.exists(folder_path):
        i += 1
        folder_name = f"dimensionProperties{i}"
        folder_path = os.path.join(downloads_path, folder_name)
    else:
        os.makedirs(folder_path)
    dimensions = [dimension for dimension in dimensionProperties if dimension]
    for dimension in dimensions:
        if not dimension: continue;
        file_full_path = os.path.join(folder_path,dimension["path"]+".json")
        with open(file_full_path, "w") as f:
            json.dump(dimension["properties"], f, indent=4)

class popUpWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x200")
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.label = ctk.CTkLabel(self, text="ToplevelWindow")
        self.label.pack(padx=20, pady=(20,5))

        self.user_Input = ctk.StringVar()
        self.entry = ctk.CTkEntry(self,textvariable=self.user_Input)
        self.entry.pack(padx=20, pady=5)

        self.focusX = -1
        self.buttons = {
            "create":ctk.CTkButton(self,text="create",command=lambda: app.leftFrame.add_dimension(self.user_Input.get())),
            "edit":ctk.CTkButton(self,text="edit",command=lambda: app.leftFrame.dimension_Frames[self.focusX]["frame"].edit(self.user_Input))
        }
        self.type = -1
    def open_create(self):
        for button in self.buttons.values():
            button.pack_forget()
        self.buttons["create"].pack()
        self.label.configure(text="creating a new dimension")
        self.user_Input.set("adv_rocketry_")
        self.buttons["create"].configure(text="create")
        self.deiconify()
        self.focus()
        self.type = 0
    def open_edit(self,id):
        self.focusX = id
        for button in self.buttons.values():
            button.pack_forget()
        self.buttons["edit"].pack()
        self.label.configure(text=f'editing {dimensionProperties[id]["properties"]["name"]}')
        self.user_Input.set(dimensionProperties[id]["path"])
        self.deiconify()
        self.focus()
        self.type = 1
    def close(self):
        self.withdraw()
app = App()
default_json = loadFile('assets/default.json')
definitions = loadFile('assets/def.json') 
app.mainloop()