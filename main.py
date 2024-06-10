import customtkinter as ctk
from tkinter import filedialog, messagebox
import sqlite3
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image, ImageTk

class XMLImporterApp:
    def __init__(self, master):
        self.master = master
        master.title("Importador de XML")
        self.master.geometry("1366x768")

        # Configurar tema do customtkinter
        ctk.set_appearance_mode("dark")  # Modos: "System" (padrão), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

        self.frame = ctk.CTkFrame(master)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="Insira o CNPJ para buscar o XML:", font=ctk.CTkFont(size=14))
        self.label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        self.cnpj_entry = ctk.CTkEntry(self.frame, font=ctk.CTkFont(size=12))
        self.cnpj_entry.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        self.fetch_button = ctk.CTkButton(self.frame, text="Buscar XML", command=self.fetch_xml)
        self.fetch_button.grid(row=0, column=3, padx=5, pady=10, sticky="ew")

        self.import_button = ctk.CTkButton(self.frame, text="Importar XML", command=self.import_xml)
        self.import_button.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew")

        self.export_button = ctk.CTkButton(self.frame, text="Exportar para PDF", command=self.export_to_pdf)
        self.export_button.grid(row=1, column=2, columnspan=2, pady=20, sticky="ew")

        self.text_area = ctk.CTkTextbox(self.frame, width=100, height=30, font=("Courier", 12))
        self.text_area.grid(row=2, column=0, columnspan=4, padx=5, pady=20, sticky="nsew")

        self.signature_label = ctk.CTkLabel(master, text="Desenvolvido por GNP Tech", font=ctk.CTkFont(size=10))
        self.signature_label.pack(side=ctk.BOTTOM, pady=10)

        # Configurar expansão de colunas e linhas
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)

    def fetch_xml(self):
        cnpj = self.cnpj_entry.get()
        if not cnpj:
            messagebox.showerror("Erro", "Por favor, insira um CNPJ válido.")
            return

        try:
            xml_content = self.get_xml_from_cnpj(cnpj)
            self.display_xml_content(xml_content)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao buscar o XML do CNPJ:\n{e}")

    def get_xml_from_cnpj(self, cnpj):
        url = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe=43181007364617000107650010000006451120000727&nVersao=100&tpAmb=1&dhEmi=323031382d30392d30315431313a34323a31362d30333a3030&vNF=7.50&vICMS=0.00&digVal=645165725a5537766b33513978475a57704d7a4e793d&cIdToken=000001&cHashQRCode=DFEBEA4787BFF153CB7F4E5D805E71CA74D0AF4A"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Falha ao buscar o XML. Verifique se o CNPJ está correto ou tente novamente mais tarde.")

    def display_xml_content(self, xml_content):
        xml_dom = xml.dom.minidom.parseString(xml_content)
        pretty_xml = xml_dom.toprettyxml()

        self.text_area.delete("1.0", ctk.END)
        self.text_area.insert(ctk.END, pretty_xml)

    def import_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    xml_content = file.read()
                    self.display_xml_content(xml_content)
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao importar o arquivo XML:\n{e}")

    def export_to_pdf(self):
        xml_content = self.text_area.get("1.0", ctk.END)

        if not xml_content.strip():
            messagebox.showerror("Erro", "Nenhum conteúdo XML para exportar.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.create_pdf(file_path, xml_content)
                messagebox.showinfo("Sucesso", "XML exportado para PDF com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao exportar para PDF:\n{e}")

    def parse_nfe(self, xml_content):
        root = ET.fromstring(xml_content)
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        data = {
            'emitente': {
                'nome': root.find('.//nfe:emit/nfe:xNome', ns).text,
                'cnpj': root.find('.//nfe:emit/nfe:CNPJ', ns).text,
                'endereco': root.find('.//nfe:emit/nfe:enderEmit/nfe:xLgr', ns).text,
                'bairro': root.find('.//nfe:emit/nfe:enderEmit/nfe:xBairro', ns).text,
                'cidade': root.find('.//nfe:emit/nfe:enderEmit/nfe:xMun', ns).text,
                'uf': root.find('.//nfe:emit/nfe:enderEmit/nfe:UF', ns).text,
            },
            'destinatario': {
                'nome': root.find('.//nfe:dest/nfe:xNome', ns).text,
                'cnpj': root.find('.//nfe:dest/nfe:CNPJ', ns).text,
                'endereco': root.find('.//nfe:dest/nfe:enderDest/nfe:xLgr', ns).text,
                'bairro': root.find('.//nfe:dest/nfe:enderDest/nfe:xBairro', ns).text,
                'cidade': root.find('.//nfe:dest/nfe:enderDest/nfe:xMun', ns).text,
                'uf': root.find('.//nfe:dest/nfe:enderDest/nfe:UF', ns).text,
            },
            'produtos': []
        }

        for prod in root.findall('.//nfe:det', ns):
            produto = {
                'descricao': prod.find('.//nfe:prod/nfe:xProd', ns).text,
                'quantidade': prod.find('.//nfe:prod/nfe:qCom', ns).text,
                'valor': prod.find('.//nfe:prod/nfe:vProd', ns).text
            }
            data['produtos'].append(produto)

        return data

    def generate_danfe(self, data, output_file):
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20 * mm, height - 20 * mm, "DANFE")

        # Dados do Emitente
        c.setFont("Helvetica", 10)
        c.drawString(20 * mm, height - 40 * mm, f"Emitente: {data['emitente']['nome']}")
        c.drawString(20 * mm, height - 45 * mm, f"CNPJ: {data['emitente']['cnpj']}")
        c.drawString(20 * mm, height - 50 * mm, f"Endereço: {data['emitente']['endereco']}, Bairro: {data['emitente']['bairro']}")
        c.drawString(20 * mm, height - 55 * mm, f"Cidade: {data['emitente']['cidade']}, UF: {data['emitente']['uf']}")

        # Dados do Destinatário
        c.drawString(20 * mm, height - 70 * mm, f"Destinatário: {data['destinatario']['nome']}")
        c.drawString(20 * mm, height - 75 * mm, f"CNPJ: {data['destinatario']['cnpj']}")
        c.drawString(20 * mm, height - 80 * mm, f"Endereço: {data['destinatario']['endereco']}, Bairro: {data['destinatario']['bairro']}")
        c.drawString(20 * mm, height - 85 * mm, f"Cidade: {data['destinatario']['cidade']}, UF: {data['destinatario']['uf']}")

        # Tabela de Produtos
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20 * mm, height - 100 * mm, "Produtos")
        c.setFont("Helvetica", 10)

        y = height - 110 * mm
        c.drawString(20 * mm, y, "Descrição")
        c.drawString(100 * mm, y, "Quantidade")
        c.drawString(130 * mm, y, "Valor")

        for produto in data['produtos']:
            y -= 5 * mm
            c.drawString(20 * mm, y, produto['descricao'])
            c.drawString(100 * mm, y, produto['quantidade'])
            c.drawString(130 * mm, y, produto['valor'])

        c.save()

    def create_pdf(self, file_path, xml_content):
        data = self.parse_nfe(xml_content)
        self.generate_danfe(data, file_path)

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("1366x768")

        # Conexão com banco de dados SQLite
        self.conn = sqlite3.connect('database/users.db')
        self.create_table()

       # Frame para o conteúdo (fundo transparente)
        self.frame = ctk.CTkFrame(master, fg_color='transparent', bg_color='transparent', corner_radius=10)
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.label = ctk.CTkLabel(self.frame, text="Login", font=ctk.CTkFont(size=18), text_color='white', fg_color='transparent', bg_color='transparent')
        self.label.pack(pady=10)

        self.username_label = ctk.CTkLabel(self.frame, text="Nome de usuário:", text_color='white', fg_color='transparent', bg_color='transparent')
        self.username_label.pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.frame, fg_color='transparent', bg_color='transparent')
        self.username_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self.frame, text="Senha:", text_color='white', fg_color='transparent', bg_color='transparent')
        self.password_label.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.frame, show="*", fg_color='transparent', bg_color='transparent')
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.create_user_button = ctk.CTkButton(self.frame, text="Criar Usuário", command=self.open_create_user_window)
        self.create_user_button.pack(pady=5)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.master.destroy()
            self.open_main_app()
        else:
            messagebox.showerror("Erro", "Nome de usuário ou senha incorretos.")

    def open_create_user_window(self):
        create_user_window = ctk.CTkToplevel(self.master)
        create_user_window.title("Criar Usuário")
        create_user_window.geometry("400x300")

        label = ctk.CTkLabel(create_user_window, text="Criar Novo Usuário", font=ctk.CTkFont(size=18))
        label.pack(pady=10)

        username_label = ctk.CTkLabel(create_user_window, text="Nome de usuário:")
        username_label.pack(pady=5)
        username_entry = ctk.CTkEntry(create_user_window)
        username_entry.pack(pady=5)

        password_label = ctk.CTkLabel(create_user_window, text="Senha:")
        password_label.pack(pady=5)
        password_entry = ctk.CTkEntry(create_user_window, show="*")
        password_entry.pack(pady=5)

        def create_user():
            username = username_entry.get()
            password = password_entry.get()

            cursor = self.conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                create_user_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Nome de usuário já existe.")

        create_button = ctk.CTkButton(create_user_window, text="Criar", command=create_user)
        create_button.pack(pady=5)

    def open_main_app(self):
        main_app_window = ctk.CTk()
        app = XMLImporterApp(main_app_window)
        main_app_window.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    login_app = LoginWindow(root)
    root.mainloop()
