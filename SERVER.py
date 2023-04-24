import socket
import pyaudio
import wave
from pydub import AudioSegment
from tkinter import *
from tkinter import ttk, filedialog
import tkinter.messagebox as msgbox
from PIL import Image, ImageTk
import threading
import time
import rsa

###################################
CLIENT_KEYS = {}
CLIENTS = {}
psw = []
ADDR_CLIENTS = []
music_path = {}

###################################
class Enterprise:
	def __init__(self, root):
		#plublic kluc servera RSA
		self.public_key = None
		#private kluc servera RSA
		self.private_key = None
		#################################
		#premenna ktora bude obsahovat hodnotu socketu
		self.SERVER = None
		#premenna s ip serverom / string
		self.HOST = None
		#premenna s portom servera / int
		self.PORT = None
		#################################
		#tieto hodnoty su len pre audio cast v streamovacej casti sa vsetky nastavuju
		#premenna s nastavenim zvuku na 16bit 
		#self.FORMAT = pyaudio.paInt16
		#premenna do ktorej sa nastavia channels 
		self.CHANNELS = 1
		#premenna ktora nastavi Hz daneho .wav filu 
		self.RATE = 44100
		#premenna s velkost odosielania napr 512,1024,2048,4096..
		self.CHUNK = 4096
        #################################
        #premenna ktora zistuje ci server pocuva alebo nie True alebo False
		self.server_lis = False
		#premenna ktora urcuje podla stlacenia tlacitka pre mikrofon ci streamovat alebo zastavit stream
		self.stream_voice = False
		#premenna ktora urcuje podla stlacenia tlacitka pre hudbu ci streamovat alebo zastavit stream
		self.stream_music = False
		self.converting = False

        #################################
		self.root = root
		self.image_icon = PhotoImage(file="image/logo.png")
		self.root.iconphoto(False, self.image_icon)

		self.listen_lbl = Label(self.root, text="", bg="#212a3f", font=10)
		self.listen_lbl.place(x=60,y=370)

		self.entry_psw = Entry(self.root, width=18)
		self.entry_psw.place(x=15, y=10)
		self.entry_psw.insert(0, "Create Password")

		self.listen_btn = Button(self.root, 
		                    text="LISTEN", 
		                    bd=0, 
		                    width=15, 
		                    height=2,
		                    command=self.listen_bttn)
		self.listen_btn.place(x=15,y=35)

		self.microp = Image.open("image/mic.png")
		self.mic_res = self.microp.resize((52, 52))
		self.mic_fin = ImageTk.PhotoImage(self.mic_res)
		#self.mic_button = PhotoImage(file="image/mic.png")
		self.mic = Button(self.root,
		        image=self.mic_fin, 
		        bg="red", 
		        bd=0,
		        command=self.thread_voice)
		self.mic.place(x=40, y=85)

		self.server_log = Image.open("image/server.png")
		self.slog_res = self.server_log.resize((300, 90))
		self.slog_fin = ImageTk.PhotoImage(self.slog_res)
		Label(self.root, image=self.slog_fin, bg="#212a3f", bd=0).place(x=27, y=280)

		self.mus = Image.open("image/music.png")
		self.musres = self.mus.resize((70, 70))
		self.mus_fin = ImageTk.PhotoImage(self.musres)
		#music_button = PhotoImage(file="image/music.png")
		self.mus_btn = Button(self.root, 
		        			image=self.mus_fin, 
		        			bg="red",
		        			width=52,
		        			height=52,
		        			command=self.thread_music, 
		        			bd=0)
		self.mus_btn.place(x=40, y=155)

		self.add_button = PhotoImage(file="image/add_file.png")
		Button(self.root, 
		            image=self.add_button, 
		            bg="#212a3f", 
		            bd=0, 
		            command=self.thread_add).place(x=42, y=220)

		self.convert = Label(self.root, text="", bg="#212a3f", font=10)
		self.convert.place(x=130, y=270)

		self.music_frame = Frame(self.root, 
		                        bd=2, 
		                        relief=RIDGE)
		self.music_frame.place(x=130, 
		                      y=10, 
		                      width=460, 
		                      height=260)

		self.client_frame = Frame(self.root,
		                     bd=2,
		                     relief=RIDGE)
		self.client_frame.place(x=360,
		                   		y=280,
		                   		width=230,
		                   		height=110)

		self.scroll_play = Scrollbar(self.music_frame)
		self.playlist = Listbox(self.music_frame, 
		                        width=150,
		                        font=("Arial", 12),
		                        bg="#333333", 
		                        fg="grey", 
		                        selectbackground="lightblue", 
		                        cursor="hand2", 
		                        bd=0, 
		                        yscrollcommand=self.scroll_play.set
		                        )

		self.scroll_client = Scrollbar(self.client_frame)
		self.clientlist = Listbox(self.client_frame, 
		                        width=100,
		                        font=("Arial", 12),
		                        bg="#333333", 
		                        fg="grey", 
		                        selectbackground="lightblue", 
		                        cursor="hand2", 
		                        bd=0, 
		                        yscrollcommand=self.scroll_client.set
		                        )

		self.scroll_play.config(command=self.playlist.yview)
		self.scroll_play.pack(side=RIGHT, fill=Y)

		self.scroll_client.config(command=self.clientlist.yview)
		self.scroll_client.pack(side=RIGHT, fill=Y)

		self.playlist.pack(side=LEFT, fill=BOTH)
		self.clientlist.pack(side=LEFT, fill=BOTH)

		msgbox.showinfo("Welcome", "Welcome on ENTERPRISE! :D")

