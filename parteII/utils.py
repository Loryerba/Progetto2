import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image,ImageTk
from ttkthemes import ThemedTk
from scipy.fft import dctn,idctn
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Variabili globali
global entry_file_path, entry_f, entry_d, path, label_dim
path = ""
def check_input_values():
    global entry_f, entry_d, path

    F = entry_f.get()
    d = entry_d.get()

    if not path:
        messagebox.showerror("Errore", "Selezionare un'immagine")
        return False

    if not F:
        messagebox.showerror("Errore", "Inserire un valore nel campo F")
        return False

    if not check_if_int(F):
        messagebox.showerror("Errore", "Il campo F dev'essere intero")
        return False

    F = int(F)

    if F <= 0:
        messagebox.showerror("Errore", "Il campo F dev'essere > 0")
        return False

    size = get_img_size()
    if not size:
        return False

    width, height = size
    if F > width or F > height:
        messagebox.showerror("Errore", "F non può essere maggiore delle dimensioni dell'immagine")
        return False

    if not d:
        messagebox.showerror("Errore", "Inserire un valore nel campo d")
        return False

    if not check_if_int(d):
        messagebox.showerror("Errore", "Il campo d dev'essere intero")
        return False

    d = int(d)

    if d < 0:
        messagebox.showerror("Errore", "Il campo d dev'essere >= 0")
        return False

    if d > 2 * F - 2:
        messagebox.showerror("Errore", "d non può essere maggiore di 2F - 2")
        return False

    return F, d

def check_if_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def get_img_size():
    try:
        img = Image.open(path)
        width, height = img.size
        img.close()
        return width, height
    except Exception as e:
        img.close()
        messagebox.showerror("Errore", str(e))
        return False

def open_file_system():
    global entry_file_path, path, label_dim
    path = filedialog.askopenfilename(
        filetypes=[("File BMP", "*.bmp")]
    )
    if path:
        entry_file_path.config(state='normal')
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, path)
        entry_file_path.config(state='readonly')
        size = get_img_size()
        if not size:
            return

        width, height = size
        label_dim.config(text=f"Dimension: {width}x{height}")

def divide_image_into_blocks(F):
    blocks = []
    size = get_img_size()
    if(not size):
        return False
    
    width,height = size
    try:
        img_converted = Image.open(path).convert('L')
        max_width = width // F
        max_height = height // F

        for by in range(0, max_height):
            for bx in range(0, max_width):
                x = bx * F
                y = by * F
                block = img_converted.crop((x, y, x + F, y + F))  # (left, upper, right, lower)
                blocks.append(block)

        return blocks
    except Exception as e:
        messagebox.showerror("Errore",str(e))
        return False


def run_dct2_and_round(blocks,F,d):
    dct2_result = []
    for block in blocks:
        array_from_block = np.array(block)
        result = dctn(array_from_block,type=2,norm="ortho")
        result = delete_frequencies(result,F,d)
        dct2_result.append(result)
    
    return dct2_result



def delete_frequencies(dct_block, F, d):
    rounded_freq = dct_block * (np.abs(np.add.outer(range(F), range(F))) < d)
    return rounded_freq


def run_idct2(frequencies):
    blocks_reconstructed = []

    for f in frequencies:
        idct2_result = idctn(f,type=2,norm="ortho")
        idct2_result = np.round(idct2_result)
        idct2_result = np.clip(idct2_result, 0, 255).astype(np.uint8)
        blocks_reconstructed.append(idct2_result)
    
    return blocks_reconstructed

def reconstruct_image(blocks_reconstructed,F):
    size = get_img_size()
    if(not size):
        return False
    width,height = size
    new_image = Image.new('L',(width,height))
    new_image_path = "immagini/my_image_compressed.bmp"
    max_width = width // F
    max_height = height // F

    for j in range(max_height):
        for i in range(max_width):
            block = blocks_reconstructed.pop(0)
            x = i * F
            y = j * F
            new_image.paste(Image.fromarray(block), (x, y))

    
    new_image.save(new_image_path)
    new_image.close()

    return new_image_path


def show_comparison(original_image, compressed_image):
    def on_closing():
        original_image.close()
        compressed_image.close()

        root.destroy()
        root.quit()

    original_image = Image.open(original_image).convert('L')
    compressed_image = Image.open(compressed_image).convert('L')
    root = tk.Tk()
    root.title("Confronto Originale e Compressa")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7))

    ax1.imshow(original_image, cmap="gray", interpolation="nearest")
    ax1.set_title("Immagine Originale")
    ax1.axis("off")

    ax2.imshow(compressed_image, cmap="gray", interpolation="nearest", vmin=0, vmax=255)
    ax2.set_title("Immagine Ricostruita")
    ax2.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()



def start():
    result = check_input_values()
    if not result:
        return

    F, d = result
    blocks = divide_image_into_blocks(F)

    dct2_result = run_dct2_and_round(blocks,F,d)

    reconstructed = run_idct2(dct2_result)

    new_path = reconstruct_image(reconstructed,F)

    show_comparison(path,new_path)
    


def run_dialog():
    global entry_file_path, entry_f, entry_d, label_dim

    def on_closing():

        root.destroy()
        root.quit()

    # Usa ThemedTk per applicare il tema
    root = ThemedTk(theme="plastik")
    root.title("Selezione file e parametri")

    frame_file = ttk.Frame(root)
    frame_file.pack(padx=10, pady=10)

    btn_scegli = ttk.Button(frame_file, text="Scegli file", command=open_file_system,style="Material.TButton")
    btn_scegli.pack(side=tk.LEFT)

    entry_file_path = ttk.Entry(frame_file, width=50, state='readonly')
    entry_file_path.pack(side=tk.LEFT, padx=(5, 0))

    frame_dim = ttk.Frame(root)
    frame_dim.pack(padx=10, pady=5)
    label_dim = ttk.Label(frame_dim, text="Dimension: ")
    label_dim.pack(side=tk.LEFT)

    frame_f = ttk.Frame(root)
    frame_f.pack(padx=10, pady=5)
    label_f = ttk.Label(frame_f, text="F:")
    label_f.pack(side=tk.LEFT)

    entry_f = ttk.Entry(frame_f)
    entry_f.pack(side=tk.LEFT)

    frame_d = ttk.Frame(root)
    frame_d.pack(padx=10, pady=5)
    label_d = ttk.Label(frame_d, text="d:")
    label_d.pack(side=tk.LEFT)

    entry_d = ttk.Entry(frame_d)
    entry_d.pack(side=tk.LEFT)

    btn_avvia = ttk.Button(root, text="Avvia", command=start,style="Material.TButton")
    btn_avvia.pack(pady=10)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


