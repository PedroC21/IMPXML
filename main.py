import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image, ImageTk  # Importa a biblioteca Pillow

class XMLImporterApp:
    def __init__(self, master):
        self.master = master
        master.title("Importador de XML")

        self.frame = ttk.Frame(master,  padding="40")
        self.frame.pack()

        #self.logo = Image.open("logo.png")  # Carrega o logo
        #self.logo = self.logo.resize((275, 340), Image.ANTIALIAS)  # Redimensiona o logo conforme necessário
        #self.logo = ImageTk.PhotoImage(self.logo)  # Converte o logo para o formato suportado pelo Tkinter
        #self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)
        #self.logo_label = ttk.Label(self.frame, image=self.logo)  # Cria um Label para exibir o logo

        self.label = ttk.Label(self.frame, text="Insira o CNPJ para buscar o XML:", font=("Arial", 14))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.cnpj_entry = ttk.Entry(self.frame, font=("Arial", 12))
        self.cnpj_entry.grid(row=0, column=2, padx=5, pady=10)

        self.fetch_button = ttk.Button(self.frame, text="Buscar XML", command=self.fetch_xml)
        self.fetch_button.grid(row=0, column=3, padx=5, pady=10)

        self.import_button = ttk.Button(self.frame, text="Importar XML", command=self.import_xml)
        self.import_button.grid(row=1, column=0, columnspan=2, pady=20)

        self.export_button = ttk.Button(self.frame, text="Exportar para PDF", command=self.export_to_pdf)
        self.export_button.grid(row=1, column=2, columnspan=2, pady=20)

        self.text_area = tk.Text(self.frame, width=100, height=30, font=("Courier", 12))
        self.text_area.grid(row=2, column=0, columnspan=4, padx=5, pady=20)

        self.signature_label = ttk.Label(master, text="Desenvolvido por GNP Tech", font=("Arial", 10))
        self.signature_label.pack(side=tk.BOTTOM, pady=10)

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
        # Exemplo de URL da API do SEFAZ para buscar XML de nota fiscal por CNPJ
        url = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe=43181007364617000107650010000006451120000727&nVersao=100&tpAmb=1&dhEmi=323031382d30392d30315431313a34323a31362d30333a3030&vNF=7.50&vICMS=0.00&digVal=645165725a5537766b33513978475a57704d7a4e793d&cIdToken=000001&cHashQRCode=DFEBEA4787BFF153CB7F4E5D805E71CA74D0AF4A"
        
        # Aqui você faria a solicitação HTTP à API do SEFAZ para buscar o XML correspondente ao CNPJ fornecido
        # Vou usar uma URL de exemplo para fins de demonstração
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Falha ao buscar o XML. Verifique se o CNPJ está correto ou tente novamente mais tarde.")

    def display_xml_content(self, xml_content):
        # Formata o XML para torná-lo mais legível
        xml_dom = xml.dom.minidom.parseString(xml_content)
        pretty_xml = xml_dom.toprettyxml()

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, pretty_xml)

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
        xml_content = self.text_area.get(1.0, tk.END)

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

    def create_pdf(self, file_path, xml_content):
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        xml_dom = xml.dom.minidom.parseString(xml_content)
        pretty_xml = xml_dom.toprettyxml()
        xml_paragraph = Paragraph(pretty_xml, styles["Normal"])
        doc.build([xml_paragraph])

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("1366x786")

        # Conecta ao banco de dados SQLite
        self.conn = sqlite3.connect("users.db")
        self.create_table()  # Cria a tabela de usuários se ainda não existir

        self.label = ttk.Label(master, text="Login", font=("Arial", 18))
        self.label.pack(pady=10)

        self.username_label = ttk.Label(master, text="Nome de usuário:")
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(master)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(master, text="Senha:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(master, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(master, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.create_user_button = ttk.Button(master, text="Criar Usuário", command=self.create_user)
        self.create_user_button.pack(pady=5)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT NOT NULL UNIQUE,
                           password TEXT NOT NULL)''')
        self.conn.commit()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Consulta o banco de dados para verificar as credenciais do usuário
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Sucesso", "Login bem-sucedido")
            self.master.destroy()  # Fecha a janela de login após o login bem-sucedido
            root = tk.Tk()
            app = XMLImporterApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Nome de usuário ou senha incorretos")

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Verifica se o nome de usuário já existe no banco de dados
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Erro", "Nome de usuário já existe. Escolha outro.")
        else:
            # Insere o novo usuário no banco de dados
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso.")

def main():
    root = tk.Tk()
    login_window = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()