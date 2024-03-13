import os
import sys
import tkinter as tk
import subprocess
from tkinter import filedialog, simpledialog, messagebox, Button
import time

def install_dependencies():
    libraries = ["Pillow", "pandas"]
    for lib in libraries:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {lib}. Error: {e}")

def attempt_imports():
    try:
        global pd, Image, ImageDraw, ImageFont, ImageTk
        import pandas as pd
        from PIL import Image, ImageDraw, ImageFont, ImageTk
        return True
    except ImportError as e:
        print("Missing required libraries. Installing...")
        install_dependencies()
        return False
    
# Attempt to import the libraries. If imports fail, install the dependencies and try one more time.
if not attempt_imports():
    print("Attempting to import libraries again after installation.")
    if not attempt_imports():  # Try to import again after installation.
        print("Failed to import libraries after installation attempts.")
        sys.exit(1)

def select_image_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    dir_path = filedialog.askdirectory(title='SELECT IMAGE DIRECTORY...')
    return dir_path

# select csv file function:
def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    csv_path = filedialog.askopenfilename(title='SELECT PHOTODATA.CSV...')
    # if not a CSV, return None
    if not csv_path.endswith('.csv'):
        return None
    return csv_path

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within a given width when rendered."""
    # print("MAX WIDTH: ", max_width)
    # print("TEXT: ", text)
    lines = []
    for line in text.split('\n'):
        # print("\nLINE: ", line)
        # print("LENGTH: ", draw.textlength(line, font=font))

        if draw.textlength(line, font=font) <= max_width:
            lines.append(line)
        else:
            # if too long, split into words
            words = line.split()
            i = 0
            current_line = ''
            while i < len(words):
                # Check if adding another word exceeds the max width
                test_line = current_line + ' ' + words[i] if current_line else words[i] # if current_line is empty, then just add the word first

                if draw.textlength(test_line, font=font) <= max_width:
                    current_line = test_line
                    i += 1
                else:
                    # if adding the next word exceeds the max width, add the current line and reset. HOWEVER this will not work if the word is longer than the max width. So, we need to check if the word is longer than the max width
                        
                    if current_line:  # Ensure there's something to add before resetting
                        lines.append(current_line)

                    # we know the word hasn't been added to the current line: so we need to check if the word itself is longer than the max width
                    if draw.textlength(words[i], font=font) > max_width:
                        lines.append(words[i])
                        i += 1

                    current_line = ''
                    
            if current_line:  # Add any remaining text (here, length is guaranteed to be less than max_width)
                lines.append(current_line)
    return lines

def annotate_image(image_path, left_text, right_text, output_path):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        width, height = img.size
        font_size = int(min(width, height) // 40)
        margin = font_size
        font = ImageFont.truetype("arialbd.ttf", size=font_size)

        max_text_width = width // 2 - margin # // is floor division
        wrapped_left_text = wrap_text(left_text, font, max_text_width, draw)
        wrapped_right_text = wrap_text(right_text, font, max_text_width, draw)

        # Calculate text height for positioning
        left_text_height = sum(font_size for line in wrapped_left_text)
        right_text_height = sum(font_size for line in wrapped_right_text)

        # Initial position for left, right text
        left_text_position = (margin, height - margin - left_text_height)
        right_text_position = (width - margin, height - margin - right_text_height)

        # Draw left text
        for line in wrapped_left_text:
            draw.text((left_text_position[0]+3, left_text_position[1]+3), line, fill="black", font=font)
            draw.text(left_text_position, line, fill="white", font=font)

            left_text_position = (left_text_position[0], left_text_position[1] + font_size)
        
        # Draw right text
        for line in wrapped_right_text:
            text_width = draw.textlength(line, font=font)
            right_text_x = width - margin - text_width  # Calculate X so that text ends at the right margin
            draw.text((right_text_x+3, right_text_position[1]+3), line, fill="black", font=font)
            draw.text((right_text_x, right_text_position[1]), line, fill="white", font=font)
            right_text_position = (right_text_x, right_text_position[1] + font_size)

        img.save(output_path)




tkinter_running = True
root = tk.Tk()

root.withdraw()  # Hide the main window
def on_quit():
    global tkinter_running
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        tkinter_running = False
        root.destroy()
        sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_quit)

def select_starting_image(image_dir):
    image_list = [filename for filename in os.listdir(image_dir) if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not image_list:
        return None

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    starting_image = filedialog.askopenfilename(initialdir=image_dir, title='MANUAL: SELECT STARTING IMAGE...', filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.gif')])
    if not starting_image:
        return None

    return os.path.basename(starting_image)



def show_image_and_get_input(image_path, default_location="", default_comment="", default_photographer="", default_address=""):
    if not tkinter_running:
        return None, None, None, None, None, None, None, None  # Exit function if tkinter_running is False
    
    # Variables to hold input values
    default_location_input = None
    default_comment_input = None
    default_photographer_input = None
    default_address_input = None
    location_input = None
    comment_input = None
    photographer_input = None
    address_input = None

    def on_window_close():
        nonlocal photo
        label.config(image=None)
        photo = None
        tk_window.destroy()
    
    def delete_and_continue():
        nonlocal location_input, comment_input, photographer_input, address_input, default_location_input, default_comment_input, default_photographer_input, default_address_input
        location_input = "DELETE"
        comment_input = "DELETE"
        photographer_input = "DELETE"
        address_input = "DELETE"
        default_location_input = default_location
        default_comment_input = default_comment
        default_photographer_input = default_photographer
        default_address_input = default_address
        on_window_close()

    def save_and_continue():
        nonlocal location_input, comment_input, photographer_input, address_input, default_location_input, default_comment_input, default_photographer_input, default_address_input

        # Retrieve input from entry fields
        default_location_input = default_location_entry.get()
        default_comment_input = default_comment_entry.get()
        default_photographer_input = default_photographer_entry.get()
        default_address_input = default_address_entry.get()

        location_input = location_entry.get()
        comment_input = comment_entry.get()
        photographer_input = photographer_entry.get()
        address_input = address_entry.get()
        on_window_close()

    # Create a top-level window
    tk_window = tk.Toplevel(root)
    tk_window.title(os.path.basename(image_path))
    tk_window.protocol("WM_DELETE_WINDOW", on_quit)  # Set the same quit protocol for the Toplevel window

    # Disable window resizing
    tk_window.resizable(False, False)

    # Open and display the image
    image = Image.open(image_path)
    # if the image is vertically oriented, rotate it
    if image.height > image.width:
        image = image.rotate(90, expand=True)

    image = image.resize((800, image.height * 800 // image.width), Image.LANCZOS)

    photo = ImageTk.PhotoImage(image)

    # Set the window size and position
    window_width = round(image.width )
    window_height = round(image.height+100)
    screen_width = tk_window.winfo_screenwidth()
    screen_height = tk_window.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    tk_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")


    label = tk.Label(tk_window, image=photo)
    label.pack()



    # Keep a reference to the photo object to prevent garbage collection
    # label.image = photo

    # Create frames for each input group
    address_frame = tk.Frame(tk_window)
    address_frame.pack(side=tk.LEFT, padx=5, pady=5)

    location_frame = tk.Frame(tk_window)
    location_frame.pack(side=tk.LEFT, padx=5, pady=5)

    comment_frame = tk.Frame(tk_window)
    comment_frame.pack(side=tk.LEFT, padx=5, pady=5)

    photographer_frame = tk.Frame(tk_window)
    photographer_frame.pack(side=tk.LEFT, padx=5, pady=5)

    # Address
    address_label = tk.Label(address_frame, text="Address:")
    address_label.pack(side=tk.TOP, anchor="w")
    address_entry = tk.Entry(address_frame)
    address_entry.pack(side=tk.TOP)
    address_entry.insert(0, default_address)  # Preset the default address

    # Default Address
    default_address_label = tk.Label(address_frame, text="Default Address:")
    default_address_label.pack(side=tk.TOP, anchor="w")
    default_address_entry = tk.Entry(address_frame)
    default_address_entry.pack(side=tk.TOP)
    default_address_entry.insert(0, default_address)  # Preset the default address

    # Location
    location_label = tk.Label(location_frame, text="Location:")
    location_label.pack(side=tk.TOP, anchor="w")
    location_entry = tk.Entry(location_frame)
    location_entry.pack(side=tk.TOP)
    location_entry.insert(0, default_location)  # Preset the default location

    # Default Location
    default_location_label = tk.Label(location_frame, text="Default Location:")
    default_location_label.pack(side=tk.TOP, anchor="w")
    default_location_entry = tk.Entry(location_frame)
    default_location_entry.pack(side=tk.TOP)
    default_location_entry.insert(0, default_location)  # Preset the default location

    # Comment
    comment_label = tk.Label(comment_frame, text="Comment:")
    comment_label.pack(side=tk.TOP, anchor="w")
    comment_entry = tk.Entry(comment_frame)
    comment_entry.pack(side=tk.TOP)
    comment_entry.insert(0, default_comment)  # Preset the default comment

    # Default Comment
    default_comment_label = tk.Label(comment_frame, text="Default Comment:")
    default_comment_label.pack(side=tk.TOP, anchor="w")
    default_comment_entry = tk.Entry(comment_frame)
    default_comment_entry.pack(side=tk.TOP)
    default_comment_entry.insert(0, default_comment)  # Preset the default comment

    # Photographer
    photographer_label = tk.Label(photographer_frame, text="Photographer:")
    photographer_label.pack(side=tk.TOP, anchor="w")
    photographer_entry = tk.Entry(photographer_frame)
    photographer_entry.pack(side=tk.TOP)
    photographer_entry.insert(0, default_photographer)  # Preset the default photographer

    # Default Photographer
    default_photographer_label = tk.Label(photographer_frame, text="Default Photographer:")
    default_photographer_label.pack(side=tk.TOP, anchor="w")
    default_photographer_entry = tk.Entry(photographer_frame)
    default_photographer_entry.pack(side=tk.TOP)
    default_photographer_entry.insert(0, default_photographer)  # Preset the default photographer

    # Create a "Save" or "OK" button that retrieves input and closes the window
    save_button = tk.Button(tk_window, text="Save", command=save_and_continue)
    save_button.pack(side=tk.LEFT, padx=5)

    # Create a "Delete" button that deletes the current photo and moves to the next one
    delete_button = tk.Button(tk_window, text="Delete", command=delete_and_continue)
    delete_button.pack(side=tk.RIGHT, padx=5)

    tk_window.wait_window()  # Wait here until the window is closed

    return location_input, comment_input, photographer_input, address_input, default_location_input, default_comment_input, default_photographer_input, default_address_input

def main():
    print('\n')

    print("                 ████████████████                 ")
    print("             ████████████████████████             ")
    print("          ██████████████████████████████          ")
    print("        ██████████████████████████████████        ")
    print("       ████████   ██████████████   █████████      ")
    print("      █████████   ██████████████    ████████      ")
    print("    ██████████     ████████████     ██████████    ")
    print("    █████████       ██████████       █████████    ")
    print("    ████████    █   ██████████   █    ████████    ")
    print("    ███████    ███    ██████    ███    ███████    ")
    print("    ██████    █████    ████    █████    ██████    ")
    print("    █████   █████████    ███ █████████   █████    ")
    print("    █████ █████████████    █████████████ █████    ")
    print("      █████████████   ███      ██████████████     ")
    print("      █████████       ██████       █████████      ")
    print("        ███████   ███████████████  ███████        ")
    print("          ██████████████████████████████          ")
    print("             ████████████████████████             ")
    print("                 ████████████████                 ")

    print('\n')
    print("PHOTO ANNOTATOR V.0.5")
    print("Implemented by Kelvin Filyk")
    print("Municon West Coast")
    print('\n')

    print('---------------')

    images_dir = select_image_directory()

    if not images_dir:
        print("No input image directory selected, exiting...")
        return
    
    prints_dir = os.path.join(images_dir, "../Prints")
    # Create 'Prints' directory if it doesn't exist
    if not os.path.exists(prints_dir):
        os.makedirs(prints_dir)


    print("Choose CSV [FileName, Date, Photographer, Location, Comment]: ")
    csv_path = select_csv_file()
    if not csv_path:
        print("\nNO CSV SELECTED: Assuming manual input. ")
        # prompt for the starting image
        starting_image = select_starting_image(images_dir)
        starting_index = -1
        # show all images side by side in a pop up window
        global default_location, default_comment, default_photographer, default_address
        default_address = ""
        default_location = ""
        default_comment = "General Condition"
        default_photographer = ""
        image_index = 1
        for filename in os.listdir(images_dir):

            if (starting_image and filename == starting_image):
                starting_image = None  # Reset starting_image to process the remaining images
                starting_index = image_index

            if starting_image:
                image_index += 1
                continue  # while starting image is not 'None' Skip images until the starting image is found

            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                print(f"\nANNOTATING {filename}:")

                image_path = os.path.join(images_dir, filename)
                location, comment, photographer, address, default_location, default_comment, default_photographer, default_address = show_image_and_get_input(image_path, default_location, default_comment, default_photographer, default_address)

                if location == "DELETE" and comment == "DELETE":
                    print(f"Deleting {filename} and moving to the next image.")
                    os.remove(image_path)
                    continue


                # At initializaiton, if someone forgets to set default and index == 1
                if image_index == starting_index:

                    if location.strip() == "":
                        location = default_location
                    if comment.strip() == "":
                        comment = default_comment
                    if photographer.strip() == "":
                        photographer = default_photographer
                    if address.strip() == "":
                        address = default_address

                    if default_location.strip() == "":
                        default_location = location
                    if default_comment.strip() == "":
                        default_comment = comment
                    if default_photographer.strip() == "":
                        default_photographer = photographer
                    if default_address.strip() == "":
                        default_address = address

                output_name = address+"_"+str(image_index)+".jpg"
                output_name = output_name.replace(" ", "_")
                output_path = os.path.join(prints_dir, output_name)
                
                # set date to now
                date = ""
                # try/catch set date of image from metadata

                try:
                    date = Image.open(image_path)._getexif()[36867]
                except:
                    date = time.strftime("%H:%M:%S", time.localtime())
                left_text = f"{output_name}\n{location}\n{comment}"
                right_text = f"{photographer}\nMunicon West Coast\n{date}"
                annotate_image(image_path, left_text, right_text, output_path)
                print(f"Annotated image saved: {output_path}")
                image_index += 1



        return
    else:
        df = pd.read_csv(csv_path)

        for index, row in df.iterrows():
            filename = row.get('SourceFile') or row.get('FileName', '')  # Use 'SourceFile' if it exists, else use 'FileName'
            image_path = os.path.join(images_dir, filename)
            default_date = Image.open(image_path)._getexif()[36867]
            output_path = os.path.join(prints_dir, filename)  # Adjust output path as required
            # if the column 'SourceFile' exists, then use the old form of CSV file

            left_text = ""
            right_text = ""

             # Check for SourceFile or FileName for left_text
            if not pd.isna(row.get('SourceFile', pd.NA)):
                left_text += str(row['SourceFile']) + "\n"
            elif not pd.isna(row.get('FileName', pd.NA)):
                left_text += str(row['FileName']) + "\n"


            # Additional fields appending to left_text or right_text

            # Do location next:
            if not pd.isna(row.get('Location', pd.NA)):
                left_text += str(row['Location']) + "\n"
            elif not pd.isna(row.get('ImageDescription', pd.NA)):
                right_text += str(row['ImageDescription']) + "\n"

            if not pd.isna(row.get('UserComment', pd.NA)):
                left_text += str(row['UserComment'])
            elif not pd.isna(row.get('Comment', pd.NA)):
                left_text += str(row['Comment'])

            if not default_date or pd.isna(default_date):
                if not pd.isna(row.get('DateTimeOriginal', pd.NA)):
                    right_text += str(row['DateTimeOriginal']) + "\n"
                elif not pd.isna(row.get('Date', pd.NA)):
                    right_text += str(row['Date']) + "\n"
                else:
                    right_text += "NO TIMESTAMP FOUND\n"
            else:
                # get date from the photo metadata as opposed to the csv file
                right_text += default_date + "\n"

            # artist
            if not pd.isna(row.get('Photographer', pd.NA)):
                right_text += str(row['Photographer']) + "\n"
            elif not pd.isna(row.get('Artist', pd.NA)):
                right_text += str(row['Artist']) + "\n"

            right_text += "Municon West Coast"

            if os.path.exists(image_path):
                annotate_image(image_path, left_text, right_text, output_path)
                print(f"Annotated image saved: {output_path}")
            else:
                print(f"Image not found: {image_path}")

if __name__ == "__main__":
    main()
