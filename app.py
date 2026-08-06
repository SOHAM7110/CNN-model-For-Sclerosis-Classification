# set PYTHONIOENCODING=utf-8
# python your_script.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from customtkinter import CTkImage
import sqlite3
import os
import sys
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import bcrypt

APP_WIDTH = 950
APP_HEIGHT = 800
sys.stdout.reconfigure(encoding='utf-8')

# ------------------ DATABASE SETUP ------------------
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS staff (
    username TEXT PRIMARY KEY,
    password TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    gender TEXT,
    symptoms TEXT,
    medical_history TEXT,
    image_path TEXT,
    class TEXT
)""")
conn.commit()

# ------------------ BACKGROUND IMAGE LOADING ------------------

def load_background_image(path, width, height):
    try:
        if not os.path.exists(path):
            print(f"Background image not found at: {path}")
            return None
        print(f"Background image found at: {path}")
        img = Image.open(path)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return CTkImage(light_image=img, dark_image=img, size=(width, height))
    except Exception as e:
        print(f"Error loading background image: {e}")
        return Noneg

bg_path = ""  # <-- Update this if needed
ctk_bg_image = load_background_image(bg_path, APP_WIDTH, APP_HEIGHT)

def center_window(window, width=APP_WIDTH, height=APP_HEIGHT):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 4
    y = (screen_height - height) // 4
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.attributes('-topmost', True)

    if ctk_bg_image:
        bg_label = ctk.CTkLabel(window, image=ctk_bg_image, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()
        print(f"🎨 Background image applied to window: {window.title()}")
    else:
        print(f"⚠️ No background image applied to window: {window.title()}")

# ------------------ MODEL PREDICTION ------------------

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    model = load_model('model_1.keras')
    class_names = ['class 1','class 2','class 3','class 4','class 5','class 6']
    prediction = model.predict(img_array)
    return np.argmax(prediction[0])

# ------------------ LOGIN / REGISTRATION ------------------

def verify_login():
    user = entry_username.get()
    pwd = entry_password.get()

    cursor.execute("SELECT password FROM staff WHERE username=?", (user,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(pwd.encode(), result[0]):
        root.withdraw()
        open_staff_window()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

def open_register_window():
    def register():
        username = entry_reg_user.get()
        password = entry_reg_pass.get()
        confirm = entry_reg_confirm.get()

        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields required.")
            return
        if len(username) < 4:
            messagebox.showerror("Error", "Username too short.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        hashed_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            cursor.execute("INSERT INTO staff (username, password) VALUES (?, ?)", (username, hashed_pwd))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            reg_win.destroy()
            root.deiconify()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
    root.withdraw()

    reg_win = ctk.CTkToplevel()
    reg_win.title("Register")
    center_window(reg_win, 400, 300)

    entry_reg_user = ctk.CTkEntry(reg_win, placeholder_text="Username")
    entry_reg_pass = ctk.CTkEntry(reg_win, placeholder_text="Password", show="*")
    entry_reg_confirm = ctk.CTkEntry(reg_win, placeholder_text="Confirm Password", show="*")

    entry_reg_user.pack(pady=10)
    entry_reg_pass.pack(pady=10)
    entry_reg_confirm.pack(pady=10)
    ctk.CTkButton(reg_win, text="Register", command=register).pack(pady=10)

# ------------------ MAIN WINDOWS ------------------

def open_staff_window():
    win = ctk.CTkToplevel()
    win.title("Staff Panel")
    center_window(win)
    ctk.CTkButton(win, text="Add Patient", width=400, height=100, command=lambda: [win.destroy(), add_patient()]).place(x=300, y=130)
    ctk.CTkButton(win, text="View Patients", width=400, height=100, command=lambda: [win.destroy(), view_patients()]).place(x=300, y=270)
    ctk.CTkButton(win, text="Logout", width=400, height=100, command=lambda: [win.destroy(), root.deiconify()]).place(x=300, y=400)

def add_patient():
    win = ctk.CTkToplevel()
    win.title("Add Patient")
    center_window(win)

    name = ctk.CTkEntry(win, placeholder_text="Name", width=350, fg_color="#212121",border_color="#5c5c5c", text_color="white", border_width=1,corner_radius=6)
    age = ctk.CTkEntry(win, placeholder_text="Age", width=350,fg_color="#212121",border_color="#5c5c5c", text_color="white", border_width=1,corner_radius=6)
    gender = ctk.StringVar(value="Male")
    # history = ctk.CTkEntry(win, placeholder_text="Medical History", width=300, height = 150)
    history = ctk.CTkTextbox(win, width=450, height=150, fg_color="#212121",border_color="#5c5c5c", text_color="white", border_width=1,corner_radius=6)
    img_path = ctk.CTkEntry(win, placeholder_text="Image Path", width=300,fg_color="#212121",border_color="#5c5c5c", text_color="white", border_width=1,corner_radius=6)

    ctk.CTkLabel(win, text="Name").place(x=240, y=20)
    name.place(x=300, y=20)
    ctk.CTkLabel(win, text="Age").place(x=240, y=70)
    age.place(x=300, y=70)

    ctk.CTkLabel(win, text="Gender").place(x=240, y=120)
    gender_frame = ctk.CTkFrame(win, width=300, height=40)
    gender_frame.place(x=300, y=120)
    for idx, g in enumerate(["Male", "Female", "Other"]):
        ctk.CTkRadioButton(gender_frame, text=g, variable=gender, value=g).place(x=idx * 80, y=5)

    symptoms = ["Vision Problems", "Muscle Weakness", "Numbness & Tingling", "Fatigue", "Coordination Issues", "Cognitive Problems"]
    vars = [ctk.StringVar() for _ in symptoms]
    ctk.CTkLabel(win, text="Symptoms").place(x=225, y=180)
    for i, s in enumerate(symptoms):
        col = i % 2
        row = i // 2
        ctk.CTkCheckBox(win, text=s, variable=vars[i], onvalue=s, offvalue="").place(x=300 + col * 180, y=180 + row * 30)

    ctk.CTkLabel(win, text="Doctor's Note").place(x=140, y=300)
    history.place(x=250, y=300)
    history.insert("0.0", "")  # optional: pre-fill with text

    ctk.CTkLabel(win, text="Upload Image").place(x=140, y=470)
    img_path.place(x=250, y=470)
    ctk.CTkButton(win, text="Browse", command=lambda: browse_image(img_path)).place(x=565, y=470)

    def save():
        s = ", ".join([v.get() for v in vars if v.get()])
        if name.get() and age.get():
            predicted_index = predict_image(img_path.get())
            class_names = [
                'class 1',
                'class 2',
                'class 3',
                'class 4',
                'class 5',
                'class 6'
                ]
            predicted_disease = class_names[predicted_index]
            cursor.execute("INSERT INTO patients (name, age, gender, symptoms, medical_history, image_path, class) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name.get(), age.get(), gender.get(), s, history.get("1.0", "end-1c"), img_path.get(), predicted_disease))
            conn.commit()
            messagebox.showinfo("Saved", "Patient added")
            win.destroy()
            open_staff_window()
        else:
            messagebox.showerror("Error", "Required fields missing")

    ctk.CTkButton(win, text="Save", command=save, width=200,height = 60).place(x=400, y=520)
    ctk.CTkButton(win, text="Back", command=lambda: [win.destroy(), open_staff_window()], width=200, height =60).place(x=400, y=590)

def browse_image(entry):
    path = filedialog.askopenfilename(filetypes=[("Image", "*.png;*.jpg;*.jpeg")])
    if path:
        entry.delete(0, 'end')
        entry.insert(0, path)

def view_patients():
    win = ctk.CTkToplevel()
    win.title("Patients")
    center_window(win)

    cursor.execute("SELECT id, name FROM patients")
    y = 20
    for pid, pname in cursor.fetchall():
        f = ctk.CTkFrame(win, width=800, height=40)
        f.place(x=50, y=y)
        ctk.CTkLabel(f, text=pname).place(x=10, y=10)
        ctk.CTkButton(f, text="View", command=lambda pid=pid: (win.destroy(), view_details(pid))).place(x=600, y=5)
        y += 60

    ctk.CTkButton(win, text="Back", width=200, height=60, command=lambda: (win.destroy(), open_staff_window())).place(x=400, y=y+20)



def view_details(pid):
    cursor.execute("SELECT * FROM patients WHERE id=?", (pid,))
    p = cursor.fetchone()

    if p:
        win = ctk.CTkToplevel()
        win.title("Patient Details")
        center_window(win)

        # ---------------------------
        # Main Patient Details
        # ---------------------------
        details = {
            "Name": p[1], "Age": p[2], "Gender": p[3],
            "Symptoms": p[4], "Medical History": p[5],
            "Prediction": p[7]
        }

        label_x = 40
        value_x = 200
        y = 20
        spacing = 35

        for label, value in details.items():
            ctk.CTkLabel(win, text=f"{label}:", font=("Arial", 14, "bold")).place(x=label_x, y=y)
            ctk.CTkLabel(win, text=value, font=("Arial", 14)).place(x=value_x, y=y)
            y += spacing

        # ---------------------------
        # Symptom List Grid
        # ---------------------------
        symptoms_list = p[4].split(", ")
        y += 10
        ctk.CTkLabel(win, text="Symptoms Breakdown:", font=("Arial", 13, "bold")).place(x=label_x, y=y)
        y += spacing

        for i, sym in enumerate(symptoms_list):
            col = i % 2
            row = i // 2
            x = label_x + col * 200
            ctk.CTkLabel(win, text=f"- {sym}", font=("Arial", 12, "bold")).place(x=x, y=y + row * 25)

        y += ((len(symptoms_list) + 1) // 2) * 25 + 20

        # ---------------------------
        # MRI Image Display
        # ---------------------------
        if p[6] and os.path.exists(p[6]):
            try:
                img = Image.open(p[6])
                ctk_img = CTkImage(dark_image=img, size=(350, 350))
                lbl = ctk.CTkLabel(win, image=ctk_img, text="")
                lbl.image = ctk_img
                lbl.place(x=label_x, y=y)
                y += 360 + 10
            except Exception as e:
                ctk.CTkLabel(win, text=f"Error loading image: {e}", text_color="red").place(x=label_x, y=y)
                y += 30

        # ---------------------------
        # Back Button
        # ---------------------------
        ctk.CTkButton(
    win, text="Back", command=lambda: (win.destroy(), open_staff_window()), width=200, height=30).place(x=390, y=y + 10)



# ------------------ MAIN ROOT WINDOW ------------------

root = ctk.CTk()
root.title("Sclerosis Prediction System")
center_window(root)

entry_username = ctk.CTkEntry(root, placeholder_text="Username", width=350, height=50)
entry_password = ctk.CTkEntry(root, placeholder_text="Password", show="*", width=350, height=50)

entry_username.place(x=300, y=200)
entry_password.place(x=300, y=270)

show_pass_var = ctk.BooleanVar()
def toggle_main_password():
    entry_password.configure(show="" if show_pass_var.get() else "*")

ctk.CTkCheckBox(root, text="Show Password", variable=show_pass_var, command=toggle_main_password).place(x=300, y=330)
ctk.CTkButton(root, text="Login", width=350, height=50, command=verify_login).place(x=300, y=370)
ctk.CTkButton(root, text="Register", width=350, height=50, command=open_register_window).place(x=300, y=430)

root.mainloop()
conn.close()
