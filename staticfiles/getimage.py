import os

# Define the path to the correct folder containing images (shop/static/shop)
folder_path = os.path.join(os.getcwd(), 'shop', 'static', 'shop')

# Check if the folder exists
if os.path.exists(folder_path):
    # Get the list of image filenames in the folder
    image_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Print the list of image filenames
    print(image_names)
else:
    print(f"The folder {folder_path} does not exist.")
