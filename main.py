import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image, ImageTk  # Importa a biblioteca Pillow

class XMLImporterApp:
    def __init__(self, master):
        self.master = master
        master.title("Importador de XML")

        self.frame = ttk.Frame(master, padding="40")
        self.frame.pack()

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
        url = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe=43181007364617000107650010000006451120000727&nVersao=100&tpAmb=1&dhEmi=323031382d30392d30315431313a34323a31362d30333a3030&vNF=7.50&vICMS=0.00&digVal=645165725a5537766b33513978475a57704d7a4e793d&cIdToken=000001&cHashQRCode=DFEBEA4787BFF153CB7F4E5D805E71CA74D0AF4A"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Falha ao buscar o XML. Verifique se o CNPJ está correto ou tente novamente mais tarde.")

    def display_xml_content(self, xml_content):
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
        # Parse the XML content
        root = ET.fromstring(xml_content)
        
        # Extract necessary data
        emitente = root.find(".//emit/xNome")
        destinatario = root.find(".//dest/xNome")
        valor_total = root.find(".//total/ICMSTot/vNF")
        chave_acesso = root.find(".//infProt/chNFe")
        
        # Handle None values
        emitente_text = emitente.text if emitente is not None else "N/A"
        destinatario_text = destinatario.text if destinatario is not None else "N/A"
        valor_total_text = valor_total.text if valor_total is not None else "N/A"
        chave_acesso_text = chave_acesso.text if chave_acesso is not None else "N/A"
        
        # Create a PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Add DANFE title
        title = Paragraph("DANFE - Documento Auxiliar da Nota Fiscal Eletrônica", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Add Chave de Acesso
        chave_paragraph = Paragraph(f"Chave de Acesso: {chave_acesso_text}", styles['Normal'])
        elements.append(chave_paragraph)
        elements.append(Spacer(1, 12))

        # Add Emitente and Destinatário
        emitente_paragraph = Paragraph(f"Emitente: {emitente_text}", styles['Normal'])
        elements.append(emitente_paragraph)
        elements.append(Spacer(1, 12))

        destinatario_paragraph = Paragraph(f"Destinatário: {destinatario_text}", styles['Normal'])
        elements.append(destinatario_paragraph)
        elements.append(Spacer(1, 12))

        # Add Valor Total
        valor_paragraph = Paragraph(f"Valor Total: R$ {valor_total_text}", styles['Normal'])
        elements.append(valor_paragraph)
        elements.append(Spacer(1, 12))

        # Create a table for the items
        table_data = [['Descrição', 'Quantidade', 'Valor Unitário', 'Valor Total']]
        items = root.findall(".//det")

        for item in items:
            descricao = item.find(".//prod/xProd")
            quantidade = item.find(".//prod/qCom")
            valor_unitario = item.find(".//prod/vUnCom")
            valor_total_item = item.find(".//prod/vProd")
            
            descricao_text = descricao.text if descricao is not None else "N/A"
            quantidade_text = quantidade.text if quantidade is not None else "N/A"
            valor_unitario_text = valor_unitario.text if valor_unitario is not None else "N/A"
            valor_total_item_text = valor_total_item.text if valor_total_item is not None else "N/A"
            
            table_data.append([descricao_text, quantidade_text, valor_unitario_text, valor_total_item_text])

        table = Table(table_data, colWidths=[200, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Build the PDF
        doc.build(elements)

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("1366x768")

        # Conexão com banco de dados SQLite
        self.conn = sqlite3.connect('database/users.db')
        self.create_table()

        # Fundo da tela
        self.canvas = tk.Canvas(master, width=1366, height=768)
        self.canvas.pack()
        self.bg_image = ImageTk.PhotoImage(Image.open('background.jpg'))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)

        # Frame para o conteúdo
        self.frame = tk.Frame(master, bg='black', highlightbackground='white', highlightthickness=1, bd=10) # Frame com borda branca
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # Centraliza o frame

        self.label = ttk.Label(self.frame, text="Login", font=("Arial", 18), background='black', foreground='white')
        self.label.pack(pady=10)

        self.username_label = ttk.Label(self.frame, text="Nome de usuário:", background='black', foreground='white')
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(self.frame, text="Senha:", background='black', foreground='white')
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.create_user_button = ttk.Button(self.frame, text="Criar Usuário", command=self.open_create_user_window)
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
        create_user_window = tk.Toplevel(self.master)
        create_user_window.title("Criar Usuário")
        create_user_window.geometry("400x300")

        label = ttk.Label(create_user_window, text="Criar Novo Usuário", font=("Arial", 18))
        label.pack(pady=10)

        username_label = ttk.Label(create_user_window, text="Nome de usuário:")
        username_label.pack(pady=5)
        username_entry = ttk.Entry(create_user_window)
        username_entry.pack(pady=5)

        password_label = ttk.Label(create_user_window, text="Senha:")
        password_label.pack(pady=5)
        password_entry = ttk.Entry(create_user_window, show="*")
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

        create_button = ttk.Button(create_user_window, text="Criar", command=create_user)
        create_button.pack(pady=5)

    def open_main_app(self):
        main_app_window = tk.Tk()
        app = XMLImporterApp(main_app_window)
        main_app_window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()