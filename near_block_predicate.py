import json
from tkinter import *
from tkinter.ttk import *
import math
import re
import os


TEST_FUNCTION_TEMPLATE = """setblock ~{} ~{} ~{} minecraft:red_stained_glass\n"""

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 675
WIDGET_WIDTH = 35
INVALID_INPUT = "Invalid Input"
VALID_INPUT = ''


class PredicateGenerator():

    def __init__(self):
        self.predicate = {
            "condition": "minecraft:alternative",
            "terms": []
        }

    def generate(self, block, size, shape, height=None, zsize=None, with_test_function=False):
        """ Generates a predicate file.

        @param: block\n
        @param: size\n
        @param: shape\n
        @param: height\n
        @param: zsize\n
        @param: with_test_function
        """
        print(f'block: {block}')
        print(f'size: {size}')
        print(f'shape: {shape}')
        print(f'height: {height}')
        print(f'zsize: {zsize}')
        print(f'with_test_function: {with_test_function}')

        shape_name = shape.lower()
        if shape_name == 'diamond':
            self.generate_diamond(block, size, height,
                                  zsize, with_test_function)
        if shape_name == 'pyramid':
            self.generate_pyramid(block, size, height,
                                  zsize, with_test_function)

    def generate_pyramid(self, block, size, height=None, zsize=None, with_test_function=False):
        pass

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

        try:
            name = block.get('tag', block['block'])
        except KeyError:
            name = block.get('tag', block['tag'])

        if with_test_function:
            test_function = open('near_' + name.split(':')
                                 [-1] + '.mcfunction', 'w')

        # generate the predicate
        for dy in range(-height, height + 1):
            # decrease width as we move away from the centre
            width = distance - abs(dy)
            widthz = width
            if distanceZ != None:
                widthz = distanceZ - abs(dy)
            for dx in range(-width, width + 1):
                for dz in range(-widthz, widthz + 1):
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
                        test_function.write(
                            TEST_FUNCTION_TEMPLATE.format(dx, dy, dz))

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
        self.generator = PredicateGenerator()
        self.shapes = ['Diamond', 'Pyramind', 'Cuboid', 'Sphere']

        self.block_entry = LabelledEntry(
            window, '', 0, 0, with_namespace=True)
        self.block_entry.label = Combobox(self.block_entry.label_frame, width=int(
            WIDGET_WIDTH - 5), values=['Block ID', 'Block Tag'], state='readonly')
        self.block_entry.label.grid(row=0, column=0)
        self.block_entry.label.current(0)

        self.state_entry = LabelledEntry(
            window, 'Block State (list, optional):', 1, 0)
        self.shape_entry = LabelledCombobox(
            window, 'Shape:', 2, 0, self.shapes)

        self.size_entry = LabelledEntry(window, 'Size:', 3, 0)
        self.height_entry = LabelledEntry(window, 'Height (optional):', 4, 0)
        self.zsize_entry = LabelledEntry(window, 'Z-Size (optional):', 5, 0)

        self.include_test_function = LabelledCombobox(
            window, 'Include Test Function:', 6, 0, ['False', 'True'])

        self.info_string = """Block state must be a list of block state values, 
as you would put them in a setblock command.

For example, for a campfire you might put: 
signal_fire=true,lit=false

Do not include any brackets or spaces.    

The test function will generate red
stained glass around the player in
the same shape and size you select.
Be sure to remember put it in the 
functions folder!
"""
        self.info_label = Label(window, text=self.info_string)
        self.info_label.grid(row=7, column=0, columnspan=2)

        self.load_settings_entry = LabelledEntry(
            window, 'Load Settings from file', 8, 0)
        self.load_settings_button = Button(
            window, text='Load', command=lambda: self.load_settings())
        self.load_settings_button.grid(row=8, column=2, sticky=(E, W))

        self.save_settings_entry = LabelledEntry(
            window, 'Save Settings to file', 9, 0)
        self.save_settings_button = Button(
            window, text='Save', command=lambda: self.save_settings())
        self.save_settings_button.grid(row=9, column=2, sticky=(E, W))

        self.generate_button = Button(
            window, text='Generate', command=lambda: self.generate())
        self.generate_button.grid(
            row=10, column=0, sticky=(E, W), pady=15, columnspan=2)

        self.error_label = Label(
            window, text='', foreground='red', font=('Arial', 20))
        self.error_label.grid(row=11, column=0, pady=5)

    def generate(self):
        if self._validate_current_state():
            block = {}
            if self.block_entry.label.get() == 'Block Tag':
                block = {
                    "tag": self.block_entry.get()
                }
            else:
                block = {
                    "block": self.block_entry.get()
                }

            if len(self.state_entry.get()) > 0:
                state_list = self.state_entry.get().split(',')
                state_dict = {}
                for block_state in state_list:
                    key, value = block_state.split('=')
                    state_dict[key] = value
                block["state"] = state_dict

            size = abs(int(self.size_entry.get()))
            height = size
            zsize = size
            if len(self.height_entry.get()) > 0:
                height = abs(int(self.height_entry.get()))
            if len(self.zsize_entry.get()) > 0:
                zsize = abs(int(self.zsize_entry.get()))

            with_test_function = False
            if self.include_test_function.get() == 'True':
                with_test_function = True

            self.generator.generate(
                block,
                size,
                self.shape_entry.get(),
                height=height,
                zsize=zsize,
                with_test_function=with_test_function
            )

    def save_settings(self):
        """
        Exports a JSON file with all of the current settings in the
        program. Includes the following keys:
        name,
        is_tag,
        shape,
        test_function,
        state,
        size,
        zsize,
        height
        """
        settings = {
            "name": self.block_entry.get(),
            "is_tag": False,
            "shape": self.shape_entry.get(),
            "test_function": False
        }

        if 'True' in self.include_test_function.get():
            settings['test_function'] = True

        if 'Block Tag' in self.block_entry.label.get():
            settings['is_tag'] = True

        if len(self.state_entry.get()) > 0:
            state_list = self.state_entry.get().split(',')
            state_dict = {}
            for block_state in state_list:
                key, value = block_state.split('=')
                state_dict[key] = value

            settings["state"] = state_dict

        try:
            settings['size'] = int(self.size_entry.get())

            if len(self.height_entry.get()) > 0:
                settings["height"] = int(self.height_entry.get())

            if len(self.zsize_entry.get()) > 0:
                settings["zsize"] = int(self.zsize_entry.get())
        except ValueError:
            self.error_label['text'] = INVALID_INPUT

        filename = self.save_settings_entry.get() + '.json'
        if self.save_settings_entry.get() == '':
            filename = 'near_' + \
                settings['name'].split(':')[-1] + '_settings.json'

        if self._validate_current_state():
            try:
                print('Trying to make block gen settings folder...')
                os.mkdir('near_block_gen_settings')
            except FileExistsError:
                print("Block gen settings folder already exists!")
            settings_file = open('near_block_gen_settings/' + filename, 'w')
            settings_file.write(json.dumps(settings, sort_keys=True, indent=4))
            settings_file.close()
            print('Successfully saved current state.')
            # self.error_label['text'] = 'Valid Input'
            return True
        return False
        print(settings)

    def load_settings(self):
        filename = self.load_settings_entry.get()
        if len(filename) > 0:
            try:
                if not filename.endswith('.json'):
                    filename += '.json'
                infile = open('near_block_gen_settings/' + filename)
                settings = json.loads(infile.read())
                infile.close()
                self.import_settings(settings)
            except FileNotFoundError:
                self.error_label['text'] = 'File does not exist!'
            except json.decoder.JSONDecodeError:
                self.error_label['text'] = 'Invalid JSON'
        else:
            self.error_label['text'] = 'Enter settings file first!'

    def import_settings(self, settings):
        self.error_label['text'] = ''
        load_error_message = "Error loading settings"
        if settings.get('name', None) != None:
            namespaced_id = settings['name'].split(':')
            if len(namespaced_id) == 2:
                self.block_entry.namespace_entry.delete(0, 'end')
                self.block_entry.namespace_entry.insert(END, namespaced_id[0])
                self.block_entry.entry.delete(0, 'end')
                self.block_entry.entry.insert(END, namespaced_id[1])
            elif len(namespaced_id) == 1:
                self.block_entry.namespace_entry.delete(0, 'end')
                self.block_entry.namespace_entry.insert(END, 'minecraft')
                self.block_entry.entry.delete(0, 'end')
                self.block_entry.entry.insert(END, namespaced_id[0])
            else:
                self.error_label['text'] = load_error_message

        if settings.get('is_tag', None) != None:
            if settings['is_tag'] == True:
                self.block_entry.label.current(1)

        if settings.get('shape', None) != None:
            if settings['shape'] in self.shape_entry.values:
                index = self.shape_entry.values.index(settings['shape'])
                self.shape_entry.combobox.current(index)
            else:
                self.error_label['text'] = load_error_message

        if settings.get('test_function', None) != None:
            if settings['test_function'] == True:
                self.include_test_function.combobox.current(1)

        if settings.get('state', None) != None:
            if isinstance(settings['state'], dict):
                state_string = ""
                for key in settings['state'].keys():
                    state_string += key + '=' + \
                        str(settings['state'][key]).lower() + ','
                state_string = state_string[:-1]
                self.state_entry.entry.delete(0, 'end')
                self.state_entry.entry.insert(END, state_string)
            else:
                self.error_label['text'] = load_error_message

        if settings.get('size', None) != None:
            self.size_entry.entry.delete(0, 'end')
            self.size_entry.entry.insert(END, str(settings['size']))

        if settings.get('zsize', None) != None:
            self.zsize_entry.entry.delete(0, 'end')
            self.zsize_entry.entry.insert(END, str(settings['zsize']))

        if settings.get('height', None) != None:
            self.height_entry.entry.delete(0, 'end')
            self.height_entry.entry.insert(END, str(settings['height']))

    def _validate_current_state(self):
        try:
            if len(self.size_entry.get()) != 0:
                size = int(self.size_entry.get())
            else:
                return False
            if len(self.height_entry.get()) != 0:
                height = int(self.height_entry.get())
            if len(self.zsize_entry.get()) != 0:
                zsize = int(self.zsize_entry.get())
            if len(self.state_entry.get()) != 0:
                state_list = self.state_entry.get().split(',')
                for block_state in state_list:
                    key, value = block_state.split('=')
        except ValueError:
            self.error_label['text'] = INVALID_INPUT
            return False
        else:
            name = self.block_entry.get()
            if len(name.split(':')) <= 2:
                namespace, block_id = name.split(':')
                return bool(re.match('^[a-z0-9_:]+$', block_id)) and bool(re.match('^[a-z0-9_:-]+$', namespace))
            else:
                return False

        print('Valid settings.')
        return True


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

    def get(self):
        pass