#########################################################################
	def listen_bttn(self):
		#podmienka ak server nepocuva
		if not self.server_lis:
			#nacita zadane heslo z entry boxu v GUI
			password = str(self.entry_psw.get())
			#heslo nemoze byt prazdne a vykona sa podmienka
			if password != "":
				#podmienka server_lis sa nastavi na True co znamena ze server pocuva a disfunkcny tlacitko listen
				self.server_lis = True
				#zadane heslo sa ulozi do listu psw
				psw.append(password)
				#ak je heslo vytvorene tak server moze zacat pocuvat
				threading.Thread(target=self.connection).start()
			#else sa vykona ak heslo je zadane prazdne
			else:
				msgbox.showwarning("Password", "Vytvore heslo!")
		#ak je hodnota server_lis na True tak sa vykona tato podmienka
		else:
			msgbox.showinfo("Listenning..", "Server uz počúva!")

#########################################################################
	def connection(self):
		#automaticky si zisti ip zariadenia a na tej ip adrese zacne pocuvat
		hostname = socket.gethostname()
		#ulozi ip do premennej host
		self.HOST = socket.gethostbyname(hostname)
		#port servera sa nemeni
		self.PORT = 80
		#tu si zadefinujem do premennej nejake cislo podla toho ake cislo tolko cliento sa moze pripojit
		self.LISTENERS = 5
		#vytvorenie socketu AF_INET = IPv4, SOCK_STREAM = TCP
		self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#error handling funkcia
		try:
			#nastavenie servera na zadanu ip a port
			self.SERVER.bind((self.HOST, self.PORT))
			#GUI ukaze ze server sa nastavil na danu ip zariadenia
			self.listen_lbl.configure(text=f"Listenning > {self.HOST} : {self.PORT}", fg="green")
		#error handlig ak sa server neda spustit na konkretnej ip zariadenia
		except ConnectionRefusedError:
			msgbox.showerror("Server", f"Neda sa spustit server na adrese -> {self.HOST}: {self.PORT}")
			#vymaze list s ulozenim heslom
			psw.clear()
			#nastavi premennu na False
			self.server_lis = False

		#ak sa nevyhodi ziaden error server zacne pocvat pre 5 clientov
		self.SERVER.listen(self.LISTENERS)

		while True:
			#tu program acceptuje clientov
			CLIENT, addr = self.SERVER.accept()
			#podmienka ak je True ze sa pripojil client
			if CLIENT:
				#spusti sa podproces funkcie client_handler
				threading.Thread(target=self.client_handler, args=(CLIENT, addr) ).start()

