import tkFileDialog
import os


def traversal_del(rootDir,f_ext):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            name,ext = f.split(".")
            if ext == f_ext:
                os.remove(os.path.join(root,f))
                print "deleted file:",os.path.join(root,f)
                
if __name__ == '__main__':
    traversal_del("./logs","png")
    #traversal_del("./logs","sol")
    raw_input("press any key to exit")

# plot_f(f_out,"green")
