from lib_colors import printInfo
class Table:
    """
    table:
    {
        "ip":
            {
            "next_hop":"$ip",
            "port":"$port",
            "announcement_port":"$annport",
            "cost":"$cost",
            "active":"False"
            }
    }
    """
    DEFAULT_PORT = 65432
    DEFAULT_ANNOUNCEMENT_PORT = 23456
    def __init__(self,params=None):
        self.table = {}
        if params != None:
            for ip in params:
                if ip not in self.table:
                    self.table[ip] = {"next_hop":ip,"port":Table.DEFAULT_PORT,"announcement_port":Table.DEFAULT_ANNOUNCEMENT_PORT,"cost":1,"active":False}
                
                
    def get_table(self):
        return self.table
    
        
    # addr -> de onde veio a nova table
    # host -> self ip
    def updateTable(self,host,addr,otherTable):
        if addr not in self.table:
            print(addr)
            # Active é iniciado sempre a False para não compremeter fluxos já a correr | rever isto
            # Cost é incrementado por 1 pois : Quando custa do addr para ir para o ip + quando custa do addr para ir ao host == 1
            printInfo("table","Creating new entry > addr not in selfTable...")
            self.table[addr] = {"next_hop":addr,"port":Table.DEFAULT_PORT,"announcement_port":Table.DEFAULT_ANNOUNCEMENT_PORT,"cost":1,"active":False}
            printInfo("table",("Created new entry\nTable Updated:\n"+str(self.table)))

        for ip in otherTable:
            # se o caminho mais rápido for o meu, então ignora

            
            if ip == host or otherTable[ip]["next_hop"] == host:
                printInfo("table","ip is host or pass by host")
                pass
            elif ip in self.table:
                printInfo("table","already has an ip")
                # comparar custos
                # Só atualizar se custo + 1 for menor que o custo já definido
                if (otherTable[ip]["cost"]+1) < self.table[ip]["cost"]:
                    printInfo("table",("Updating table ... "+str(self.table[ip]["cost"]) + " -> " + str(otherTable[ip]["cost"])))
                    self.table[ip] = {"next_hop":addr,"port":otherTable[ip]["port"],"announcement_port":otherTable[ip]["announcement_port"],"cost":(otherTable[ip]["cost"]+1),"active":False}
                    printInfo("table",("Updated table\nTable Updated:\n"+str(self.table)))
                    pass
                else:
                    printInfo("table",("Custo não compensou\nOtherTableCost: "+str(otherTable[ip]["cost"])+"\nSelfTable: " + str(self.table[ip]["cost"])))
            # inserir na tabela
            else:
                # Active é iniciado sempre a False para não compremeter fluxos já a correr | rever isto
                # Cost é incrementado por 1 pois : Quando custa do addr para ir para o ip + quando custa do addr para ir ao host == 1
                printInfo("table","Creating new entry ...")
                self.table[ip] = {"next_hop":addr,"port":otherTable[ip]["port"],"announcement_port":otherTable[ip]["announcement_port"],"cost":(otherTable[ip]["cost"]+1),"active":False}
                printInfo("table",("Created new entry\nTable Updated:\n"+str(self.table)))
                pass
            
    value = property(get_table)