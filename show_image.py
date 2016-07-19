from PIL import Image

im = Image.open("logs/FLY000.png")

print(im.format, im.size, im.mode)
im.show()


 
