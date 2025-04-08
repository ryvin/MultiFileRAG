import sys
import pandas
import numpy
import matplotlib
import seaborn
import lightrag
from unstructured.partition.auto import partition

print("Python version:", sys.version)
print("\nInstalled packages:")
print(f"pandas: {pandas.__version__}")
print(f"numpy: {numpy.__version__}")
print(f"matplotlib: {matplotlib.__version__}")
print(f"seaborn: {seaborn.__version__}")
print("lightrag is installed")
print("unstructured is installed")

print("\nMultiFileRAG environment is set up correctly!")
