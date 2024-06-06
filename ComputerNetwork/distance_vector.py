class Router:
    counter = 0

    def __init__(self, network_list, label=None):
        Router.counter += 1
        self.adj = {}
        self.routing_table = {n: (32, None) for n in network_list}
        self.rcv_buffer = []
        if label is None:
            self.label = f"Router-{str(Router.counter).zfill(4)}"
        else:
            self.label = label

    def connect_router(self, other, cost):
        self.adj[other.label] = (other, cost)
        other.adj[self.label] = (self, cost)

    def connect_network(self, network):
        if network in self.routing_table:
            self.routing_table[network] = (1, self.label)

    def send_pkt(self, other, msg):
        print(f"send from {self.label} to {other.label}")
        if other.label in self.adj.keys():
            self.adj[other.label][0].rcv_pkt((self.label, msg))
        else:
            print("host not connected")

    def rcv_pkt(self, msg):
        self.rcv_buffer.append(msg)

    def propagate(self, msg):
        for i in self.adj.keys():
            self.send_pkt(self.adj[i][0], msg)

    def update_dv(self):
        change = False
        print(' '.join([str(self.adj[x][0]) for x in self.adj]))
        for i in self.rcv_buffer:
            print(i[0], ' '.join([str(i[1][x]) for x in i[1]]))
        for i in self.routing_table:
            tmp = (self.routing_table[i][0], self.routing_table[i][1])
            for j in range(len(self.rcv_buffer)):
                trial = self.adj[self.rcv_buffer[j][0]][1] + self.rcv_buffer[j][1][i][0]
                if trial < tmp[0]:
                    tmp = (trial, self.rcv_buffer[j][0])
                    change = True
            self.routing_table[i] = (tmp[0], tmp[1])
        self.rcv_buffer.clear()
        return change

    def disp(self):
        print(f"{self.label}---------------------------")
        print("Net\t\tCost\tNext")
        for i in self.routing_table:
            print(f"{i}:\t{self.routing_table[i][0]}\t\t{self.routing_table[i][1]}")

    def __str__(self):
        return f"[{self.label} --> {' '.join([x for x in self.adj])}]"


class Internet:
    def __init__(self):
        self.routers: list[Router] = []
        self.networks = []

    def add_router(self, label=None):
        rt = Router(self.networks, label)
        self.routers.append(rt)
        return rt

    def add_network(self, network_label):
        self.networks.append(network_label)
        for rt in self.routers:
            rt.routing_table[network_label] = (32, None)

    def update_dv(self):
        change = False
        for rt in self.routers:
            rt.propagate(dict(rt.routing_table))
        input("propagation complete")
        for rt in self.routers:
            change = rt.update_dv() or change
            rt.disp()
        return change

    def disp_dv(self):
        for rt in self.routers:
            rt.disp()


I = Internet()
extern: dict[str: Router] = {}

for i in range(1, 10):
    I.add_network(f'Net {i}')

for i in range(6):
    c = chr(ord("A") + i)
    extern[c] = I.add_router(f'{c}')

extern['A'].connect_router(extern['B'], 1)
extern['A'].connect_router(extern['C'], 2)
extern['B'].connect_router(extern['D'], 4)
extern['C'].connect_router(extern['D'], 6)
extern['D'].connect_router(extern['E'], 1)
extern['E'].connect_router(extern['F'], 2)
extern['A'].connect_network('Net 1')
extern['B'].connect_network('Net 1')
extern['B'].connect_network('Net 2')
extern['A'].connect_network('Net 3')
extern['C'].connect_network('Net 3')
extern['C'].connect_network('Net 4')
extern['D'].connect_network('Net 4')
extern['C'].connect_network('Net 5')
extern['D'].connect_network('Net 6')
extern['E'].connect_network('Net 6')
extern['E'].connect_network('Net 7')
extern['F'].connect_network('Net 7')
extern['F'].connect_network('Net 8')
extern['B'].connect_network('Net 9')
extern['D'].connect_network('Net 9')

I.disp_dv()
input()
cc = True
while cc:
    cc = I.update_dv()
    I.disp_dv()
    input("continue")
