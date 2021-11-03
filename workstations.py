from ws_data import data

def LoadWorkstation(name=None):
    if name == None and id == None:
        return None
    elif name != None:
        return data["workstations"][name]

def AddWorkstation(name, ip, dept) -> None:
    data["workstations"]["total"] += 1
    data["workstations"][name] = {
        "id" : data["workstations"]["total"],
        "ip" : ip,
        "dept" : dept
    }

def test():
    print(data["workstations"]["welding1"]["ip"])
    testData = LoadWorkstation(name="welding1")
    print(testData)
    AddWorkstation("test1", "none", "none")
    testData2 = LoadWorkstation(name="test1")
    print(testData2)

if __name__ == '__main__': test()
