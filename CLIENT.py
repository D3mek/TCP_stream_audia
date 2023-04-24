import socket
import pyaudio
import time
import threading
from getpass import getpass
import rsa
from tkinter import *
import tkinter.messagebox as msgbox
from PIL import Image, ImageTk

class StarShip:
    def __init__(self, root):
        #premenna ktora zistuje ci je client na server pripojeny alebo ci sa zazracne nevypol
        self.server_conn = False
        #premenna ktora dostane hodnotu True alebo False a podla toho stream sa vypne alebo stale bude streamovat
        self.server = None
        #######################################
        self.public_key = None
        self.private_key = None
        self.public_server = None
        #######################################
        #premenna pre socket servera
        self.SERVER = None
        #zadana ip z entry boxu
        self.HOST = None
        #port servera stale je fixnuty na 443
        self.PORT = 80
        self.password = None
        #######################################
        #premenna obsahujuca objekt pyaudio ktory budeme potrebovat pre stream audia
        self.audio = pyaudio.PyAudio()
        self.FORMAT = None
        self.CHANNELS = None
        self.RATE = None
        self.CHUNK = None
        #######################################
        self.root = root
        
        self.image_icon = PhotoImage(file="image/logo.png") 
        self.root.iconphoto(False, self.image_icon)

        self.logo = PhotoImage(file="image/client.png")
        Label(self.root, 
               image=self.logo, 
               bg="#212a3f", 
               bd=0).place(x=52,y=10)
        
        Label(self.root, 
               text=":", 
               font=10, 
               bg="#212a3f", 
               fg="white").place(x=162,y=47)
        
        Label(self.root, 
               text="80", 
               font=10, 
               bg="#212a3f", 
               fg="white").place(x=171,y=48)
        
        self.serverip = Label(self.root, 
                            text="", 
                            font=3, 
                            bg="#212a3f", 
                            fg="green", 
                            bd=0)
        self.serverip.place(x=35, y=230)
        
        self.entry_ip = Entry(self.root, 
                             width=20)
        self.entry_ip.place(x=35, y=50)
        self.entry_ip.insert(0, "IP")
        
        self.entry_psw = Entry(self.root, 
                               width=20)
        self.entry_psw.place(x=35, y=80)
        self.entry_psw.insert(0, "password")
        
        self.conn = Image.open("image/connect.png")
        self.connres = self.conn.resize((100, 100))
        self.conn_fin = ImageTk.PhotoImage(self.connres)
        self.connect_bt = Button(self.root, 
                                image=self.conn_fin, 
                                bg="#212a3f", 
                                bd=0, 
                                command=self.connect_bttn)
        self.connect_bt.place(x=60,y=110)

        msgbox.showinfo("Welcome", "Welcome on StarShip :D")

##############################################################################
    def connect_bttn(self):
        #ak neni cient pripojeny na server tak sa vykona prve if
        if not self.server_conn:
            #ulozi do premenny heslo z entry boxu GUI
            self.password = str(self.entry_psw.get())
            #ulozi do premenny ip servera ktore bolo zadane do entry boxu GUI
            self.HOST = str(self.entry_ip.get())
            #tato podmienka sa vykona ak entry boxi ip adresi a hesla niesu prazdne
            if self.password != "" and self.HOST != "":
                #po True hodnote podmienky sa vykona funkcia connection ako podproces
                threading.Thread(target=self.connection).start()
            #ak entry box daky je prazdny tak program vyhodi msg box 
            else:
                msgbox.showwarning("Password", "IP alebo Heslo nemoze byt prazdne!")
        #ak je hodnota server_conn na True tak client je uz pripojeny co vykona tuto else podmienku        
        else:
            msgbox.showinfo("Client", "Uz pripojene!")

##############################################################################
    def audio_recv(self):
        #loop aby ma to vratilo po ukonceni streamu naspat sem hore
        #while True:
            #try funkcia na handling errorv
        try:
            #premenna do ktorej sa ulozi recv zo servera aby client vedel co ide recv hudbu alebo mikrofon
            option = rsa.decrypt(self.SERVER.recv(1024), self.private_key)
            #decode z bitov
            option.decode()
            print(option)
            #predminka na overenie ci recv == voice
            if option == b"voice":
                #nastavenia zvuku pre mikrofon
                self.FORMAT = self.audio.get_format_from_width(2)
                self.CHANNELS = 1
                self.RATE = 44100
                self.CHUNK = 4096
                #podmienka ktora funguje na yapnutie alebo vypnutie streamu
                self.server = True
                print("changed to voice")
                #podmienka na overenie ci recv == music
            elif option == b"music":
                #nastavenie zvuku pre hudbu
                self.FORMAT = self.audio.get_format_from_width(2)
                self.CHANNELS = 2
                self.RATE = 44100
                self.CHUNK = 512
                #nastavi premenu server na true
                self.server = True
                print("changed to music")

            #toto pracuje s nasim recvnutou hudbou
            stream = self.audio.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    #output = true znamena pre repraky, input = true znamena nahravanie mik. ale to nam tu netreba
                                    output=True,
                                    frames_per_buffer=self.CHUNK,
                                    )
            #podmienka ktora vzhodnoti ci priso daco alebo n
            if option:
                #loop pre prehravanie zvuku dokym sa server = true
                while self.server:
                    #premena do ktorej sa uklada dany stream hudby v bitoch
                    voice = self.SERVER.recv(self.CHUNK)
                    print("receiving stream!")    
                    if voice == b"ended":
                        #prehodi premenu server na False
                        print(voice)
                        self.server = False
                        th = threading.Thread(target=self.audio_recv).start()
                    #pomocou stream premeny co sme si zadefinovaly prehrava co recvol
                    stream.write(voice)

        #error handlig ak nevie decodnut recv                
        except UnicodeDecodeError:
            print("cant decode")
        #error ak sa server vypne pocas streamu alebo mimo streamu
        except ConnectionResetError:
            #vymaze v GUI label kde ukazuje IP servera
            self.serverip.configure(text="")
            #nastavi premenu server na False
            self.server = False
            #nastavi premenu server_conn na False ktora riadi ci je server dostupny alebo nie
            self.server_conn = False
            #zobrazi msg box
            msgbox.showwarning("Server", "Server sa neočakávane vypol!")

