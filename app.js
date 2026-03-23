<<<<<<< HEAD

import JSZip from 'https://esm.sh/jszip@3.10.1';
let definitions_json;
let default_json;
const dimension_container = document.querySelector('#hirachy')
let dimensions = {
}
let editor;
let display; 
async function loadGameData() {
    try {
        const response1 = await fetch('assets/default.json');
        const data1 = await response1.json();
        default_json = data1
        
        const response2 = await fetch('assets/def.json');
        const data2 = await response2.json();
        editor = new Editor()
        display = new Display()
        definitions_json = data2

        document.querySelector('#download').addEventListener('click', () => {
            downloadAllDimensions()
        })
        let ids = 0
        document.querySelector('#cerate').addEventListener('click', () => {
            const json = structuredClone(default_json); 
            
            const name = `Planet${String(ids)}`;
            json.name = name;
            json.dimensionId.path = name;
            const key = `${json.dimensionId.namespace}_${name}`;
            dimensions[key] = new Dimension(key, json);
            
            ids += 1;
            display.draw_universe();
        });
        resizeCanvas()
        
    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}
function resizeCanvas() {
    const canvas = document.querySelector('#canvas');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    display.draw_universe()
}
class Dimension {
    constructor(file_path,properties) {
        this.file_path = file_path
        this.properties = properties
        this.render = true
        
        this.load()
    }
    centerPlanet() {
        let x = 0;
        let y = 0;
        let props = this.properties;

        const scale = ((1/6)* display.width/ (this.properties["earthRadiusMultiplier"] * display.AU_to_earthRadius ))
        display.scale = scale

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"]) {
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);
        }
        display.camera = [x,y]
        display.draw_universe()
    }
    load() {
        const container = document.createElement('div')
        container.className = "dimension_container"

        this.html = {
            "name": Object.assign(document.createElement('div'), {
                className: "dimension_name",
                textContent: this.properties["name"]
            }),
            "view": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_edit",
                textContent: "☑"
            }),
            "reload": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_reload",
                textContent: "🗘"
            }),
            "remove": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_remove",
                textContent: "🗑"
            }),
            "file_path": Object.assign(document.createElement('div'), {
                className: "dimension_file_path",
                textContent: this.file_path
            })
        }
        for (let item of Object.values(this.html)) {
            container.appendChild(item);
        }
        this.html["remove"].addEventListener('click',() => {
            this.html["container"].remove()
            this.html["properties_frame"].remove()
            delete dimensions[this.file_path]
            display.draw_universe()
            })
        this.html["reload"].addEventListener('click',() => {
            this.html["properties_frame"].remove()
            this.load_properties()
            })
        this.html["view"].addEventListener('click',() => {
            this.html["view"].textContent = this.html["view"].textContent == "☑" ? "☐" : "☑"
            this.render = !this.render
            display.draw_universe()
            })
        this.html["file_path"].addEventListener('click', () => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            this.toggle_properties()
            })
        this.html["name"].addEventListener('click', () => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            this.toggle_properties()})
        this.html["container"] = container
        dimension_container.appendChild(container)
        this.load_properties()
    }

    load_properties() {
        const properties_frame = Object.assign(document.createElement('div'), {
            className: "dimension_properties",
        })
        this.html["properties"] = []
        for (let item of Object.entries(this.properties)) {
            const element = Object.assign(document.createElement('div'), {
                className: "dimension_property",
                textContent: item[0]
            })
            element.addEventListener("click", () => {
                editor.focus(this.file_path,item[0])
                display.camera = [0,0]
            })
            properties_frame.appendChild(element)
            this.html["properties"].push(element)
        }
        dimension_container.appendChild(properties_frame)
        properties_frame.style.display = "none"
        this.html["properties_frame"] = properties_frame
    }
    toggle_properties() {
        const display = this.html["properties_frame"]
        if (display.style.display === 'none') {
            display.style.display = "block"
        }else {
            display.style.display = "none"
        }
    }
}
async function downloadAllDimensions() {
    const zip = new JSZip();

    for (const planet of Object.values(dimensions)) {
        const name = planet.file_path
        const fileName = `${name}.json`;
        
        const fileContent = JSON.stringify(planet.properties, null, 4);
        
        zip.file(fileName, fileContent);
    }

    const content = await zip.generateAsync({ type: "blob" });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(content);
    link.download = "dimensions_export.zip"; 
    
    document.body.appendChild(link);
    link.click();

    setTimeout(() => {
        URL.revokeObjectURL(link.href);
        link.remove();
    }, 200);
}
class Display {
    constructor() {
        this.tooltip = document.querySelector('#tooltip');
        this.planets = []
        this.canvas = document.querySelector('#canvas')
        this.ctx = this.canvas.getContext("2d");
        this.focus = null
        this.old_width = 0
        this.speed = 3
        this.camera = [0,0]
        this.scale = 10
        this.AU_to_earthRadius = 1/2343
        this.orbit_col = ["#b6c60e","#4d2911","#5A5A5A","#b6c60e","#4d2911","#5A5A5A"]
        this.mode = "draw"
        this.focus_color = false
        this.ring_width = 0.05
        this.ring_dist = 0.1
        this.mouse_focus = null
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            let isFocus = false
            for(let planet of this.planets) {
                const dx = planet.pos[0] - x
                const dy = planet.pos[1] - y
                const d = Math.sqrt(dx**2+dy**2)
                if (d < planet.radius) {
                    isFocus = true
                    this.tooltip.style.display = "block"
                    const Tx = e.clientX + 15; 
                    const Ty = e.clientY + 15;
                    this.tooltip.style.transform = `translate(${Tx}px, ${Ty}px)`;
                    this.tooltip.textContent = planet.file_path
                    console.log(planet.file_path)
                    this.mouse_focus = planet
                }
            }
            if (!isFocus) {
                this.tooltip.style.display = 'none';
            }
        });
        this.canvas.addEventListener('click', () => {
            if (this.mouse_focus) {
                console.log("x")
                editor.focus(this.mouse_focus.file_path,"position")
                editor.focus(this.mouse_focus.file_path,"position")
                if (dimensions[this.mouse_focus.file_path].html.properties_frame.style.display != "block") {
                    dimensions[this.mouse_focus.file_path].html.properties_frame.style.display = "block"
                }
                dimensions[this.mouse_focus.file_path].centerPlanet()
            }
        });
        this.canvas.addEventListener('mouseout', () => {
            this.tooltip.style.display = 'none';
        });
        this.canvas.addEventListener('keydown', (event) => {
            const key = event.key.toLowerCase();
            const moveStep = this.speed / this.scale;
            switch (key) {
                case 'arrowup':
                    this.camera[1] -= moveStep
                    break;
                case 'arrowdown':
                    this.camera[1] += moveStep
                    break;
                case 'arrowleft':
                    this.camera[0] -= moveStep
                    break;
                case 'arrowright':
                    this.camera[0] += moveStep
                    break;
                case 'o':
                    this.scale *= 1.1
                    break;
                case 'p':
                    this.scale /= 1.1
                    break;
            }
            this.draw_universe()
        });
    }
    draw_color(color) {
        this.planets = []
        this.mouse_focus = null
        this.width = this.canvas.width
        this.height = this.canvas.height
        this.ctx.clearRect(0,0,this.width   ,this.height)
        const SDR = [color.x/(1+color.x),color.y/(1+color.y),color.z/(1+color.z)]
        const RGB = [SDR[0]*255,SDR[1]*255,SDR[2]*255]
        this.ctx.fillStyle = `rgb(${RGB[0]},${RGB[1]},${RGB[2]})`
        this.ctx.fillRect(0,0,this.width,this.height)
    }
    draw_universe() {
        this.planets = []
        this.mouse_focus = null
        this.width = this.canvas.width
        this.height = this.canvas.height
        this.cx = this.width/ 2
        this.cy = this.height / 2
        this.ctx.clearRect(0,0,this.width   ,this.height)
        for (let dimension of Object.values(dimensions)){
            if (dimension.render) {
                this.draw_body(dimension)
            }
        }
    }
    draw_body(dim) {
        let parent_count = 0;
        let x = 0;
        let y = 0;
        let props = dim.properties;

        const raw_radius = (props["earthRadiusMultiplier"] || 1) * this.scale * this.AU_to_earthRadius;
        const radius = Math.max(1, raw_radius + 1);

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"] && parent_count < 10) {
                parent_count += 1;
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);

            const orbX = (x - this.camera[0]+props["orbitalDistanceToParent"]) * this.scale + this.cx;
            const orbY = (y - this.camera[1]) * this.scale + this.cy;
            const orbit_radius = (props["orbitalDistanceToParent"] || 0) * this.scale;
            
            
            this.ctx.beginPath();
            //this.ctx.setLineDash([5, 5]);
            this.ctx.arc(orbX, orbY, orbit_radius, 0, 2 * Math.PI);
            this.ctx.strokeStyle = "#ffffff";
            this.ctx.stroke();
        }
        const screenX = (x - this.camera[0]) * this.scale + this.cx;
        const screenY = (y - this.camera[1]) * this.scale + this.cy;
        const color = this.orbit_col[parent_count] || "#ffffff";

        this.ctx.beginPath();
        this.ctx.setLineDash([]);
        this.ctx.arc(screenX, screenY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();

        this.planets.push({
            "file_path": `${props.dimensionId.namespace}_${props.dimensionId.path}`,
            "radius": radius,
            "pos": [screenX,screenY]
        })
    }
}
class Editor {
    constructor() {
        this.info_html = {
            "name": document.querySelector('#editor-name'),
            "description": document.querySelector('#editor-description'),
            "type": document.querySelector('#editor-type')
        }
        this.inputs = [
            {
                "frame": document.querySelector('#switch-row'),
                "input": document.querySelector('#switch-input')
            },
            {
                "frame": document.querySelector('#text-row'),
                "input": document.querySelector('#text-input')
            },
            {
                "frame": document.querySelector('#vec3-row'),
                "inputs": [
                    document.querySelector('#vec1-input'),
                    document.querySelector('#vec2-input'),
                    document.querySelector('#vec3-input'),
                ]
            },
            {
                "frame": document.querySelector('#selection-row'),
                "input": document.querySelector('#selection-input'),
                "datalist": document.querySelector('#datalist')
            },
            {
                "frame": document.querySelector('#path-row'),
                "inputs": [
                    document.querySelector('#namespace-input'),
                    document.querySelector('#path-input')
                ]
            }
        ]
        this.inputs.forEach((item, i) => {
            if (!item.input && !item.inputs) console.error(`Input ${i} is NULL!`);
        });
        this.activeDim = null
        this.activeProp = null
        this.setupListeners()
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
    }
    setupListeners() {
        this.inputs[0]["input"].addEventListener('change', (e) => {
            if (this.activeDim && this.activeProp) {
                dimensions[this.activeDim].properties[this.activeProp] = e.target.checked;
                dimensions[this.activeDim].centerPlanet()
            }
        });
        this.inputs[1]["input"].addEventListener('input', (e) => {
            if (this.activeDim && this.activeProp) {
                let val = e.target.value;
                const type = definitions_json[this.activeProp]["varStruc"];
                dimensions[this.activeDim].properties[this.activeProp] = type == "int" || type == "floar" ? Number(val) : String(val);
                if (this.activeProp == "name" ){
                    dimensions[this.activeDim].html["name"].textContent = String(val)
                }
                dimensions[this.activeDim].centerPlanet()
            }
        });
        const axes = ["x", "y", "z"];
        this.inputs[2]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                if (this.activeDim && this.activeProp) {
                    const axis = axes[i];
                    dimensions[this.activeDim].properties[this.activeProp][axis] = parseFloat(e.target.value) || 0.0;
                    dimensions[this.activeDim].centerPlanet()
                }
            });
        });
        const paths = ["namespace","path"];
        this.inputs[4]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                if (this.activeDim && this.activeProp) {
                    const path = paths[i];
                    dimensions[this.activeDim].properties[this.activeProp][path] = String(e.target.value)
                    if (this.activeProp == "dimensionId" ){
                        const dimension = dimensions[this.activeDim]
                        const file_path = [dimension.properties[this.activeProp]["namespace"],dimension.properties[this.activeProp][path]].join("_")
                        delete dimensions[this.activeDim];
                        dimension.file_path = file_path
                        dimension.html.file_path.textContent = file_path
                        this.activeDim  = file_path
                        dimensions[file_path] = dimension
                    }
                    dimensions[this.activeDim].centerPlanet()

                }
            });
        });
        this.inputs[3]["input"].addEventListener('input', (e) => {
            if (!this.activeDim || !this.activeProp) return;
            const newValue = e.target.value;
            const currentData = dimensions[this.activeDim].properties[this.activeProp];
            if (newValue && Object.keys(dimensions).includes(newValue)) {
                dimensions[this.activeDim].properties[this.activeProp] = dimensions[newValue].properties["dimensionId"];
            } else {
                dimensions[this.activeDim].properties[this.activeProp] = newValue ? newValue : null 
            }
            dimensions[this.activeDim].centerPlanet()
        });
    }
    focus(dim,prop) {
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
        if (!Object.keys(definitions_json).includes(prop)) {
            return
        }
        const info = definitions_json[prop]
        this.info_html["name"].textContent = prop
        this.info_html["description"].textContent = info["definition"]
        this.info_html["type"].textContent = info["varStruc"]
        this.activeDim = dim
        this.activeProp = prop

        let val = dimensions[dim].properties[prop]
        
        if (info["extra"] == "color") {
            display.draw_color(val)
        }else {
            display.draw_universe()
        }
        
        switch(info["varStruc"]) {
            case "float":
            case "int":
            case "str": {
                this.inputs[1]["frame"].style.display = "block";
                console.log(this.inputs[1]["input"])
                this.inputs[1]["input"].value = (val === null) ? "" : String(val);
                break;}
            case "boolean":{
                this.inputs[0]["frame"].style.display = "block";
                this.inputs[0]["input"].checked = val;
                break;}
            case "Vec3":{
                this.inputs[2]["frame"].style.display = "block";
                for (let i = 0; i < 3; i++) {
                    let vali = val[["x","y","z"][i]]
                    this.inputs[2]["inputs"][i].value = vali
                }
                break;}
            case "path":{
                if (info["extra"] == "selection") {
                    this.inputs[3]["frame"].style.display = "block";
                    this.inputs[3]["input"].value = val ? [val["namespace"],val["path"]].join("_") : "" 
                    this.inputs[3]["datalist"].innerHTML = "";
                    const option = document.createElement('option');
                    option.value = null;
                    this.inputs[3]["datalist"].appendChild(option);
                    Object.keys(dimensions).forEach(path => {
                        const option = document.createElement('option');
                        option.value = path;
                        this.inputs[3]["datalist"].appendChild(option);
                    });
                }else {
                    this.inputs[4]["frame"].style.display = "block";
                    this.inputs[4]["inputs"][0].value = val["namespace"]
                    this.inputs[4]["inputs"][1].value = val["path"]
                }
                break;}
            default:
                console.log("not added " + info["varStruc"])
        }
    }
}
window.addEventListener('dragenter', (e) => {
    e.preventDefault();
    document.body.classList.add('dragging');
});
window.addEventListener('dragover', (e) => {
    e.preventDefault();
});
window.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
        document.body.classList.remove('dragging');
    }
});
window.addEventListener('drop', (e) => {
    e.preventDefault();
    document.body.classList.remove('dragging');

    const items = e.dataTransfer.items;
    if (items) {
        for (let i = 0; i < items.length; i++) {
            const entry = items[i].webkitGetAsEntry();
            if (entry) {
                traverseFileTree(entry);
            }
        }
    }
});
function traverseFileTree(item, path = "") {
    if (item.isFile) {
        if (item.name.endsWith('.json')) {
            item.file((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const jsonData = JSON.parse(e.target.result);
                    path = item.name.replace(".json","")
                    dimensions[path] = new Dimension(path,jsonData)
                    if (display) display.draw_universe();
                };
                reader.readAsText(file);
            });
        }
    } else if (item.isDirectory) {
        const dirReader = item.createReader();
        dirReader.readEntries((entries) => {
            for (let entry of entries) {
                traverseFileTree(entry, path + item.name + "/");
            }
        });
    }
}
window.addEventListener('resize', resizeCanvas);
=======

