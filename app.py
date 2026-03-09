import customtkinter as ctk
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")
definitions = {
    "position": {
        "definition": "pos of any celestrial object in AU relative to earth?",
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
        "definition": "the planets radius relative to earthes size",
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
        "varStruc": "dictonary with namespace and path"
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
        "varStruc": "dictonary with namespace and path"
    },
    "texture": {
        "definition": "the texture used for the space rendered body model",
        "varStruc": "dictonary with namespace and path"
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
        "definition": "the id used for the dimension eg minecraft, overword structure for existing dimensions to link and adv_rocketry, name for creating a new one"
    }
}
dimensionProperties = [{
    "position": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
    },
    "hasCustomSky": True,
    "gravitationalMultiplier": 1.0,
    "earthRadiusMultiplier": 1.0,
    "name": "Venus",
    "rotationAxis": {
        "x": 0.2,
        "y": 1.0,
        "z": 0.0
  }},{
    "position": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
    },
    "hasCustomSky": True,
    "gravitationalMultiplier": 1.0,
    "earthRadiusMultiplier": 1.0,
    "name": "Earth",
    "rotationAxis": {
        "x": 0.2,
        "y": 1.0,
        "z": 0.0
  }}]
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
            button = ctk.CTkButton(master=self, text=propertie[0],fg_color="#5F5F5F",hover_color="#505050", command=lambda ref=list(self.refrence): app.rightFrame.display_refrence(ref))
            self.buttons.append((button,refrence))
            button.grid(sticky="ew",row=self.rows, column=1, padx=20, pady=10)
            self.rows += 1
            self.refrence[1] += 1

    def toggle(self):
        if self.winfo_viewable():
            self.grid_remove() 
        else:
            self.grid()
class leftFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(self, text="Universe",font=("Arial", 18, "bold"))
        self.label.grid(row=0, column=0, padx=20, pady=10)
        
        self.grid_columnconfigure(0, weight=1)

        self.rows = 1 
        self.dimension_Frames = []
        self.dimesnion_Buttons = []
        refrence = [0]

        for dimension in dimensionProperties:
            frame = dimension_Frame(master=self, properties=dimension,refrence=refrence.copy())
            
            button = ctk.CTkButton(font=("Arial", 16, "bold"),master=self, text=dimension["name"], command=frame.toggle,corner_radius=0,fg_color="#07052b",hover_color="#0b0840")
            button.grid(sticky="ew",row=self.rows, column=0, padx=20, pady=10)

            self.rows += 1
            frame.grid(sticky="nsew",row=self.rows, column=0, padx=20, pady=10)
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
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew")

        self.name = ctk.CTkLabel(self.container, text="property name", font=("Arial", 16, "bold"))
        self.name.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.definition = ctk.CTkLabel(self.container, text="property definition", justify="left")
        self.definition.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self._parent_canvas = self._parent_canvas
        self.bind("<Configure>", self._on_resize)

        self.cur_setting = 0
        self.settings = []
        frame_input = ctk.CTkFrame(self, fg_color="transparent")
        frame_input.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        user_input = ctk.CTkEntry(frame_input, placeholder_text="Type something here...")
        user_input.bind("<Return>",lambda event, ui=user_input: self.edit(ui))
        user_input.unbind()
        user_input.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        frame_input.grid_remove()
        self.settings.append((frame_input,user_input))
        
        frame_switch = ctk.CTkFrame(self, fg_color="transparent")
        frame_switch.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        switch_var = ctk.StringVar(value="on")
        switch = ctk.CTkSwitch(frame_switch, text="True/False", command=self.edit,
                                 variable=switch_var, onvalue=True, offvalue=False)
        switch.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        frame_switch.grid_remove()
        self.settings.append((frame_switch,switch))

        vec3s = []
        frame_input3 = ctk.CTkFrame(self, fg_color="transparent")
        frame_input3.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        for i in range(0,3):
            axis = ctk.CTkLabel(frame_input3, text=("x","y","z")[i], font=("Arial", 16, "bold"))
            axis.grid(row=i, column=0, padx=10, pady=(10, 5), sticky="w")
            input = ctk.CTkEntry(frame_input3, placeholder_text="Type something here...")
            input.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
            vec3s.append(input)
        frame_input3.grid_remove()
        self.settings.append((frame_input3,vec3s))
        
    def edit(self,element):
        match self.dataType:
            case "str" | "int" | "float":
                value = element.get()
                key = list(dimensionProperties[self.refrence[0]].items())[self.refrence[1]][0]
                print(value,key)
                print(dimensionProperties[self.refrence[0]][key])
                dimensionProperties[self.refrence[0]][key] = value
    def _on_resize(self, event):
        available_width = self.container.winfo_width() - 100
        if available_width > 0:
            self.definition.configure(wraplength=available_width)

    def display_refrence(self,refrence):
        property = list(dimensionProperties[refrence[0]].items())[refrence[1]]
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



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("AR3 dimensionCreator")

        self.leftFrame = leftFrame(master=self)
        self.leftFrame.grid(row=0, column=0, sticky="nsew",padx=10,pady=20)
        
        self.rightFrame = rightFrame(master=self)
        self.rightFrame.grid(row=0, column=1, sticky="nsew",padx=10,pady=20)

app = App()
app.mainloop()