#########################################################################
	#funkcia pre handlnutie ked sa client pripoji na server
	def client_handler(self, CLIENT, addr):
		#server si vytvori public a private RSA key pre server
		self.public_key, self.private_key = rsa.newkeys(1024)
		#server recvne najprv public kluc clienta a ulozi ho do premeny public client
		public_client = rsa.PublicKey.load_pkcs1(CLIENT.recv(1024))
		#server potom odosle svoj public kluc
		CLIENT.send(self.public_key.save_pkcs1("PEM"))
		#tu server recvne heslo od clienta a decryptne ho
		password = rsa.decrypt(CLIENT.recv(1024), self.private_key)
		password = password.decode()
		#podmienka zisti ci sa heslo z clienta rovna zadanemu heslu servera
		if password == psw[0]:
			#ulozi do dictionary CLIENT_KEYS hodnotu public_key co je RSA kluc ktory s ulozi pod kluc ip adresi clienta 
			CLIENT_KEYS[addr] = public_client
			print(CLIENT_KEYS)
			#ulozi do dictionary CLIENTS hodnotu pre komunikovanie s clientom pod kluc ip adresi clienta 
			CLIENTS[addr] = CLIENT
			print(CLIENTS)
			#ulozi skratenu teda konkretnu ip servera do listu ADDR_CLIENTS
			ADDR_CLIENTS.append(addr[:5])
			#nacita ti ip adresu do listu GUI pre zobrazenie 
			self.clientlist.insert(END, addr[:5])
			#zadefinujeme do premennej msg hodnotu verified
			msg = "verified"
			#tu odosleme clientovi hodnotu msg ak je spravne heslo
			CLIENT.send(rsa.encrypt(msg.encode(), public_client) )
		#ak sa heslo nerovna vytvorenemu heslo na servery spusti sa podmienka else
		else:
			#ulozi do premennej hodnotu ACCESS DENIED
			data = "ACCESS DENIED!!!"
			#odosle premennu data clientovi
			CLIENT.send(rsa.encrypt(data.encode(), public_client) )
			time.sleep(2)
			#ukonci prepojenie s clientom respektive ho vyhodi ak je heslo zle
			CLIENT.close()
			#vyhodi msg box ze je heslo nespravne
			msgbox.showwarning("Password", f"Wrong password from {addr!r}")

#########################################################################
	#tato funkcie je pre tlacitko pre streamovanie mikrofonu
	def thread_voice(self):
		#toto vyhodnoti ci sa convertuje mp3 file na wav, ak nie pusti dalej
		if not self.converting:
			#tu vyhodnoti ci podmienka stream_voice = False
			if not self.stream_voice:
				#ak sa rovna False spusti sa funkcia ako podproces voice
				threading.Thread(target=self.voice).start()
			#ak hodnota sa rovna True tak spusti sa podmienka else ktora vypne dany stream 
			else:
				#zmeni hodnotu stream_voice na False co vypne stream mikrofonu
				self.stream_voice = False
				#zmeni farbu tlacitka mikrofon na cervene
				self.mic.configure(bg="red")
		#podmienka else sa spusti ak convertor convertuje mp3 na wav
		else:
			msgbox.showwarning("Converting...", "Converting..., wait!")
	#tato funkcia patri tlacitku pre stream hudby
	def thread_music(self):
		#ak sa convertor neconvertuje cize ak je na hodnote False tak sa vykona if
		if not self.converting:
			#ak je vybrate co chceme streamovat za hudbu z playlistu pusti dalej
			if self.playlist.get(ACTIVE):			
				#ak je hodnota stream_music na false cize ak nestrmuje pusti dalej
				if not self.stream_music:
					#spusti sa funkcia ako podproces music pre stream hudby
					threading.Thread(target=self.music).start()
				#ak je hodnota na True tak sa vykona podmienka else
				else:
					self.mus_btn.configure(bg="red")
					#zmeni hodnotu stream_music = False co stopne stream
					self.stream_music = False
			#tato podmienka elsa sa vykona ak neni vybraty file co chceme streamovat v playliste
			else:
				msgbox.showinfo("Playlist", "Treba vybrat file z listu")
		#tato podmienka sa vykona ak chceme streamovat ale convertor convertuje mp3 na wav
		else:
			msgbox.showwarning("Converting...", "Converting..., wait!")

	#tato funkcia patri tlacitku pridanie .wav suboru do playlistu v GUI
	def thread_add(self):
		#ak convertor nekonventruje
		if not self.converting:
			#to staceni sa vykona podproces open_file
			threading.Thread(target=self.open_file).start()
		#ak convertuje tak sa vykona else
		else:
			msgbox.showwarning("Converting...", "Converting..., wait!")