class LabelledCombobox(LabelledWidget):
    def __init__(self, parent, label_text, row, col, values):
        super().__init__(parent, label_text, row, col)
        self.values = values
        self.combobox = Combobox(
            self.widget_frame, values=values, width=WIDGET_WIDTH - 2, state='readonly')
        self.combobox.grid(row=row, column=col+1)
        self.combobox.current(0)

    def get(self):
        return self.combobox.get()


class LabelledEntry(LabelledWidget):
    def __init__(self, parent, label_text, row, col, with_namespace=False):
        super().__init__(parent, label_text, row, col)
        self.has_namespace = with_namespace
        self.entry = Entry(self.widget_frame, width=int(WIDGET_WIDTH))
        self.entry.grid(row=row, column=col + 1)

        if with_namespace:
            self.entry.grid(row=row, column=col + 3)
            self.colon_label = Label(self.widget_frame, text=':')
            self.colon_label.grid(row=row, column=col + 2)
            self.namespace_entry = Entry(
                self.widget_frame, width=int(WIDGET_WIDTH/2))
            self.namespace_entry.grid(row=row, column=col)
            self.namespace_entry.insert(END, 'minecraft')

            self.entry.config(width=int(WIDGET_WIDTH/2))

    def get(self):
        if self.has_namespace:
            return self.namespace_entry.get() + ':' + self.entry.get()
        return self.entry.get()
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
