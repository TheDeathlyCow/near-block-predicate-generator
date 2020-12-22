import json 
from tkinter import *
from tkinter.ttk import *
import math

TEST_FUNCTION_TEMPLATE = """setblock ~{} ~{} ~{} minecraft:red_stained_glass\n"""

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

class GUI:
    def __init__(self, window):
        pass


class TextEntry:
    def __init__(self, parent, label_text, row, col, with_namespace=False):

        self.label_frame = Frame(parent, borderwidth=8, relief=RIDGE)
        self.label_frame.grid(row=row, column=col)

        self.entry_frame = Frame(parent, borderwidth=8, relief=RIDGE)
        self.entry_frame.grid(row=row, column=col + 1)

        self.label_text = label_text
        self.label = Label(self.label_frame, text=self.label_text)
        self.label.grid(row=row, column=col, padx=5)

        self.entry = Entry(self.entry_frame, width=15)
        self.entry.grid(row=row, column=col + 1, padx=5)

        if with_namespace:
            self.entry.grid(row=row, column=col + 3, padx=5)
            self.colon_label = Label(self.entry_frame, text=':')
            self.colon_label.grid(row=row, column=col + 2)
            self.namespace_entry = Entry(self.entry_frame, width=15)
            self.namespace_entry.grid(row=row, column=col, padx=5)
            self.namespace_entry.insert(END, 'minecraft')
            
        
        

class LabelledEntry:
    def __init__(self, parent, text, row, col):
        self.label_text = text
        self.label = Label(parent, text=text)
        self.label.grid(row=row, column=col, padx=2)

        self.entry = Entry(parent, width=15)
        self.entry.grid(row=row, column=col+1, padx=2)
def gui():
    window = Tk()
    window.geometry('500x200')

    gui = TextEntry(window, 'test', 0, 0, True)
    window.mainloop()

def command_terminal():
    block_name = input('Enter block name: ')
    distance = int(input('Enter distance: '))

    block = {
        'id': block_name
    }
    generate_diamond(block, distance, with_test_function=True)

    exit_token = input('Press ENTER to exit...')

if __name__ == '__main__':
    # pass
    
    gui()
    # command_terminal()

    