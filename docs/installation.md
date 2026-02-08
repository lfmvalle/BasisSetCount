[↩ README](../README.md) | [Information about atoms and unique basis sets ▶](usage_info.md)

# Installing the script

## 1. Requirements

This script requires `Python 3.14`. Check the version of your Python installation with `$ python --version`. <br>
It may work with older versions, but you'll have to manually edit the scripts to do so. Do it at **your own risk**.

## 2. Installation steps
1. Download all contents from [src folder](../src/);
2. Move the downloaded files to any directory of your choice;
3. The executable script is the [main.py file](../src/main.py). Make sure it has proper execution permissions;
4. Call the script using the interpreter: <br> `$ python3 path/to/main.py`. <br> It must output an error message asking for a CRYSTAL23 output file.

## 3. Tips
- If you are a Linux user, you can execute it directly with: <br> `$ . path/to/main.py`
- I strongly suggest using an alias to call the script anywhere, such as `basis` or `bscount`: <br> `$ bscount output_file [params]`