#########################################################################
	#totok je podproces funkcia pre funkciu voice
	def callback(self, in_data, frame_count, time_info, status):
		#ak je aspon jeden client pripojeny cita dalej
		if ADDR_CLIENTS:
			#nastavi button mikrofonu na zeleny
			self.mic.configure(bg="green")
			#for loop funcia bude z listu ACTIVE_CLIENTS postupne vyberat ip adresi a na kazdu zvlast posielat
			for user in ADDR_CLIENTS:
				try:
					CLIENTS[user].send(in_data)

					if not self.stream_voice:
						#for loop funcia bude z dictionary CLIENTS postupne vyberat ip adresi a na kazdu zvlast posielat
						for user in ADDR_CLIENTS:
							stream_ended = "ended"
							stream_ended = stream_ended.encode()
							#tu sa to len uz odosle na konkretneho clienta
							CLIENTS[user].send(stream_ended)
						#farba mikrofonu sa zmeni na cervenu
						self.mic.configure(bg="red")
						return (None, pyaudio.paComplete)
					
					print("STREAMING!")

				#ak sa daky client odpoji tak vhandlne tento error tymto exceptnom
				except socket.error:
					threading.Thread(target=self.client_dis, args=(user, )).start()
				#ak returne naspat do voice funkcii pacontinue znamena ze sa zase odznova bude spustat tento thread 
			return (in_data, pyaudio.paContinue)
		#tento else sa spusti ak neni ziaden client pripojeny
		else:
			#nastavi farbu na cervenu mikrofonu
			self.mic.configure(bg="red")
			print("stream stopped")
			#nastavi premennu stream_voice na False
			self.stream_voice = False
			#returne pacomplete cize unoci tento thread
			return (in_data, pyaudio.paComplete)

#########################################################################
	#tato funkcia je na streamovanie mikrofonu
	def voice(self):
		#ak je aspon jeden client pripojeny
	    if CLIENTS:
	    	#ak sa stream_voice a stream_music rovna False tak bude citat dalej
	        if not self.stream_voice and not self.stream_music:
	        	#nastavi stream_voice na True
	            self.stream_voice = True
	            #for loop funcia bude z dictionary CLIENTS postupne vyberat ip adresi a na kazdu zvlast posielat
	            for user in CLIENTS:
	            	#try funkcia ak nejaky error pri posielani 
	            	try:
	            		option = "voice"
	            		option = option.encode()
	            		#tunak posle encrypnutu spravu pre daneho clienta 
	            		CLIENTS[user].send(rsa.encrypt(option, CLIENT_KEYS[user]) )
	            	#ak je daky client odpojeny alebo pocas streamu sa odpoji sa vykona tento except
	            	except socket.error:
	            		#ak je daky error spusti sa podproces client_dis ako disconnect
	            		threading.Thread(target=self.client_dis, args=(user, )).start()

	            #zadefinujeme si pyaudio
	            audio = pyaudio.PyAudio()
	            #tu otvorime nas stream ktory spusti aj thread callback ktory vykona daco a returne dalsi postup
	            stream = audio.open(format=audio.get_format_from_width(2),
	            					channels=self.CHANNELS,
									rate=self.RATE,
									input=True,
									frames_per_buffer=self.CHUNK,
									stream_callback=self.callback,
									start=True,
									)
	            while stream.is_active():
	            	time.sleep(0.1)

	        #else ktory sa spusti ak uz daky stream bezi
	        else:
	        	msgbox.showinfo("Stream", "Uz bezi jeden stream!")
	    #else ktory sa spusti ak neni ziaden client pripojeny
	    else:
	    	msgbox.showinfo("Voice", "Client neni pripojeny!")

