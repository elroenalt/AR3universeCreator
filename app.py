import customtkinter as ctk
import jsonLoader
import tkinter as tk
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")
definitions = {
    "position": {
        "definition": "?",
        "varStruc": "Vec3"
    },
    "hasCustomSky": {
        "definition": "decides wether to render a custom sky based on alter values?",
        "varStruc": "boolean"
    },
    "gravitationalMultiplier": {
        "definition": "the amount of gravity with 1 being earths gravity",
        "varStruc": "float"
    },
    "earthRadiusMultiplier": {
        "definition": "the planets radius relative to earthes radius",
        "varStruc": "float"
    },
    "rotationAxis": {
        "definition": "the axis the celestrial body curently rotates around itself",
        "varStruc": "Vec3"
    },
    "seaLevel": {
        "definition": "current sea level (vanilla setting = 63)",
        "varStruc": "int"
    },
    "originalSeaLevel": {
        "definition": "original level of the sea (vanilla setting = 63)",
        "varStruc": "int"
    },
    "generateStructures": {
        "definition": "wether the planet should generate any structure",
        "varStruc": "boolean"
    },
    "parentDimensionId": {
        "definition": "what celestrial body the celestrial body schould rotate around",
        "varStruc": "path"
    },
    "orbitAxis": {
        "definition": "the orbit the celestrial body curently takes around its parent dimension",
        "varStruc": "Vec3"
    },
    "orbitalDistanceToParent": {
        "definition": "the distance beetween the parent celestrial body and itself in AU (astronomical unit = distance beetween sun and earth)",
        "varStruc": "float"
    },
    "orbitalBaseOffsetDegrees": {
        "definition": "?",
        "varStruc": "float"
    },
    "dayTimeReference": {
        "definition": "the celestrial body it takes refrence from to calculate day and night time",
        "varStruc": "path"
    },
    "texture": {
        "definition": "the texture used for the space rendered body model",
        "varStruc": "path"
    },
    "skyColor": {
        "definition": "the normal color of the sky in RGB/255",
        "varStruc": "Vec3"
    },
    "cloudColor": {
        "definition": "the normal color of the clouds in RGB/255",
        "varStruc": "Vec3"
    },
    "fogColor": {
        "definition": "the base color of the fog in RGB/255",
        "varStruc": "Vec3"
    },
    "sunRiseColor": {
        "definition": "the normal color of the sunrise in RGB/255",
        "varStruc": "Vec3"
    },
    "reflectiveTextureTintColor": {
        "definition": "which color schould be reflected how much in RGB/255",
        "varStruc": "Vec3"
    },
    "emissiveColor": {
        "definition": "the color that the body radiates outwards in RGB/255",
        "varStruc": "Vec3"
    },
    "hasRingSystem": {
        "definition": "wether the celestrial body has rings",
        "varStruc": "boolean"
    },
    "radiationIntensity": {
        "definition": "intensity on which it radiats (emissiv color and co.)",
        "varStruc": "float"
    },
    "atmosphereDensity": {
        "definition": "the bodies atmospheric density, temporary value later to be replaced with gas calculation",
        "varStruc": "float"
    },
    "latitude_len": {
        "definition": "how much you have to move in z direction to 'go around the planet' 0% = equator, 25% = South Pole, 50% = equator again, 75% = North Pole",
        "varStruc": "int"
    },
    "targetDayLength": {
        "definition": "negative or zero for a fixed length",
        "varStruc": "int"
    },
    "dayTime": {
        "definition": "?",
        "varStruc": "int"
    },
    "isKnown": {
        "definition": "whether the player still has to discover the celestrial body in the observatory",
        "varStruc": "boolean"
    },
    "canVisit": {
        "definition": "whether the player can visit the celestrial body with a rocket",
        "varStruc": "boolean"
    },
    "artifactItem": {
        "definition": "WIP wether the palyer has to provide an artifact to discover the celestrial body",
        "varStruc": "null"
    },
    "biomePreset": {
        "definition": "wich biome mix the celestrial body schould use (defined in config AR biome preser)",
        "varStruc": "str (json file name)"
    },
    "name": {
        "definition": "name of the planet",
        "varStruc": "str"
    },
    "type": {
        "definition": "what type the of celestrial body it is eg PLANET",
        "varStruc": "str"
    },
    "dimensionID": {
        "definition": "the id used for the dimension eg minecraft, overword structure for existing dimensions to link and adv_rocketry, name for creating a new one",
        "varStruc": "path"
    }
}
dimensionProperties = jsonLoader.getdimensionProperties()
dimensions_names = [dimension[1] for dimension in dimensionProperties]
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
        for propertie in list(self.properties.items()):
            button = ctk.CTkButton(master=self, text=propertie[0],corner_radius=0,fg_color="#5F5F5F",hover_color="#505050", 
                                   command=lambda ref=list(self.refrence): self.click(ref))
            self.buttons.append((button,refrence))
            button.grid(sticky="ew",row=self.rows, column=1, padx=20, pady=0)
            self.rows += 1
            self.refrence[1] += 1
        
    def click(self,ref):
        app.rightFrame.display_refrence(ref)
        if self.properties["name"] != app.focus:
            viewer = app.rightFrame.body_viewer
            position = self.properties["position"]
            viewer.camera = [position["x"],position["y"]]
            viewer.draw()
            app.focus = self.properties["name"]
        
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
        refrence = [0]

        for dimension in dimensionProperties:
            dimension = dimension[0]
            frame = dimension_Frame(master=self, properties=dimension,refrence=refrence.copy())
            
            button = ctk.CTkButton(font=("Arial", 16, "bold"),master=self, text=dimension["name"], command=frame.toggle,corner_radius=0,fg_color="#07052b",hover_color="#0b0840")
            
            button.grid(sticky="ew",row=self.rows, column=0, padx=0, pady=0)

            self.rows += 1
            frame.grid(sticky="nsew",row=self.rows, column=0, padx=0, pady=0)
            frame.grid_remove() 
            self.rows += 1

            self.dimension_Frames.append(frame)
            self.dimesnion_Buttons.append(button)
            refrence[0] += 1

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
        frame_input.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        user_input_var = ctk.StringVar()
        user_input = ctk.CTkEntry(frame_input, textvariable=user_input_var)
        user_input_var.trace_add("write",lambda *args: self.edit(user_input_var))
        user_input.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        frame_input.grid_remove()
        self.settings.append((frame_input,user_input))
        
        #switch input type
        frame_switch = ctk.CTkFrame(self, fg_color="transparent")
        frame_switch.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        switch_var = ctk.StringVar(value="on")
        switch = ctk.CTkSwitch(frame_switch, text="True/False", command=lambda: self.edit(switch_var),variable=switch_var, onvalue=True, offvalue=False)
        switch.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        frame_switch.grid_remove()
        self.settings.append((frame_switch,switch))

        #vec3 input type
        vec3s = []
        frame_input3 = ctk.CTkFrame(self, fg_color="transparent")
        frame_input3.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        for i in range(3):
            axis_label = ("x", "y", "z")[i]
            axis = ctk.CTkLabel(frame_input3, text=axis_label, font=("Arial", 16, "bold"))
            axis.grid(row=i, column=0, padx=10, pady=(10, 5), sticky="w")
            input_var = ctk.StringVar()
            input_field = ctk.CTkEntry(frame_input3, textvariable=input_var)
            input_var.trace_add("write", lambda *args, i=i, var=input_var: self.edit(value=var, i=i))
            input_field.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
            vec3s.append(input_field)
        frame_input3.grid_remove()
        self.settings.append((frame_input3, vec3s))
        
        #body viewer
        self.body_viewer = body_Display(self,height=50)
        self.body_viewer.grid(row=4,column=1,sticky="s",pady=20,padx=20)
        self.body_viewer.draw()
        
    def edit(self,value,i=0):
        print("change: " + self.dataType,value)
        match self.dataType:
            case "str" | "int" | "float":
                value = value.get()
                key = list(dimensionProperties[0][0][self.refrence[0]].items())[self.refrence[1]][0]
                if not value: return
                dimensionProperties[self.refrence[0]][0][key] = str(value) if self.dataType == "str" else int(float(value)) if self.dataType == "int" else float(value) 
            case "boolean":
                value = True if value.get() == "1" else False
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                dimensionProperties[self.refrence[0]][0][key] = value
            case "Vec3":
                print("---")
                value = value.get()
                key = list(dimensionProperties[self.refrence[0]][0].items())[self.refrence[1]][0]
                print(key,i)
                dimensionProperties[self.refrence[0]][0][key][("x","y","z")[i]] = float(value)
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
                item[1].bind()
                item[0].grid()
            case "boolean":
                self.cur_setting = 1
                item = self.settings[1]
                item[1].configure(state="enabled" if property[1] else "disabled")
                item[0].grid()
            case "Vec3":
                self.cur_setting = 2
                item = self.settings[2]
                for i in range(0,3):
                    item[1][i].delete("0", "end")
                    item[1][i].insert("0", str(list(property[1].values())[i]))
                item[0].grid()
            case __:
                pass