##############################################################################
    #funkcia pre pripojenie sa na server
    def connection(self):
        #vytvorenie publick a private RSA kluca pre clienta pre ecryption a decryption
        self.public_key, self.private_key = rsa.newkeys(1024) 
        #nastavenie socketu AF_INET = IPv4 , SOCK_STREAM = TCP
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #premena obsahujuca int s cislom portu na ktorom server pocuva
        self.PORT = 80
        #podmienka ak neni entry box pre ip prazdny tak sa skusi vykonat 
        if self.HOST != "":
            #funkcia pre handling errorov
            try:
                #pre krasu :D
                self.serverip.configure(text="Pripájam!...", fg="red")
                #tu sa client skusi napojit na konkretnu ip a port
                self.SERVER.connect((self.HOST, self.PORT)) 
                #ak sa napoji tak to pokracuje dalej tadialto
                time.sleep(1)
                #client odosle serveru svoj public RSA kluc
                self.SERVER.send(self.public_key.save_pkcs1("PEM")) 
                #ulozi do podmienky publuc kluc servera
                self.public_server = rsa.PublicKey.load_pkcs1(self.SERVER.recv(1024))
                #client odosle zadane heslo
                self.SERVER.send(rsa.encrypt(self.password.encode(), self.public_server))
                #server overi heslo odoslanim spravi "verified"
                verify = rsa.decrypt(self.SERVER.recv(1024), self.private_key)
                verify = verify.decode()
                print(verify)
                #podmienka ktora overi ci je heslo spravne ak hej tak pokracuje
                if verify == "verified":
                    #vypise v GUI ip servera a port 
                    self.serverip.configure(text=f"{self.HOST} : {self.PORT}", fg="green")
                    #spusti funkciu audio_recv ako podproces ktora uz sluzi na recv zvuku
                    threading.Thread(target=self.audio_recv).start()
                    #zmeni hodnotu server_conn na True hlavne nato ze ked sa stlaci connect bttn znova tak to vyhodi msg box
                    self.server_conn = True
                #ak je heslo nespravne tak to vyhodi tuto podmienku
                else:
                    #GUI zmena textu
                    self.serverip.configure(text="")
                    #premena server_conn na False
                    self.server_conn = False
                    msgbox.showerror("Password", "Zlé heslo!")

            except socket.gaierror:
                self.serverip.configure(text="")
                self.server_conn = False
                msgbox.showwarning("Server", "SERVER NIEJE SPUSTENY ALEBO NEEXISTUJE!\n" + "try re-connect")

            #error handling ak sa nedokaze client pripojit na server
            except ConnectionRefusedError:
                #zmeni GUI label na prazdne
                self.serverip.configure(text="")
                self.server_conn = False
                msgbox.showwarning("Server", "SERVER NIEJE SPUSTENY ALEBO NEEXISTUJE!\n" + "try re-connect")
            except TimeoutError:
                #zmeni GUI label na prazdne
                self.serverip.configure(text="")
                self.server_conn = False
                msgbox.showwarning("Server", "SERVER NIEJE SPUSTENY ALEBO NEEXISTUJE!\n" + "try re-connect")

#toto znamena ze tento modul nemoze byt importnuty do dalsieho modulu
if __name__ == '__main__':
    #nastavi podmienku root pre Tk
    root = Tk()
    #nastavi title gui na StarShip
    root.title("StarShip")
    #velkost GUI v px
    root.geometry("230x250")
    #nastavi pozadie na tmavo modru v hexadecimal
    root.configure(bg="#212a3f")
    #nastavi ze sa neda upravovat velkost GUI / velkost je fixnuta
    root.resizable(False, False)
    #vyvola konkretnu triedu s argumentom root pre GUI
    StarShip(root)
    #main loop pre GUI / aby som mohol upravovat GUI v celom kode
    root.mainloop()

#ak je tento modul importnuty do ineho modulu tak to vykona tuto podmienku
if __name__ != '__main__':
    print("only main modulu!")

#D3mko