#########################################################################
	#funkcia ktora prida zvukovy file do playlistu
	def open_file(self):
		#otvori directory pre vybratie daneho filu
	    path = filedialog.askopenfilename()
	    #rozdeli dany ciel k suboru na jednotlive casti lomitkom
	    file = path.split("/")
	    #ak sa koniec cieloveho suboru == .wav vykona sa toto if
	    if path.endswith(".wav"):
	    	#vlozi sa do playlistu ale len posledny text cieloveho linku
	    	self.playlist.insert(END, file[-1])
	    	#do dictionary sa ulozi ten posledny text cize meno toho suboru ako kluc a hodnota ako ciel k tomu suboru
	    	music_path[file[-1]] = path
	    	print(music_path)
	    #ak sa koniec path suboru rovna mp3 tak sa sputi toto elif
	    elif path.endswith(".mp3"):
	    	#nastavi premennu converting na True ze konvertuje
	    	self.converting = True
	    	#nastavi convert label na text converting s farbou cervena
	    	self.convert.configure(text="CONVERTING...", fg="red")
	    	#toto vytiahne z vybraneho mp3 filu segment
	    	sound = AudioSegment.from_mp3(path)
	    	#nastavi frame rate na 44100 Hz
	    	sound = sound.set_frame_rate(44100)
	    	#totok vlastne rozdeli nazov filu bodkou cize name.mp3 = "name", ".mp3" 
	    	wav = file[-1].split(".")
	    	#tu sa to uz convertne na konkretny wav file s takym istym nazvon ako bolo mp3
	    	wave_file = sound.export(f"musiclist/{wav[0]}.wav", format="wav")
	    	#vlozi to playlistu nazov konvertnuteho filu
	    	self.playlist.insert(END, f"{wav[0]}.wav")
	    	#tu ulozi do dictionary musci_path meno filu ako kluc a path k nemu ako hodnotu
	    	music_path[f"{wav[0]}.wav"] = f"musiclist/{wav[0]}.wav"
	    	#zmeni convert label na text converted a farbu zelena
	    	self.convert.configure(text="CONVERTED", fg="green")
	    	#zastavi vsetky procesi na 3 sekundy
	    	time.sleep(3)
	    	#zmeni label convert text na prazdny cize zmizne
	    	self.convert.configure(text="")
	    	#zmeni premenu converting na False
	    	self.converting = False
	    #ak bude vkladat file ktory neni .mp3 alebo .wav tak sa sputi tato else podmienka
	    else:
	    	msgbox.showerror("type error", "WRONG FILE! only(.mp3, .wav)")

