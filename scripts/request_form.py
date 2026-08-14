
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class RequestForm:

    def __init__(self):
        self.length = None
        self.width = None
        self.height = None

        self.image_path = ""

        self.root = tk.Tk()
        self.root.title("Sofa Cost Estimation System")
        self.root.geometry("550x420")
        self.root.resizable(False, False)

        tk.Label(
            self.root,
            text="SOFA COST ESTIMATION SYSTEM",
            font=("Arial",18,"bold")
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Choose Sofa Image",
            command=self.choose_image,
            width=20
        ).pack()

        self.image_label = tk.Label(
            self.root,
            text="No image selected",
            wraplength=500,
            fg="blue"
        )
        self.image_label.pack(pady=10)

        tk.Label(self.root,text="Length (mm)").pack()

        self.length_entry=tk.Entry(self.root,width=25)
        self.length_entry.pack()

        tk.Label(self.root,text="Width (mm)").pack()

        self.width_entry=tk.Entry(self.root,width=25)
        self.width_entry.pack()

        tk.Label(self.root,text="Height (mm)").pack()

        self.height_entry=tk.Entry(self.root,width=25)
        self.height_entry.pack()

        tk.Button(
            self.root,
            text="Submit Request",
            command=self.submit,
            bg="green",
            fg="white",
            width=20
        ).pack(pady=20)

    def choose_image(self):

        path=filedialog.askopenfilename(

            title="Select Sofa Image",

            filetypes=[("Image Files","*.jpg *.jpeg *.png")]

        )

        if path:
            self.image_path=path
            self.image_label.config(text=path)

    def submit(self):

        if self.image_path == "":
            messagebox.showerror("Error", "Select an image.")
            return

        if self.length_entry.get() == "":
            messagebox.showerror("Error", "Enter Length.")
            return

        if self.width_entry.get() == "":
            messagebox.showerror("Error", "Enter Width.")
            return

        if self.height_entry.get() == "":
            messagebox.showerror("Error", "Enter Height.")
            return

    # Save values BEFORE closing the window
        self.length = float(self.length_entry.get())
        self.width = float(self.width_entry.get())
        self.height = float(self.height_entry.get())

        self.root.destroy()

    def get_request(self):

        self.root.mainloop()

        requests_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "outputs",
            "requests"
        )

        os.makedirs(requests_folder, exist_ok=True)

        count = 1
        while os.path.exists(os.path.join(requests_folder, f"demo_{count:03d}")):
            count += 1

        return {
            "request_id": f"demo_{count:03d}",
            "image_path": self.image_path,
            "length": self.length,
            "width": self.width,
            "height": self.height
        }