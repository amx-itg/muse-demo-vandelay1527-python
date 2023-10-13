import asyncio
import threading
import re
import time

class precis:
    def __init__(self, host, port, username=None, password=None, dvTP=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dvTP = dvTP

    async def socketListener(self, reader):
        while True:
            data = await reader.readline()
            if not data:
                break
            data = data.decode("utf-8", "ignore")
            self.handleFeedback(data.strip())
        await asyncio.sleep(.5)


    async def handshakeFunction(self, reader, writer):
        data = None
        if self.username and self.password:
            data = await reader.readuntil(b"Login :")
            print(data.decode())
            writer.write(self.username.encode() + b"\n")
            data = await reader.readuntil (b"Password :")
            print(data.decode())
            writer.write(self.password.encode() + b"\n")
        
            # Read the command prompt
            data = await reader.readuntil (b"Login successful")
            
        if data or not self.username:
            await self.socketListener(reader)
        
        print("Socket was closed?")


    async def InitiateConnection(self):
        global reader, writer
        while True:
            try:
                reader, writer = await asyncio.open_connection(self.host, self.port)
                await self.handshakeFunction(reader, writer) 
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"An error occurred opening the socket: {e}")
                print("Attempting reconnect...")
                await asyncio.sleep(10)


    def connectBlocking(self):
        asyncio.run(self.InitiateConnection())


    def connect(self):
        threading.Thread(target=self.connectBlocking, name="t1").start()


    def sendMessage(self, cmd):
        # print(f"Precis Sending: {cmd}")
        writer.write(cmd.encode())


    def handleFeedback(self, response):
        # print(f"Precis Received: {response}")
        regexp = re.compile(r'get (.*) video input ([0-9]+)')
        if "Welcome to " in response:
            for i in range(1,5):
                self.sendMessage(f"get vidin res:{i}\n")
                time.sleep(1)
        elif regexp.search(response):
            result = regexp.search(response)
            signal = result.group(1)
            source = int(result.group(2))
            
            state = signal not in {"no video", "Not Support"}            
            if source == 1:
                self.dvTP.port[2].channel[102].value = state
            if source == 2:
                self.dvTP.port[2].channel[104].value = state
            if source == 3:
                self.dvTP.port[2].channel[101].value = state
            if source == 4:
                self.dvTP.port[2].channel[103].value = state
        

    def switch(self, input):
        self.sendMessage(f"set switch CI{input}O1\n")


    def setTP(self, dvTP):
        self.dvTP = dvTP
        self.dvTP.port[2].channel[102].value = False
        self.dvTP.port[2].channel[104].value = False
        self.dvTP.port[2].channel[101].value = False
        self.dvTP.port[2].channel[103].value = False