#########################################################################
	#tatok music funkcia patri pre tlacitko pre hudbu 
	def music(self):
		#ak je aspon jeden client pripojeny
		if CLIENTS:
			#ak sa stream_music a stream_voice == False
			if not self.stream_music and not self.stream_voice:
				#nastavi stream_music premennu na True
				self.stream_music = True
				#tu sa ulozi do premennej music_name dany music file z playlistu
				music_name = self.playlist.get(ACTIVE)
				#tu sa overi ci dany music_name sa nachadza v music_path dictionry
				if music_name in music_path:
					print(music_name[0:-4])
					#try funkcia preto ak sa nejaky client odpoji alebo daky iny error
					try:
						#for loop funcia bude z dictionary CLIENTS postupne vyberat ip adresi a na kazdu zvlast posielat
						for user in CLIENTS:
							#totok sluzi nato aby client vedel co ide primat ci hudbu alebo voice
							option = "music"
							option = option.encode()
							#encryptne s RSA klucom a odosle clientovi 
							CLIENTS[user].send(rsa.encrypt(option, CLIENT_KEYS[user]) )
											#except pre to ak sa nejaky client odpoji ale stream to neprerusi
					except socket.error:
						#spusti podproces client_dis
						threading.Thread(target=self.client_dis, args=(user, )).start()
						self.mus_btn.configure(bg="red")
						#zmeni premennu stream _music na False
						self.stream_music = False
					
					#nastavi music tlacitko na zelene
					self.mus_btn.configure(bg="green")
						
					#pomocou modulu wave otvorime nas subor co chceme streamovat
					wf = wave.open(f"{music_path[music_name]}", "rb")
					#while loop nato ze dokym je stream_music na true bude sa opakovat 
					while self.stream_music:
						#tu nacita frames z wave filu
						data = wf.readframes(1024)

						try:
							#for loop funcia bude z disctionary CLIENTS postupne vyberat ip adresi a na kazdu zvlast posielat
							for user in ADDR_CLIENTS:
								#posle kazdemu clientovi postupne data
								CLIENTS[user].send(data)
								print("Streaming")
						#except pre to ak sa nejaky client odpoji ale stream to neprerusi
						except socket.error:
							#spusti podproces client_dis
							threading.Thread(target=self.client_dis, args=(user, )).start()
						if not self.stream_music:
							break
						if data == b"":
							break

					self.stream_music = False
					self.mus_btn.configure(bg="red")
					time.sleep(2)
					print("uz neni co streamovat!")
					#ak bol preruseny while loop spusti sa tento for loop
					for user in ADDR_CLIENTS:
						stop = "ended"
						stop = stop.encode()
						#co odosle clientom postupne ended co odosle prikaz na ukoncenie streamu clienta
						CLIENTS[user].send(stop)

			#totok sa spusti ak uz stream bezi
			else:
				msgbox.showinfo("Stream", "Uz bezi jeden stream!")
				self.mus_btn.configure(bg="red")
		#totok sa sputi ak neni pripojeny ziaden client
		else:
			msgbox.showinfo("Voice", "Client neni pripojeny!")
			self.mus_btn.configure(bg="red")

#########################################################################
	#tato funkcia sluzi nato ako sa nejaky client odpoji tak aby sa yo vsetkych listov odstranil nech nevyhadzuje errori
	def client_dis(self, user):
		key_list = list(CLIENTS.keys())
		index = key_list.index(user)
		#tu sa odstrani ip adressa podla indexu co sme si ulozili do premeny lebo maju taky isty index
		removed_client = ADDR_CLIENTS.pop(index)
		#vyhodi ip clienta z clienlistu v GUI
		self.clientlist.delete(index)
		#ukonci spojenie s danym clientom
		CLIENTS[user].close()
		CLIENTS.pop(user)
		print(CLIENTS)
		#vyhodi msg box ze client sa odpojil
		msgbox.showinfo("Client", f"CLient sa odpojil: {removed_client!r}")
#########################################################################
#toto sa sputi ako prve po spusteni kodu ak je program spusteny ako main ze nieje nikde importnuty do dalsieho modulu
if __name__ == "__main__":
	#zadefinujeme si Tk()
	root = Tk()
	#nastavenie title
	root.title("Enterprise")
	#velkost GUI x,y
	root.geometry("600x400")
	#nastavenie pozadia
	root.configure(bg="#212a3f")
	#prenastavovanie velkosti je zakazane 
	root.resizable(False, False)
	#zavolame triedu class do ktorej vlozime argument root
	Enterprise(root)
	#nastavime na koniec kodu mainloop gui aby sa dalo upravovat v celom kode gui
	root.mainloop()

#ak je tento modul importnuty do ineho modulu tak to vykona tuto podmienku
if __name__ != '__main__':
    print("only main modulu!")

#D3mko