class body_Display(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#000000", highlightthickness=0, **kwargs)
        self.old_size = 0
        self.bind("<Configure>", self.resize)
        self.speed = 3
        self.camera = [0, 0]
        self.scale = 0.5
        self.AU_to_earthRadius = 1/2343
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
        self.delete("all")
        cx = self.winfo_width() / 2
        cy = self.winfo_height() / 2
        for dimension in dimensionProperties:
            x = 0
            y = 0
            dimension_props = dimension[0]
            raw_radius = dimension_props["earthRadiusMultiplier"] * self.scale * self.AU_to_earthRadius
            radius = max(0.1, raw_radius) 
            if not dimension_props["parentDimensionId"]:
                pos = dimension_props["position"]
                x = pos["x"]
                y = pos["y"]
            else:
                body = dimension[1]
                parent = dimensionProperties[dimensions_names.index(body)][0]
                while parent["parentDimensionId"]:
                    x -= parent["orbitalDistanceToParent"]
                    parent = dimensionProperties[dimensions_names.index(f'{parent["parentDimensionId"]["namespace"]}_{parent["parentDimensionId"]["path"]}')][0]
                else:
                    x += parent["position"]["x"]
                    y += parent["position"]["y"]
            x = (x - self.camera[0]) * self.scale + cx
            y = (y - self.camera[1]) * self.scale + cy
            self.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#ffffff", outline="")
                    
                    
    def resize(self, event):
        if event.width != self.old_size:
            self.old_size = event.width
            self.configure(height=event.width)
            self.draw()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        self.body_focus = None
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("AR3 dimensionCreator")
        self.leftFrame = leftFrame(master=self)
        self.leftFrame.grid(row=0, column=0, sticky="nsew",padx=10,pady=20)
        
        self.rightFrame = rightFrame(master=self)
        self.rightFrame.grid(row=0, column=1, sticky="nsew",padx=10,pady=20)
        self.bind("<KeyPress>", self.rightFrame.body_viewer.move_cam)

app = App()
app.mainloop()