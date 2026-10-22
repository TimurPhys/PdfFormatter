import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["fitz", "pymupdf", "PyQt5"],
    "excludes": ["tkinter", "unittest", "email", "http", "xml", "onnxruntime", "numpy"],
}

base = "gui" if sys.platform == "win32" else None

setup(
    name="PDFProcessor",
    version="2.0",
    options={"build_exe": build_exe_options},
    executables=[Executable("gui.py", base=base, target_name="PDFProcessor.exe")]
)