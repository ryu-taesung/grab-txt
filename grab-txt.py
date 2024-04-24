try:
    import pyi_splash
except:
    pass
import sys
from time import sleep
def update_splash(msg):
    if getattr(sys, 'frozen', False):
        sleep(0.1)
        pyi_splash.update_text(msg)

# from: https://stackoverflow.com/a/58130065
update_splash('importing tkinter . . .')
import tkinter as tk
update_splash('importing pillow . . .')
from PIL import ImageGrab, ImageTk, Image, ImageEnhance
update_splash('importing subprocess . . .')
from subprocess import run as _run, PIPE as _PIPE #STARTUPINFO as _STARTUPINFO, STARTF_USESHOWWINDOW as _STARTF_USESHOWWINDOW
update_splash('importing io . . .')
from io import BytesIO as _BytesIO
#update_splash('importing pystray . . .')
#import pystray
#from pystray import MenuItem as item
update_splash('importing os . . .')
from os import path as _path, name as _name
update_splash('import threading . . .')
from threading import Thread as _Thread
from time import sleep as _sleep

class ScreenGrabWindow(tk.Toplevel):
    def __init__(self, grab_button):
        super().__init__()
        self.withdraw()
        self.grab_button = grab_button
        self.grab_button.config(state=tk.DISABLED)
        self.update()
        self.t1 = _Thread()

        self.canvas = tk.Canvas(self, cursor="crosshair")
        self.canvas.pack(fill="both",expand=True)

        #screencapture_command = ['screencapture', '-x', '-R', bbox_str, '/tmp/screenshot.png']
        screencapture_command = ['grim', '/tmp/screenshot.png']
        _run(screencapture_command, shell=False)
        self.screenshot_image = Image.open('/tmp/screenshot.png')
        self.image = ImageTk.PhotoImage(self.screenshot_image)
        self.photo = self.canvas.create_image(0,0,image=self.image,anchor="nw")
        self.x, self.y = 0, 0
        self.rect, self.start_x, self.start_y = None, None, None
        self.deiconify()
        self.geometry(f"{self.screenshot_image.width}x{self.screenshot_image.height}")
        self.attributes('-fullscreen', True)

        self.canvas.tag_bind(self.photo,"<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.photo,"<B1-Motion>", self.on_move_press)
        self.canvas.tag_bind(self.photo,"<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, width='2', outline='green')

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        bbox = self.canvas.bbox(self.rect)
        self.withdraw()
        if self.t1.is_alive():
            return
        self.t1 = _Thread(target=self.image_processing_thread, args=(bbox,))
        self.t1.start()
        
    def image_processing_thread(self, bbox):
#        _sleep(1)
#        # bbox format should be "x,y widthxheight"        
#        bbox_str = f"{bbox[0]},{bbox[1]} {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}"
#        scrot_command = ['grim','-g',bbox_str,'/tmp/screenshot_rect.png']
#        _run(scrot_command, shell=False)
# Load the image from the file saved by scrot
#        screen_grab = Image.open('/tmp/screenshot_rect.png')
        cropped_image = self.screenshot_image.crop(bbox)        

        # Image processing
        larger = cropped_image.resize((cropped_image.width * 3, cropped_image.height * 3))
        larger = larger.convert('L')
        buf = _BytesIO()
        contrast = ImageEnhance.Contrast(larger)
        contrast.enhance(2).save(buf, format='PNG', dpi=(300, 300))
        image_bytes = buf.getvalue()

        # Update the GUI with the new image
        self.new_image = ImageTk.PhotoImage(cropped_image)
        self.attributes('-fullscreen', False)
        self.title("Image grabbed")
        self.canvas.destroy()
        self.deiconify()
        tk.Label(self, image=self.new_image).pack()   
        self.geometry(f"{cropped_image.width}x{cropped_image.height}")     

        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
            tess = _path.join(application_path, "Tesseract-OCR", "tesseract.exe --psm 4 stdin stdout")
        else:
            tess = ("/usr/bin/tesseract","--psm","4","stdin","stdout")
        print(f'tess: {tess}')
        #tess = r"c:\Program Files\Tesseract-OCR\tesseract.exe --psm 4 stdin stdout"
        self.update()
        
        #prevent program console from displaying, from: https://stackoverflow.com/a/1016651
        startupinfo = None
        if _name == 'nt':
            startupinfo = _STARTUPINFO()
            startupinfo.dwFlags |= _STARTF_USESHOWWINDOW

        rc = _run(
            tess,
            input=image_bytes,
            stdout=_PIPE,
            stderr=None,
            shell=False,
            startupinfo=startupinfo
        )
        text = rc.stdout.decode()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.after(750, self.withdraw)
        self.grab_button.config(state=tk.NORMAL)

    def close_window(self):
        self.destroy()

class MainMenu(tk.Menu):
    def __init__(self):
        super().__init__()
        file = tk.Menu(self, tearoff=False)
        file.add_command(label="Exit", command=self.quit)
        self.add_cascade(label="File", underline=0, menu=file)
        options = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Options", underline=0, menu=options)

class Application(tk.Tk):
    def __init__(self, title):
        super().__init__()
        self.wm_attributes('-alpha', 0)
        if getattr(sys, 'frozen', False): #https://stackoverflow.com/a/45631436
            self.application_path = sys._MEIPASS
            try:
                with open(_path.join(self.application_path,'version.txt'), 'r') as file:
                    self.version_number = file.read()
            except:
                self.version_number = "ERR"
        elif __file__:
            self.application_path = _path.dirname(__file__)
            try:
                import get_git_version_tag
            
                self.version_number = get_git_version_tag.get_git_version_tag()
            except:
                self.version_number = "vEXP"

        self.grab_window = None
        self.icon = None
        self.resizable(0,0)
        icon = Image.open(_path.join(self.application_path, 'icons', 'smiley-glass.png'))
        img = ImageTk.PhotoImage(icon)
        self.call('wm', 'iconphoto', self._w, img)
        self.title(f'{title} {self.version_number}')
        menubar = MainMenu()
        self.config(menu=menubar)
        #self.geometry('200x90')
        self.grab_button = tk.Button(self, text="Screenshot to Grab Text", command=self.create_screen_grabber, padx="10", pady="10")
        self.grab_button.pack(fill="both", expand=True, padx="20", pady="20")
        #if sys.platform == 'win32':
        #    self.protocol('WM_DELETE_WINDOW', self.hide_window) #on close window
        update_splash('Done!')
        self.wm_attributes('-alpha', 1)

    def create_screen_grabber(self):
        if self.grab_window:
            self.grab_window.close_window()
        self.grab_window = ScreenGrabWindow(self.grab_button)

    #def quit_window(self, icon, item):
    #    self.icon.stop()
    #    self.destroy()

    #def show_window(self, icon, item):
    #    print('show')
    #    self.icon.stop()
    #    self.after(0,self.deiconify)

    #def hide_window(self, *args, **kwargs):
    #    self.withdraw()
        #print('minimized')
    #    image = Image.open(_path.join(self.application_path, "icon.png"))
    #    menu=(item('Show Window', self.show_window), item('Exit', self.quit_window), )
    #    self.icon = pystray.Icon('text_grabber', image, 'Text Grabber', menu=menu)
    #    self.icon.run()

root = Application("Text Grabber")

root.attributes('-topmost', True)
root.after_idle(root.focus_force)
root.after_idle(root.attributes, '-topmost', False)

if getattr(sys, 'frozen', False):
    root.after(1200,pyi_splash.close)

root.mainloop()
