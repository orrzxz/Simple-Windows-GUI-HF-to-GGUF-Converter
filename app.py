import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import sys
from huggingface_hub import snapshot_download

class GGUFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HF to GGUF Converter")
        
        # Configure paths
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.llama_dir = os.path.join(self.app_dir, "llama.cpp")
        self.output_base_dir = os.path.join(self.app_dir, "Converted")
        
        # Create required directories
        os.makedirs(self.output_base_dir, exist_ok=True)
        
        # GUI Setup
        ttk.Label(root, text="Hugging Face Model Name:").pack(padx=10, pady=5)
        self.model_entry = ttk.Entry(root, width=60)
        self.model_entry.pack(padx=10, pady=5)
        
        self.convert_btn = ttk.Button(root, text="Convert", command=self.start_conversion)
        self.convert_btn.pack(pady=10)
        
        self.log_text = tk.Text(root, height=20, width=100, state=tk.DISABLED)
        self.log_text.pack(padx=10, pady=10)
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")

    def log(self, message, tag=None):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_conversion(self):
        model_name = self.model_entry.get().strip().replace("https://huggingface.co/", "")
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name")
            return
            
        self.convert_btn.config(state=tk.DISABLED)
        threading.Thread(
            target=self.convert_model,
            args=(model_name,),
            daemon=True
        ).start()

    def convert_model(self, model_name):
        try:
            # Create output directory
            output_model_dir = os.path.join(self.output_base_dir, model_name.replace("/", "--"))
            os.makedirs(output_model_dir, exist_ok=True)
            output_file = os.path.join(output_model_dir, "model.f16.gguf")

            # Step 1: Download model
            self.log("[1/2] Downloading model...", "success")
            model_path = snapshot_download(
                repo_id=model_name,
                resume_download=True,
                local_files_only=False
            )

            # Step 2: Convert to GGUF
            self.log("[2/2] Converting to GGUF...", "success")
            convert_script = os.path.join(self.llama_dir, "convert_hf_to_gguf.py")
            
            if not os.path.exists(convert_script):
                raise FileNotFoundError(f"llama.cpp not found at: {self.llama_dir}")

            # Simplified conversion command
            convert_cmd = [
                sys.executable,
                convert_script,
                model_path,
                "--outtype", "f16",
                "--outfile", output_file,
                "--model-name", os.path.basename(model_name)
            ]

            process = subprocess.Popen(
                convert_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.llama_dir
            )
            
            # Capture output
            while True:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())

            if process.returncode != 0:
                raise RuntimeError("Conversion failed - check log for details")

            self.log(f"\nSuccess! GGUF saved to:\n{output_file}", "success")
            messagebox.showinfo("Done", f"Model saved in:\n{output_model_dir}")

        except Exception as e:
            self.log(f"\nERROR: {str(e)}", "error")
            messagebox.showerror("Error", str(e))
        finally:
            self.convert_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = GGUFConverterApp(root)
    root.mainloop()