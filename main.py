from enum import Enum
import re

# Define the commands that the interpreter can execute
class Commands(Enum):
    CREATE = 'create'
    DELETE = 'delete'
    UPDATE = 'update'
    ADD = 'add'
    SUBTRACT = 'subtract'
    MULTIPLY = 'multiply'
    DIVIDE = 'divide'
    PRINT = 'print'
    INIT = 'init'
class Parser:
    # Use dictionaries to store variables, functions and commands within each function so they can be used globally
    def __init__(self):
        self.vars = {}
        self.functions = {}

    # Trigger the script by parsing the script and running the init function
    def trigger_script(self, scripts):
        for script in scripts:
            self.parse_script(script)
            self.run_function('#init', {})

    # Parse the script by going line by line and store variables and functions
    def parse_script(self, script):
        #split the script into lines
        lines = script.strip().split('\n')
        #initialize the current function to None
        current_function = None
        #iterate through the lines
        for line in lines:
            line = line.strip()
            if not line:
                continue
            #if the line matches pattern of': [', we know that it's the start of an array of commands
            if re.search(r':\s*\[$', line):
                #get the name/operation of the function or command
                current_function = line.split(':')[0].strip()
                #if the function already exsits, we just overide with with empty list to store the commands
                self.functions[current_function] = []
            #if the line is ']', we know that the array of commands has ended
            elif line == ']':
                current_function = None
            elif current_function:
                # parse the command and add it to the current function
                command = self.process_command(line)
                self.functions[current_function].append(command)
            else:
                #get the name and value of the variable by splitting on colon
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # print(f'{key}: {value}')
                #parse the value of the var which should be numeric
                try:
                    self.vars[key] = self.parse_value(value)
                except ValueError:
                    print("Invalid value for variable")


    #parse the value of a variable and check for references to other variables
    def parse_value(self, value):
        if isinstance(value, str) and value.startswith('#'):
            return self.vars.get(value[1:], None)
        else:
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value


    # Parse the command and return a dictionary
    def process_command(self, line):
        command = {}
        #we need to split the line by commas so each part of the command can be parsed
        line_parts = line.split(',')
        for part in line_parts:
            #this is another key/value for a command so we can split it again by colon
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()
                command[key] = value
        return command


    #run each command in our function
    def run_function(self, function_name, params):
        if function_name.startswith('#'):
            function_name = function_name[1:]
            #if we find the function in our functions dictionary, we can run each command we stored in the function
            if function_name in self.functions:
                function = self.functions[function_name]
                for command in function:
                    #create a new dictionary to store the final parsed command
                    final_command = {}
                    for key, value in command.items():
                        #we know this would be a parameter passed in so we need to for the value of the parameter
                        if isinstance(value, str) and value.startswith('$'):
                            param_name = value[1:]
                            final_command[key] = params.get(param_name, value)
                        else:
                            final_command[key] = value
                    self.run_command(final_command)

    # run each command in our script
    def run_command(self, command):
        cmd = command['cmd']
        if cmd == Commands.CREATE.value:
            self.vars[command['id']] = self.parse_value(command['value'])
        elif cmd == Commands.UPDATE.value:
            self.vars[command['id']] = self.parse_value(command['value'])
        elif cmd == Commands.DELETE.value:
            if command['id'] in self.vars:
                del self.vars[command['id']]
        elif cmd == Commands.PRINT.value:
            value = self.parse_value(command['value'])
            print(value if value else 'undefined')
        elif cmd in ['add', 'subtract', 'multiply', 'divide']:
            #we need to retrieve the values of in the command
            param_values = {}
            for k, v in command.items():
                if k != 'cmd' and k != 'id':
                    values = self.parse_value(v)
                    param_values[k] = values
            value1, value2 = param_values.values()
            if cmd == Commands.ADD.value:
                self.vars[command['id']] = value1 + value2
            elif cmd == Commands.SUBTRACT.value:
                self.vars[command['id']] = value1 - value2
            elif cmd == Commands.MULTIPLY.value:
                self.vars[command['id']] = value1 * value2
            elif cmd == Commands.DIVIDE.value:
                self.vars[command['id']] = value1 / value2
        else:
            self.run_function(cmd, command)



if __name__ == "__main__":
    # Read scripts from files
    with open('sample-script.txt', 'r') as file:
        script1 = file.read()
    with open('script2.txt', 'r') as file:
        script2 = file.read()

    parser = Parser()
    parser.trigger_script([script1, script2])