import JSZip from 'https://esm.sh/jszip@3.10.1';
let definitions_json;
let default_json;
const dimension_container = document.querySelector('#hirachy')
let dimensions = {
}
let editor;
let display; 
async function loadGameData() {
    try {
        const response1 = await fetch('assets/default.json');
        const data1 = await response1.json();
        default_json = data1
        
        const response2 = await fetch('assets/def.json');
        const data2 = await response2.json();
        editor = new Editor()
        display = new Display()
        definitions_json = data2

        document.querySelector('#download').addEventListener('click', () => {
            downloadAllDimensions()
        })
        let ids = 0
        document.querySelector('#cerate').addEventListener('click', () => {
            dimensions[String(ids)] = new Dimension(String(ids),default_json)
            ids +=1 
        })
        resizeCanvas()
        
    } catch (error) {
        console.error("Error loading JSON:", error);
    }
}
function resizeCanvas() {
    const canvas = document.querySelector('#canvas');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    display.draw_universe()
}
class Dimension {
    constructor(file_path,properties) {
        this.file_path = file_path
        this.properties = properties
        this.render = true
        
        this.load()
    }
    centerPlanet() {
        let x = 0;
        let y = 0;
        let props = this.properties;

        const scale = ((1/6)* display.width/ (this.properties["earthRadiusMultiplier"] * display.AU_to_earthRadius ))
        display.scale = scale

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"]) {
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);
        }
        display.camera = [x,y]
        display.draw_universe()
    }
    load() {
        const container = document.createElement('div')
        container.className = "dimension_container"

        this.html = {
            "name": Object.assign(document.createElement('div'), {
                className: "dimension_name",
                textContent: this.properties["name"]
            }),
            "view": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_edit",
                textContent: "☑"
            }),
            "reload": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_reload",
                textContent: "🗘"
            }),
            "remove": Object.assign(document.createElement('div'), {
                className: "dimension_btn",
                id: "dimension_remove",
                textContent: "🗑"
            }),
            "file_path": Object.assign(document.createElement('div'), {
                className: "dimension_file_path",
                textContent: this.file_path
            })
        }
        for (let item of Object.values(this.html)) {
            container.appendChild(item);
        }
        this.html["view"].addEventListener('click',() => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            display.draw_universe()})
        this.html["name"].addEventListener('click', () => {
            if (display.focus != this.file_path) {
                display.focus = this.file_path
                this.centerPlanet()
            }
            this.toggle_properties()})
        this.html["container"] = container
        dimension_container.appendChild(container)
        this.load_properties()
    }

    load_properties() {
        const properties_frame = Object.assign(document.createElement('div'), {
            className: "dimension_properties",
        })
        this.html["properties"] = []
        for (let item of Object.entries(this.properties)) {
            const element = Object.assign(document.createElement('div'), {
                className: "dimension_property",
                textContent: item[0]
            })
            element.addEventListener("click", () => {
                editor.focus(this.file_path,item[0])
                display.camera = [0,0]
            })
            properties_frame.appendChild(element)
            this.html["properties"].push(element)
        }
        dimension_container.appendChild(properties_frame)
        properties_frame.style.display = "none"
        this.html["properties_frame"] = properties_frame
    }
    toggle_properties() {
        const display = this.html["properties_frame"]
        if (display.style.display === 'none') {
            display.style.display = "block"
        }else {
            display.style.display = "none"
        }
    }
}
async function downloadAllDimensions() {
    const zip = new JSZip();

    for (const planet of Object.values(dimensions)) {
        const name = planet.file_path
        const fileName = `${name}.json`;
        
        const fileContent = JSON.stringify(planet.properties, null, 4);
        
        zip.file(fileName, fileContent);
    }

    const content = await zip.generateAsync({ type: "blob" });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(content);
    link.download = "dimensions_export.zip"; 
    
    document.body.appendChild(link);
    link.click();

    setTimeout(() => {
        URL.revokeObjectURL(link.href);
        link.remove();
    }, 200);
}
class Display {
    constructor() {
        this.canvas = document.querySelector('#canvas')
        this.ctx = this.canvas.getContext("2d");
        this.focus = null
        this.old_width = 0
        this.speed = 3
        this.camera = [0,0]
        this.scale = 10
        this.AU_to_earthRadius = 1/2343
        this.orbit_col = ["#b6c60e","#4d2911","#5A5A5A","#b6c60e","#4d2911","#5A5A5A"]
        this.mode = "draw"
        this.focus_color = false
        this.ring_width = 0.05
        this.ring_dist = 0.1
        this.canvas.addEventListener('keydown', (event) => {
            const key = event.key.toLowerCase();
            const moveStep = this.speed / this.scale;
            switch (key) {
                case 'arrowup':
                    this.camera[1] -= moveStep
                    break;
                case 'arrowdown':
                    this.camera[1] += moveStep
                    break;
                case 'arrowleft':
                    this.camera[0] -= moveStep
                    break;
                case 'arrowright':
                    this.camera[0] += moveStep
                    break;
                case 'o':
                    this.scale *= 1.1
                    break;
                case 'p':
                    this.scale /= 1.1
                    break;
            }
            this.draw_universe()
        });
    }
    draw() {

    }
    draw_universe() {
        const rect = this.canvas.getBoundingClientRect()
        const w = rect.width
        const h = rect.height
        this.width = w
        this.height = h
        this.cx = w/ 2
        this.cy = h / 2
        this.ctx.clearRect(0,0,w,h)
        for (let dimension of Object.values(dimensions)){
            this.draw_body(dimension)
        }
    }
    draw_body(dim) {
        let parent_count = 0;
        let x = 0;
        let y = 0;
        let props = dim.properties;

        const raw_radius = (props["earthRadiusMultiplier"] || 1) * this.scale * this.AU_to_earthRadius;
        const radius = Math.max(1, raw_radius + 1);

        if (!props["parentDimensionId"]) {
            x = props["position"]?.["x"] || 0;
            y = props["position"]?.["y"] || 0;
        } else {
            let parent = props;
            while (parent["parentDimensionId"] && parent_count < 10) {
                parent_count += 1;
                x -= (parent["orbitalDistanceToParent"] || 0);
                let pId = parent["parentDimensionId"];
                let parentKey = `${pId.namespace}_${pId.path}`;
                if (dimensions[parentKey]) {
                    parent = dimensions[parentKey].properties;
                } else { 
                    break; 
                }
            }
            
            x += (parent["position"]?.["x"] || 0);
            y += (parent["position"]?.["y"] || 0);

            const orbX = (x - this.camera[0]+props["orbitalDistanceToParent"]) * this.scale + this.cx;
            const orbY = (y - this.camera[1]) * this.scale + this.cy;
            const orbit_radius = (props["orbitalDistanceToParent"] || 0) * this.scale;
            
            
            this.ctx.beginPath();
            //this.ctx.setLineDash([5, 5]);
            this.ctx.arc(orbX, orbY, orbit_radius, 0, 2 * Math.PI);
            this.ctx.strokeStyle = "#ffffff";
            this.ctx.stroke();
        }
        const screenX = (x - this.camera[0]) * this.scale + this.cx;
        const screenY = (y - this.camera[1]) * this.scale + this.cy;
        const color = this.orbit_col[parent_count] || "#ffffff";

        this.ctx.beginPath();
        this.ctx.setLineDash([]);
        this.ctx.arc(screenX, screenY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();
    }
}
class Editor {
    constructor() {
        this.info_html = {
            "name": document.querySelector('#editor-name'),
            "description": document.querySelector('#editor-description'),
            "type": document.querySelector('#editor-type')
        }
        this.inputs = [
            {
                "frame": document.querySelector('#switch-row'),
                "input": document.querySelector('#switch-input')
            },
            {
                "frame": document.querySelector('#text-row'),
                "input": document.querySelector('#text-input')
            },
            {
                "frame": document.querySelector('#vec3-row'),
                "inputs": [
                    document.querySelector('#vec1-input'),
                    document.querySelector('#vec2-input'),
                    document.querySelector('#vec3-input'),
                ]
            },
            {
                "frame": document.querySelector('#selection-row'),
                "input": document.querySelector('#selection-input'),
                "datalist": document.querySelector('#datalist')
            },
            {
                "frame": document.querySelector('#path-row'),
                "inputs": [
                    document.querySelector('#namespace-input'),
                    document.querySelector('#path-input')
                ]
            }
        ]
        this.inputs.forEach((item, i) => {
            if (!item.input && !item.inputs) console.error(`Input ${i} is NULL!`);
        });
        this.activeDim = null
        this.activeProp = null
        this.setupListeners()
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
    }
    setupListeners() {
        this.inputs[0]["input"].addEventListener('change', (e) => {
            if (this.activeDim && this.activeProp) {
                dimensions[this.activeDim].properties[this.activeProp] = e.target.checked;
            }
        });
        this.inputs[1]["input"].addEventListener('input', (e) => {
            if (this.activeDim && this.activeProp) {
                let val = e.target.value;
                const type = definitions_json[this.activeProp]["varStruc"];
                dimensions[this.activeDim].properties[this.activeProp] = type == "int" || type == "floar" ? Number(val) : String(val);
                if (this.activeProp == "name" ){
                    dimensions[this.activeDim].html["name"].textContent = String(val)
                }
            }
        });
        const axes = ["x", "y", "z"];
        this.inputs[2]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                if (this.activeDim && this.activeProp) {
                    const axis = axes[i];
                    dimensions[this.activeDim].properties[this.activeProp][axis] = parseFloat(e.target.value) || 0.0;
                }
            });
        });
        const paths = ["namespace","path"];
        this.inputs[4]["inputs"].forEach((input, i) => {
            input.addEventListener('input', (e) => {
                if (this.activeDim && this.activeProp) {
                    const path = paths[i];
                    dimensions[this.activeDim].properties[this.activeProp][path] = String(e.target.value)
                    if (this.activeProp == "dimensionId" ){
                        const dimension = dimensions[this.activeDim]
                        const file_path = [dimension.properties[this.activeProp]["namespace"],dimension.properties[this.activeProp][path]].join("_")
                        delete dimensions[this.activeDim];
                        dimension.file_path = file_path
                        dimension.html.file_path.textContent = file_path
                        this.activeDim  = file_path
                        dimensions[file_path] = dimension
                    }

                }
            });
        });
        this.inputs[3]["input"].addEventListener('input', (e) => {
            if (!this.activeDim || !this.activeProp) return;
            const newValue = e.target.value;
            const currentData = dimensions[this.activeDim].properties[this.activeProp];
            if (typeof currentData === 'object' && currentData !== null) {
                currentData = dimensions[newValue].properties["dimensionId"];
            } else {
                dimensions[this.activeDim].properties[this.activeProp] = dimensions[newValue].properties["dimensionId"];
            }
        });
    }
    focus(dim,prop) {
        for(let input of this.inputs) {
            input["frame"].style.display = "none"
        }
        if (!Object.keys(definitions_json).includes(prop)) {
            return
        }
        const info = definitions_json[prop]
        this.info_html["name"].textContent = prop
        this.info_html["description"].textContent = info["definition"]
        this.activeDim = dim
        this.activeProp = prop

        let val = dimensions[dim].properties[prop]
        switch(info["varStruc"]) {
            case "float":
            case "int":
            case "str": {
                this.inputs[1]["frame"].style.display = "block";
                console.log(this.inputs[1]["input"])
                this.inputs[1]["input"].value = (val === null) ? "" : String(val);
                break;}
            case "boolean":{
                this.inputs[0]["frame"].style.display = "block";
                this.inputs[0]["input"].checked = val;
                break;}
            case "Vec3":{
                this.inputs[2]["frame"].style.display = "block";
                for (let i = 0; i < 3; i++) {
                    let vali = val[["x","y","z"][i]]
                    this.inputs[2]["inputs"][i].value = vali
                }
                break;}
            case "path":{
                if (info["extra"] == "selection") {
                    this.inputs[3]["frame"].style.display = "block";
                    this.inputs[3]["input"].value = val ? [val["namespace"],val["path"]].join("_") : "" 
                    this.inputs[3]["datalist"].innerHTML = "";
                    Object.keys(dimensions).forEach(path => {
                        const option = document.createElement('option');
                        option.value = path;
                        this.inputs[3]["datalist"].appendChild(option);
                    });
                }else {
                    this.inputs[4]["frame"].style.display = "block";
                    this.inputs[4]["inputs"][0].value = val["namespace"]
                    this.inputs[4]["inputs"][1].value = val["path"]
                }
                break;}
            default:
                console.log("not added " + info["varStruc"])
        }
    }
}
window.addEventListener('dragenter', (e) => {
    e.preventDefault();
    document.body.classList.add('dragging');
});
window.addEventListener('dragover', (e) => {
    e.preventDefault();
});
window.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
        document.body.classList.remove('dragging');
    }
});
window.addEventListener('drop', (e) => {
    e.preventDefault();
    document.body.classList.remove('dragging');

    const items = e.dataTransfer.items;
    if (items) {
        for (let i = 0; i < items.length; i++) {
            const entry = items[i].webkitGetAsEntry();
            if (entry) {
                traverseFileTree(entry);
            }
        }
    }
});
function traverseFileTree(item, path = "") {
    if (item.isFile) {
        if (item.name.endsWith('.json')) {
            item.file((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const jsonData = JSON.parse(e.target.result);
                    path = item.name.replace(".json","")
                    dimensions[path] = new Dimension(path,jsonData)
                    if (display) display.draw_universe();
                };
                reader.readAsText(file);
            });
        }
    } else if (item.isDirectory) {
        const dirReader = item.createReader();
        dirReader.readEntries((entries) => {
            for (let entry of entries) {
                traverseFileTree(entry, path + item.name + "/");
            }
        });
    }
}
window.addEventListener('resize', resizeCanvas);
>>>>>>> 1f2e271d2a354d760288eda41eab0fbf3a0bb5a7
loadGameData();