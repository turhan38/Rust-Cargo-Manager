import tkinter as tk
from tkinter import ttk, messagebox ,filedialog
import webbrowser

import toml
import requests
import shutil

class CargoManager(tk.Tk):
    selectedTomlFilePath = None
    selectedTomlConfig = None
    createsInProject = []
    

    def __init__(self):
        super().__init__()
        self.title("Rust Cargo Manager")
        self.geometry("1750x720")
        self.minsize(1750, 600)

        self.palette = {
            "bg":       "#f6f7fb",
            "fg":       "#1f2937",
            "muted":    "#6b7280",
            "card":     "#ffffff",
            "accent":   "#4f46e5", 
            "accentfg": "#ffffff",
            "border":   "#e5e7eb",
        }

        self.configure(bg=self.palette["bg"])
        self.initStyle()

        self.statusVar = tk.StringVar(value="Ready")
        self.searchVar = tk.StringVar()
        self.depScopeVar = tk.StringVar(value="dependencies")

        self.buildHeader()      
        self.buildBody()        
        self.buildStatusbar() 

    def initStyle(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.palette["bg"])
        style.configure("Card.TFrame", background=self.palette["card"], borderwidth=1, relief="solid")
        style.map("TButton", background=[("active", "#eef2ff")])
        style.configure("Title.TLabel", background=self.palette["bg"], foreground=self.palette["fg"], font=("Segoe UI", 14, "bold"))
        style.configure("Muted.TLabel", background=self.palette["bg"], foreground=self.palette["muted"]) 
        style.configure("CardTitle.TLabel", background=self.palette["card"], foreground=self.palette["fg"], font=("Segoe UI", 11, "bold"))
        style.configure("CardMuted.TLabel", background=self.palette["card"], foreground=self.palette["muted"]) 
        style.configure("Accent.TButton", foreground=self.palette["accentfg"]) 
        style.configure("TSeparator", background=self.palette["border"]) 

        style.configure("Treeview",
                        background=self.palette["card"],
                        fieldbackground=self.palette["card"],
                        foreground=self.palette["fg"],
                        bordercolor=self.palette["border"],
                        borderwidth=0,
                        rowheight=28)
        style.configure("Treeview.Heading",
                        background="#f3f4f6",
                        foreground=self.palette["fg"],
                        relief="flat")
        style.map("Treeview.Heading", background=[("active", "#e5e7eb")])

        style.configure("TProgressbar", troughcolor=self.palette["bg"], background=self.palette["accent"]) 

    def buildHeader(self):
        header = ttk.Frame(self, padding=(16, 14))
        header.pack(fill="x")
        title = ttk.Label(header, text="RUST Cargo Manager", style="Title.TLabel")
        title.pack(side="left")
        actions = ttk.Frame(header)
        actions.pack(side="right")

    def buildBody(self):
        body = ttk.Frame(self, padding=(16, 0))
        body.pack(fill="both", expand=True)

        paned = ttk.PanedWindow(body, orient="horizontal")
        paned.pack(fill="both", expand=True)

        leftWrap, leftContent = self.card(paned, pad=(12, 12)) 
        self._buildLeftPanel(leftContent)
        paned.add(leftWrap, weight=1)

        rightWrap, rightContent = self.card(paned, pad=(12, 12)) 
        self._buildRightPanel(rightContent)
        paned.add(rightWrap, weight=1)

    def card(self, parent, pad=(12, 12)):
        wrap = ttk.Frame(parent, style="TFrame") 
        inner = ttk.Frame(wrap, style="Card.TFrame")
        inner.pack(fill="both", expand=True, padx=8, pady=8)
        content = ttk.Frame(inner, padding=pad, style="Card.TFrame")
        content.pack(fill="both", expand=True)
        return wrap, content

    def _buildLeftPanel(self, parent):
        header = ttk.Frame(parent, style="Card.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Current Packages", style="CardTitle.TLabel").pack(side="left")
        self.filePathLabel = ttk.Label(header, text="Not Selected", style="CardMuted.TLabel")
        self.filePathLabel.pack(side="left", padx=(8,0))

        toolbar = ttk.Frame(parent, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(8, 8))
        ttk.Button(toolbar, text="Select Cargo.toml", command=self.selectTomlFile).pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=self.loadTomlFile).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Remove Selected", command=self.deleteCrateInProject).pack(side="left")

        cols = ("scope", "name", "version", "latest", "desc")
        self.treeLeft = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        self.treeLeft.heading("scope", text="Section")
        self.treeLeft.heading("name", text="Crate")
        self.treeLeft.heading("version", text="Version")
        self.treeLeft.heading("latest", text="Latest Version")
        self.treeLeft.heading("desc", text="Description")

        self.treeLeft.column("scope", width=120, anchor="center")
        self.treeLeft.column("name", width=120, anchor="center")
        self.treeLeft.column("version", width=120, anchor="center")
        self.treeLeft.column("latest", width=120, anchor="center")
        self.treeLeft.column("desc", width=500)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.treeLeft.yview)
        self.treeLeft.configure(yscroll=vsb.set)
        self.treeLeft.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

    def _buildRightPanel(self, parent):
        header = ttk.Frame(parent)
        header.pack()
        ttk.Label(header, text="Search / Add", style="CardTitle.TLabel").pack(side="left")

        searchbar = ttk.Frame(parent, style="Card.TFrame")
        searchbar.pack(fill="x", pady=(8, 4))
        ttk.Label(searchbar, text="🔎", style="CardMuted.TLabel").pack(side="left", padx=(0, 6))
        entry = ttk.Entry(searchbar, textvariable=self.searchVar)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(searchbar, text="Search", command=self.searchAndGetCrates).pack(side="left", padx=(6, 0))

        addbar = ttk.Frame(parent, style="Card.TFrame")
        addbar.pack(fill="x", pady=(8, 12))
        ttk.Label(addbar, text="Target Section:", style="CardMuted.TLabel").pack(side="left")
        for scope in ("dependencies", "dev-dependencies", "build-dependencies"):
            ttk.Radiobutton(addbar, text=scope, value=scope, variable=self.depScopeVar).pack(side="left", padx=(6, 0))

        ttk.Button(addbar, text="Open Crates Link", command=self.openSelectedSearchLink).pack(side="right")
        ttk.Button(addbar, text="Add to Selected", command=self.addSelectedToProject).pack(side="right", padx=(0, 6))

        cols = ("name", "maxver", "desc")
        self.treeRight = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        self.treeRight.heading("name", text="Crate")
        self.treeRight.heading("maxver", text="Latest Version")
        self.treeRight.heading("desc", text="Description")

        self.treeRight.column("name", width=220)
        self.treeRight.column("maxver", width=130, anchor="center")
        self.treeRight.column("desc", width=520)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.treeRight.yview)
        self.treeRight.configure(yscroll=vsb.set)
        self.treeRight.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

    def buildStatusbar(self):
        bar = ttk.Frame(self, padding=(16, 12))
        bar.pack(fill="x")
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=140)
        self.progress.pack(side="left")
        ttk.Label(bar, textvariable=self.statusVar, style="Muted.TLabel").pack(side="left", padx=(12, 0))

    # --- Loading helpers ---
    def setStatus(self, text, busy=False):
        self.statusVar.set(text)
        if busy:
            try:
                self.progress.start(10)
            except Exception:
                pass
        else:
            try:
                self.progress.stop()
            except Exception:
                pass
    
    # Get json
    def getJson(self ,url: str, timeout=10):          
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "tk-crates-ui/1.0"})
        r.raise_for_status()
        return r.json()

    # Crates.io
    def cratesSearch(self ,query: str, per_page=50):
        if not query.strip():
            return {"crates": []}
        url = f"https://crates.io/api/v1/crates?q={query}&per_page={per_page}"
        return self.getJson(url)

    def crateInfo(self, name: str):
        url = f"https://crates.io/api/v1/crates/{name}"
        return self.getJson(url)

    def openLink(self, name: str):
        webbrowser.open(f"https://crates.io/crates/{name}")

    # Open selected search link
    def openSelectedSearchLink(self):
        selected = self.treeRight.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a crate from the right list.")
            return
        self.openLink(self.treeRight.item(selected)["values"][0])

    # Add to Project
    def addSelectedToProject(self):
        if not self.selectedTomlFilePath:
            messagebox.showinfo("Error", "Please first select a TOML file.")
            return
        selected = self.treeRight.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a crate from the right list.")
            return
        crate = self.treeRight.item(selected)["values"]
        addable = (self.depScopeVar.get(), crate[0], crate[1], crate[1], crate[2])
        if addable not in self.createsInProject:
            self.createsInProject.append(addable)
            self.updateTomlFile()
        else:
            messagebox.showinfo("Info", "This crate is already added to the project.")

    # Search and Get Crates
    def searchAndGetCrates(self):
        self.setStatus("Searching Crates...", busy=True)
        query = self.searchVar.get()
        results = self.cratesSearch(query)
        for item in self.treeRight.get_children():
            self.treeRight.delete(item)
        for crate in results.get("crates", []):
            self.treeRight.insert("", "end", values=(
                crate["name"],
                crate["max_version"],
                crate["description"],
            ))
        self.after(1000, lambda: self.setStatus("Ready", busy=False))

    # Delete crate in project
    def deleteCrateInProject(self):
        selected = self.treeLeft.selection() 
        if(len(selected) != 0):
            deletable = tuple(self.treeLeft.item(selected)["values"])
            self.createsInProject.remove(deletable)
            self.updateTomlFile()

    # Crates in project
    def updateCreatesInProject(self):
        self.createsInProject = []
        if "dependencies" in self.selectedTomlConfig:
            for key,value in self.selectedTomlConfig.get("dependencies", {}).items():
                self.createsInProject.append(("dependencies",key,value,self.crateInfo(name=key)["crate"]["newest_version"],self.crateInfo(name=key)["crate"]["description"]))
        if "dev-dependencies" in self.selectedTomlConfig:
            for key,value in self.selectedTomlConfig.get("dev-dependencies", {}).items():
                self.createsInProject.append(("dev-dependencies",key,value,self.crateInfo(name=key)["crate"]["newest_version"],self.crateInfo(name=key)["crate"]["description"]))
        if "build-dependencies" in self.selectedTomlConfig:
            for key,value in self.selectedTomlConfig.get("build-dependencies", {}).items():
                self.createsInProject.append(("build-dependencies",key,value,self.crateInfo(name=key)["crate"]["newest_version"],self.crateInfo(name=key)["crate"]["description"]))
        
        for item in self.treeLeft.get_children():
            self.treeLeft.delete(item)
        for crates in self.createsInProject:
            self.treeLeft.insert("", "end", values=crates)

    # Update Toml File
    def updateTomlFile(self):
        if not self.selectedTomlFilePath:
            messagebox.showinfo("Error", "Please first select a TOML file.")
            return
        self.setStatus("Updating...", busy=True)
        if self.createsInProject.count == 0:
            self.selectedTomlConfig["dependencies"].clear()
            self.selectedTomlConfig["dev-dependencies"].clear()
            self.selectedTomlConfig["build-dependencies"].clear()
        else :
            for section, name, version , lastVersion , desc in self.createsInProject:
                if(section not in self.selectedTomlConfig.keys()):
                    self.selectedTomlConfig[section] = {}
                self.selectedTomlConfig[section][name] = version

        shutil.copy2(self.selectedTomlFilePath, f"{self.selectedTomlFilePath}.backup")
        
        with open(self.selectedTomlFilePath, 'w') as f:
            toml.dump(self.selectedTomlConfig, f)
        self.loadTomlFile()

    # Loading Toml File
    def loadTomlFile(self):
        if not self.selectedTomlFilePath:
            messagebox.showinfo("Error", "Please first select a TOML file.")
            return
        self.setStatus("Loading...", busy=True)
        with open(self.selectedTomlFilePath, 'r') as f:
               self.selectedTomlConfig = toml.load(f)
               self.updateCreatesInProject()
        self.after(1000, lambda: self.setStatus("Ready", busy=False))

    # Select Toml File
    def selectTomlFile(self):
        self.selectedTomlFilePath = filedialog.askopenfilename(filetypes=[("TOML files", "*.toml")])
        if self.selectedTomlFilePath:
           self.filePathLabel.config(text=f"{self.selectedTomlFilePath}")
           self.loadTomlFile()

if __name__ == "__main__":
    app = CargoManager()
    app.mainloop()
