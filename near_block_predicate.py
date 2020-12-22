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

def gui():
    window = Tk()
    

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
    
    # gui()
    command_terminal()

    