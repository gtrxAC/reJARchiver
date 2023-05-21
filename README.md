# reJARchiver
Effort to analyze and clean up [J2ME archives](https://archive.org/download/J2MEarchivesMay2020).

[Original idea](https://docs.google.com/document/d/16Jjg64qgWixwob7FTYOnBwxEqv3hWZ4DfNn_DyWcpfk/edit?usp=sharing)

## Structure
So far the procedure consists of 4 Python scripts:

### 1. Extract
Recursively extract ZIP, 7Z and RAR archives.

### 2. Index
Create a JSON index of all JARs found, including their hashes and manifest data.

We also need to check if the JARs are valid J2ME midlets, since some of them can be broken files, Java desktop apps, or libraries.

### 3. Filter
Remove entries from the index that show signs of modification by third parties (such as pirate sites that put their own name on the manifest - we call these "bad keywords").

At the same time, we also do de-duping of files based on the hashes.

### 4. Sort
Sort each JAR file into directories based on the app's name, and use a standard naming scheme, so variants of the same game are easy to find.