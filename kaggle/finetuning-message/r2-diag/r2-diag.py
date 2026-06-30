import os, glob
print(">>> /kaggle/input exists:", os.path.exists("/kaggle/input"), flush=True)
print(">>> listdir /kaggle/input:", os.listdir("/kaggle/input") if os.path.exists("/kaggle/input") else "N/A", flush=True)
print(">>> glob */sequences.csv:", glob.glob("/kaggle/input/*/sequences.csv"), flush=True)
print(">>> glob **/sequences.csv:", glob.glob("/kaggle/input/**/sequences.csv", recursive=True), flush=True)
