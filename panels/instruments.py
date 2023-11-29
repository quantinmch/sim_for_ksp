def writeInstrL(streams):
    data = []
    for i in range(1):
        data.append(0)
    
    if streams == None:
        data[0]=0
    else:
        data[0]=int(streams.speed())
    
    return data