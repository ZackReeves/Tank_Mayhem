import time

def request_data_from_file():
    f = open("data.txt")
    data = f.read()
    data = data.split('<-->')
    if(len(data)==4):
        return data[0], data[1], data[2], data[3]
    else:
        return [0,0,1,1]

def Main():
    while(True):
        time.sleep(0.1)
        
        x, y, button0, button1 = request_data_from_file()
        print("x: ", x,"   y: ", y,"    button 0: ", button0,"    button 1: ", button1)
        

if __name__ == '__main__':
    Main()
