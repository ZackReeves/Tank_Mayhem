import subprocess
    
def twos_complement(num):
    val = -1*(int(num[0])<<len(num)-1)
    for i in range(1, len(num)):
        val+=int(num[i])<<(len(num)-1-i)
    return val

def main():
    message = ""
    process = subprocess.Popen(
        "nios2-terminal <<< {}",
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=0, text=True
    )
    i=0
    while True:
    # subprocess allows python to run a bash command
        f = open("command.txt", "r")
        res = f.read()
        process.stdin.write(res)
        process.stdin.flush()
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            #output=output.decode("utf-8")
            output=output.split('<-->')
            # output=output.strip()
            if (i>5):
                data = output
                x_data = data[1][3:]
                y_data = data[2][3:]
                buttons = data[3][9:]
                x_bin = bin(int(x_data, 16))[2:].zfill(32)[22:] #translates accelerometer data from hex to bin and selects the significant bits
                y_bin = bin(int(y_data, 16))[2:].zfill(32)[22:]
                buttons_bin = bin(int(buttons, 16))[2:].zfill(2)
                button0 = int(buttons_bin[1], 2)
                button1 = int(buttons_bin[0], 2)
                x_tilt = twos_complement(x_bin)
                y_tilt = twos_complement(y_bin)
                x_tilt = round(x_tilt/270,3)
                y_tilt = round(y_tilt/135,3)
                #if x_tilt>1:
                #    x_tilt=1
                #elif x_tilt<-1:
                #    x_tilt=-1
                if y_tilt>1:
                    y_tilt=1
                elif y_tilt<-1:
                    y_tilt = -1
                print("x: ", x_tilt,"   y: ", y_tilt,"    button 0: ", button0,"    button 1: ", button1)
                data = str(x_tilt)+"<-->"+str(y_tilt)+"<-->"+str(button0)+"<-->"+str(button1)
                f = open("data.txt","w")
                f.write(data+'\n')
                f.close()
                #print(data)	
                #s.sendto(message.encode('utf-8'), server)
            if (i<=5):
                
                i+=1
                
    rc = process.poll()


if __name__ == '__main__':
    main()
