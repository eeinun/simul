import re
import time


class Tape:
    def __init__(self, blank_symbol='_'):
        self.left = []
        self.right = []
        self.blank_symbol = blank_symbol
        self.head = blank_symbol
        self.step = 0

    def load(self, input_string: str):
        self.right = list(input_string[1:][::-1])
        self.left.clear()
        self.head = input_string[0]

    def insert(self, input_string: str):
        self.right = list(input_string[1:]) + self.right
        self.head = input_string[0]

    def read(self):
        return self.head

    def write(self, symbol=None):
        self.head = self.blank_symbol if symbol is None else symbol

    def move(self, left: bool):
        if left:
            self.right.append(self.head)
            if len(self.left):
                self.head = self.left.pop()
            else:
                self.head = self.blank_symbol
        else:
            self.left.append(self.head)
            if len(self.right):
                self.head = self.right.pop()
            else:
                self.head = self.blank_symbol

    def disp(self, lookahead=10, leave=False, interval=0.5, desc=None):
        left = ([self.blank_symbol] * lookahead + self.left)[-lookahead:]
        right = ([self.blank_symbol] * lookahead + self.right)[-lookahead:]
        if desc is None:
            desc = f"[{self.step:3d}]"
            self.step += 1
        print(f"{desc} ...{'|'.join(left)}[{self.head}]{'|'.join(right[::-1])}...")
        if interval:
            time.sleep(interval)

    def insta(self, state, derive=False):
        print(('⊢ ' if derive else '') + ''.join(self.left) + state + self.head + ''.join(self.right[::-1]))


class TuringMachine:
    def __init__(
            self,
            states: list[str],
            input_symbols: list[str],
            tape_symbols: list[str],
            transitions: dict[str:dict[str:tuple[str, str, bool]]],
            initial_state: str,
            final_states: list[str],
            blank_symbol: str = '_'
    ):
        '''
        :param states: List of states. For example ['q_0', 'q_f']
        :param input_symbols: List of symbols (single character)
        :param tape_symbols: List of symbols (single character)
        :param transitions: delta(q_0, a) = (q_1, b, R) is equivalent to delta["q_0"]["a"] = ("q_1", b, False)
        :param initial_state:
        :param final_states:
        :param blank_symbol:
        '''
        self.states = states
        self.input_symbols = input_symbols
        self.tape_symbols = tape_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.blank_symbol = blank_symbol
        self.tape = Tape(blank_symbol=blank_symbol)
        if self.blank_symbol not in self.tape_symbols:
            self.tape_symbols.append(self.blank_symbol)
        for q in self.transitions:
            if q not in self.states:
                raise Exception("State {q} is not given.")
            for a in self.transitions[q]:
                if a not in self.tape_symbols:
                    raise Exception(f"Tape symbol {a} is not given.")
                if len(self.transitions[q][a]) == 0:
                    del self.transitions[q][a]
                q1, b, _ = self.transitions[q][a]
                if q1 not in self.states:
                    raise Exception(f"State {q1} is not given.")
                if b not in self.tape_symbols:
                    raise Exception("Tape symbol {b} is not given.")

    def load(self, input_string: str):
        self.tape.load(input_string)

    def compute_with_input(self, input_string, v=0):
        current_state = self.initial_state
        for current_input_symbol in input_string:
            if current_input_symbol not in self.transitions[current_state]:
                break
            p = f"({current_state}, {current_input_symbol})"
            current_state, output, direction = self.transitions[current_state][current_input_symbol]
            self.tape.write(output)
            self.tape.move(direction)
            if v:
                self.tape.disp(desc=f"delta({p})=({current_state}, {output}, {'L' if direction else 'R'})")
        if current_state in self.final_states:
            if v:
                print(f"{input_string} is accepted")
            return True
        if v:
            print(f"{input_string} is not accepted at delta({current_state}, {current_input_symbol})")
        return False

    def compute(self, v=0):
        current_state = self.initial_state
        current_tape_symbol = self.blank_symbol
        while True:
            current_tape_symbol = self.tape.read()
            if current_state not in self.transitions or current_tape_symbol not in self.transitions[current_state]:
                break
            p = f"({current_state}, {current_tape_symbol})"
            current_state, output, direction = self.transitions[current_state][current_tape_symbol]
            self.tape.write(output)
            self.tape.move(direction)
            if v == 1:
                self.tape.disp(desc=f"delta({p})=({current_state}, {output}, {'L' if direction else 'R'})", interval=0.3)
            elif v == 2:
                self.tape.insta(current_state, derive=True)
        if current_state in self.final_states:
            if v:
                print(f"Input string is accepted")
            return True
        if v:
            print(f"Input string is not accepted at delta({current_state}, {current_tape_symbol})")
        return False


def transition_parser(string):
    l = string.split('\n')
    d = {}
    for i in l:
        if i.strip().startswith("//"):
            continue
        prs = ([(None, None)] + re.findall(r'([\w\d_#]+)\s*,\s*([\w\d_#])\s*-+>\s*([\w\d_#]+)\s*,\s*([\w\d_#])\s*,\s*([LR])', i.strip()))[-1]
        if len(prs) != 5:
            continue
        [q0, a, q1, b, di] = prs
        if q0 not in d:
            d[q0] = {}
        d[q0][a] = (q1, b, di == 'L')
    return d


transitions = '''
// replace a with an x and move to b then replace it with a y
q_0, a -> q_1, x, R
q_1, a -> q_1, a, R
q_1, y -> q_1, y, R
q_1, b -> q_2, y, L
// return to a
q_2, y -> q_2, y, L
q_2, a -> q_2, a, L
q_2, x -> q_0, x, R
// termination
q_0, y -> q_3, y, R
q_3, y -> q_3, y, R
q_3, _ -> q_4, _, R
'''
M = TuringMachine(
    ["q_0", "q_1", "q_2", "q_3", "q_4"],
    ["a", "b"],
    ["a", "b", "x", "y", "_"],
    transition_parser(transitions),
    "q_0",
    ["q_4"],
    "_"
)

M.load("aabb")
M.tape.disp(leave=True)
M.compute(v=1)