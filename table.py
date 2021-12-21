class Table:
    """
    table:
        {
            "primary":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                },
            "secondary":
                {
                    "next_hop":"$ip",
                    "cost":"$cost",
                }
        }
    """
    DEFAULT_PORT = 65432
    DEFAULT_ANNOUNCEMENT_PORT = 23456
    def __init__(self):
        self.table = {"primary":{"next_hop":None,"cost":None},"secondary":{"next_hop":None,"cost":None}}
                
    def get_table(self):
        return self.table
    
    def get_next_hop(self):
        return self.table["primary"]["next_hop"]
    
    def get_sec_hop(self):
        return self.table["secondary"]["next_hop"]
        
    # addr -> de onde veio a nova table
    # host -> self ip
    def updateTable(self,next_hop,cost):
        if self.hasRoute():
            toChange = 0
            if cost < self.table["primary"]["cost"]:
                self.changeOrder()
                toChange = 1
            elif not self.table["secondary"]["cost"]:
                toChange = 2
            elif cost < self.table["secondary"]["cost"]:
                toChange = 2
                
            if toChange == 1:
                self.table["primary"]["next_hop"] = next_hop
                self.table["primary"]["cost"] = cost
            elif toChange == 2:
                self.table["secondary"]["next_hop"] = next_hop
                self.table["secondary"]["cost"] = cost
        else:
            self.table["primary"]["next_hop"] = next_hop
            self.table["primary"]["cost"] = cost
            toChange = 1
        return toChange
        
    def hasRoute(self):
        return self.table["primary"]["next_hop"]
    
    def removePrimaryRoute(self):
        self.table["primary"]["next_hop"] = None
        self.table["primary"]["cost"] = None
        self.changeOrder()
    
    def getRouteCost(self):
        return self.table["primary"]["cost"]
    
    def getRouteNextHop(self):
        return self.table["primary"]["next_hop"]
    
    def changeOrder(self):
        temp = self.table["primary"]
        self.table["primary"] = self.table["secondary"]
        self.table["secondary"] = temp
        
    def print(self):
        print(self.table)
        