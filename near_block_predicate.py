import json 
from tkinter import *
from tkinter.ttk import *
import math

TEST_FUNCTION_TEMPLATE = """setblock ~{} ~{} ~{} minecraft:red_stained_glass\n"""

WINDOW_WIDTH = 550
WINDOW_HEIGHT = 500
WIDGET_WIDTH = 35
class PredicateGenerator():

    def __init__(self):
        self.predicate = {
            "condition": "minecraft:alternative",
            "terms": []
        }
    
    def generate_diamond(self, block, distance, height=None, distanceZ=None, with_test_function=False):
        """ Generates a predicate to check in a diamond-shaped area.

        @param block: the block object to be checked, includes state, tag, or ID.\n
        @param distance: the "radius" of the pyramid, or its size\n
        @param height (optional): how tall the pyramid should be. By default it is the same as distance
        @param distanceZ (optional): affects the Z size of the pyramid. If specified, distance is treated as the X-size. 
        By default is same as distance\n
        @param with_test_function (default=False): A boolean that determines whether or not to also output a .mcfunction
        file that will generate a test size area. 
        """
        # check parameters
        if distanceZ == None:
            distanceZ = distance
        
        if height == None:
            height = distance

        # validate block id 
        # TODO: maybe validate this in the GUI code
        try:
            name = block.get('tag', block['id'])
        except KeyError:
            raise Exception('A block id or tag must be specified!')
        if name.count(':') > 1:
            raise Exception('Invalid namespaced id or tag!')

        if with_test_function:
            test_function = open('near_' + name.split(':')[-1] + '.mcfunction', 'w')

        # generate the predicate
        for dy in range (-height, height + 1):
            width = distance - abs(dy) # decrease width as we move away from the centre
            for dx in range(-width, width + 1):
                for dz in range(-width, width + 1):
                    self.predicate["terms"].append({
                        "condition": "minecraft:location_check",
                        "offsetX": dx,
                        "offsetY": dy,
                        "offsetZ": dz,
                        "predicate": {
                            "block": block
                        }
                    })

                    if with_test_function:
                        if (dx == 0 and dy == 0 and dz == 0) and (block.get('id', None) != None):
                            test_function.write("setblock ~{} ~{} ~{} ".format(dx, dy, dz) + name + '\n')
                        else:
                            test_function.write(TEST_FUNCTION_TEMPLATE.format(dx, dy, dz))

        if with_test_function:
            test_function.close()
        outfile = open('near_' + name.split(':')[-1] + '.json', 'w')
        outfile.write(json.dumps(self.predicate, sort_keys=True, indent=4))
        outfile.close()
    # === end generate diamond ===
# === end generator class ===

# === start GUI glass definitions ===
class GUI:
    def __init__(self, window):
        self.shapes = ['Diamond', 'Pyramind', 'Cuboid', 'Sphere']

        self.block_entry = LabelledEntry(window, 'Block (tag or ID):', 0, 0, with_namespace=True)
        self.state_entry = LabelledEntry(window, 'Block State (list, optional):', 1, 0)
        self.shape_entry = LabelledCombobox(window, 'Shape:', 2, 0, self.shapes)

        self.size_entry = LabelledEntry(window, 'Size:', 3, 0)
        self.height_entry = LabelledEntry(window, 'Height (optional):', 4, 0)
        self.size_entry = LabelledEntry(window, 'Z-Size (optional):', 5, 0)

        self.info_string = """Block state must be a list of block state values, 
as you would put them in a setblock command.

For example, for a campfire you might put: 
signal_fire=true,lit=false

Do not include any brackets or spaces.    
"""
        self.info_label = Label(window, text=self.info_string)
        self.info_label.grid(row=6,column=0, columnspan=2)


        self.load_settings_entry = LabelledEntry(window, 'Load Settings from file', 7, 0)
        self.load_settings_button = Button(window, text='Load', command= lambda : self.load_settings())
        self.load_settings_button.grid(row=7, column=2, sticky=(E, W))

        self.save_settings_entry = LabelledEntry(window, 'Load Settings from file', 7, 0)
        self.save_settings_button = Button(window, text='Load', command= lambda : self.load_settings())
        self.save_settings_button.grid(row=7, column=2, sticky=(E, W))

    def save_settings(self):
        pass
    
    def load_settings(self):
        pass

    def read_data(self):
        pass

class LabelledWidget:
    def __init__(self, parent, label_text, row, col):
        self.parent = parent
        self.row = row
        self.col = col

        self.label_frame = Frame(parent, borderwidth=8, relief=RIDGE)
        self.label_frame.grid(row=row, column=col)

        self.widget_frame = Frame(parent, borderwidth=8, relief=RIDGE)
        self.widget_frame.grid(row=row, column=col + 1)

        self.label_text = label_text
        self.label = Label(self.label_frame, text=self.label_text)
        self.label.grid(row=row, column=col)
        self.label.config(width=int(WIDGET_WIDTH))
        


class LabelledCombobox(LabelledWidget):
    def __init__(self, parent, label_text, row, col, values):
        super().__init__(parent, label_text, row, col)
        self.values = values
        self.combobox = Combobox(self.widget_frame, values=values, width=WIDGET_WIDTH - 2, state='readonly')
        self.combobox.grid(row=row, column=col+1)
        self.combobox.current(0)


class LabelledEntry(LabelledWidget):
    def __init__(self, parent, label_text, row, col, with_namespace=False):
        super().__init__(parent, label_text, row, col)

        self.entry = Entry(self.widget_frame, width= int(WIDGET_WIDTH))
        self.entry.grid(row=row, column=col + 1)

        if with_namespace:
            self.entry.grid(row=row, column=col + 3)
            self.colon_label = Label(self.widget_frame, text=':')
            self.colon_label.grid(row=row, column=col + 2)
            self.namespace_entry = Entry(self.widget_frame, width=int(WIDGET_WIDTH/2))
            self.namespace_entry.grid(row=row, column=col)
            self.namespace_entry.insert(END, 'minecraft')

            self.entry.config(width=int(WIDGET_WIDTH/2))
# === end GUI glass definitions ===

def gui():
    window = Tk()
    window.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT))
    window.title('Near Block Predicate Generator')
    gui = GUI(window)
    window.mainloop()

def command_terminal():
    block_name = input('Enter block name: ')
    distance = int(input('Enter distance: '))

    block = {
        'id': block_name
    }
    # generate_diamond(block, distance, with_test_function=True)

    exit_token = input('Press ENTER to exit...')

if __name__ == '__main__':
    # pass
    
    gui()
    # command_terminal()

    