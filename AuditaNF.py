from typing import List
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter.ttk import Progressbar
from tkinter.ttk import Combobox
from tkinter import messagebox
import sqlite3
from datetime import datetime
import csv
import re
from unicodedata import normalize
from bs4 import BeautifulSoup
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')

""" CLASSE DE CONEXÃO COM BANCO DE DADOS """

class ConectarDB:

    def __init__(self):

        self.con = sqlite3.connect('AuditaNF.db')
        self.cur = self.con.cursor()
        self.criarTabela()

    def criarTabela(self):
        """Cria a tabela caso a mesma não exista."""
        try:
            self.cur.execute("""create table if not exists notasfiscais (
                     id integer primary key autoincrement ,
                     cnpj_prestador integer,
                     nome_prestador varchar,
                     cnpj_tomador varchar,
                     nome_tomador varchar,
                     numero_nota integer,
                     mes_comp integer,
                     ano_comp integer,
                     data_nota varchar,
                     competencia_nota integer,
                     valor_total float,
                     base_calculo float,
                     aliquota float,
                     imposto float,
                     local_servico varchar,
                     situacao varchar,
                     responsavel_imp varchar,
                     atividade varchar,
                     descricao_servico text,
                     observacao text,
                     comp_servico varchar,
                     contrato varchar,
                     rm varchar,
                     nl varchar,
                     vlr_servicos float,
                     sem_isencao varchar,
                     classificacao integer,
                     auditada varchar)""")
            self.con.commit()
        except Exception as err:
            Log().inserirLog("ERRO ao Criar Tabelas, motivo: " + str(err))

    def inserirRegistro(self, comando:str):

        try:
            self.cur.execute(comando)
        except Exception as err:
            Log().inserirLog("FALHA ao inserir registro, motivo: "+ str(err))
            Log().inserirLog("REVERTENDO operação (rollback)")
            self.con.rollback()
        else:
            self.con.commit()
            Log().inserirLog(comando)
        finally:
            self.con.close()

    def consultarRegistros(self, comando:str)->List[tuple]:
        """Consulta registros da tabela.
        Se não houver dados é retornada uma lista vazia [].
        """
        try:
            resultado = self.cur.execute(comando).fetchall()
        finally:
            self.con.close()

        return resultado

    def alterarRegistro(self, comando:str):
        """Alterar uma linha da tabela"""
        try:
            self.cur.execute(comando)
        except Exception as err:
            Log().inserirLog("FALHA na alteração do registro, motivo "+ str(err))
            Log().inserirLog("REVERTENDO operação (rollback)")
            self.con.rollback()
        else:
            self.con.commit()
            Log().inserirLog(comando)
        finally:
            self.con.close()

    def removerRegistro(self, comando:str):
        """Remove uma linha da tabela"""
        try:
            self.cur.execute(comando)
        except Exception as err:
            Log().inserirLog("FALHA ao remover registro, motivo: "+ str(err))
            Log().inserirLog("REVERTENDO operação (rollback)")
            self.con.rollback()
        else:
            self.con.commit()
            Log().inserirLog(comando)
        finally:
            self.con.close()

# Converte string de valores em Float
def MoedaToFloat(valor:str)->float:
    valor = str(valor)
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")
    try:
        float(valor)
    except:
        valor = 0
    return float(valor)

# Converte uma data ou intervalo de datas em uma tupla competência(mes,ano)
def selecionaCompetencia(data:str)->tuple:
    data = data.replace("-", "/")                                  #substitui o separador "-" por "/"
    data = data.replace(".","/")                                   #substitui o separador "." por "/"
    if len(data)<= 10:                                             # se o tamanho da string data for <=10
        data = data.split('/')                                     # separa os numeros removendo a "/"
        if len(data[len(data) - 1]) == 2:                          # se o tamanho do ano for = 2
            data[len(data) - 1] = int(data[len(data) - 1]) + 2000  # transforma o ano de AA para AAAA
        competencia = (int(data[1]),int(data[2]))                  # define a competencia (mes,ano)
    else:
        data = data.split()                                        #separa as datas
        data = data[len(data)-1]                                   #seleciona apenas a última data
        data = data.split('/')                                     # separa os numeros removendo a "/"
        if len(data[len(data) - 1]) == 2:                          # se o tamanho do ano for = 2
            data[len(data) - 1] = int(data[len(data) - 1]) + 2000  # transforma o ano de AA para AAAA
        competencia = (int(data[1]), int(data[2]))                 # define a competencia (mes,ano)

    return competencia                                             #Retorna uma Tupla(mes,ano)

#Transformar uma string em data.
def StringToDate(data:str)->datetime:
    data = data.replace("-", "/")  # substitui o separador "-" por "/"
    data = data.replace(".", "/")  # substitui o separador "." por "/"
    data = datetime.strptime(data,'%d/%m/%Y').date() #Transforma a String em DATA
    return data

def selecionarArquivoEntrada():
    arquivo = filedialog.askopenfilename(filetypes = (("csv","*.csv"),("CSV","*.CSV")))
    localImportacao.insert(0, arquivo)

def importarNotas():

    local = '{}'.format(localImportacao.get())
    with open(local, newline='') as numlinhas:
        linhas = csv.DictReader(numlinhas, delimiter=';')
        totalLinhas = sum(1 for line in linhas)
        numlinhas.close()
    contadorBarraProgressao = 0
    with open(local, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:

            # recebe, remove as tags HTML e normaliza o campo Observação da Nota
            try:
                observ = row['observacao']
            except KeyError as err:
                messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                break
            soup = BeautifulSoup(observ, 'html.parser')  # REMOVE HTML
            norm = normalize('NFKD', soup.text).encode('ASCII', 'ignore').decode('ASCII')  # REMOVE ACENTOS,Ç...

            # Recebe e normaliza o campo de Descrição do Serviço da Nota
            try:
                descricao_serv = row['descricao_servico']
            except KeyError as err:
                messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                break
            descricao = normalize('NFKD', descricao_serv).encode('ASCII', 'ignore').decode('ASCII')

            # REGRA01 - Encontrar Data do período do serviço:
            comp_servico = re.findall('\d{2}\.\d{2}\.\d{2,4}.a.\d{2}\.\d{2}\.\d{2,4}', soup.text, re.I)
            if comp_servico == []:
                comp_servico = re.findall('\d{2}\/\d{2}\/\d{2}.a.\d{2}\/\d{2}\/\d{2}', soup.text, re.I)
                if comp_servico == []:
                    comp_servico = re.findall('\d{2}\/\d{2}\/\d{2}.à.\d{2}\/\d{2}\/\d{2}', soup.text, re.I)
                    if comp_servico == []:
                        comp_servico = re.findall('\d{2}\/\d{2}\/\d{4}.a.\d{2}\/\d{2}\/\d{4}', soup.text, re.I)
                        if comp_servico == []:
                            comp_servico = re.findall('...\/\d{2}.a....\/\d{2}', soup.text, re.I)
                            if comp_servico == []:
                                comp_servico = re.findall('\d{2}\.\d{2}\.\d{4}', soup.text, re.I)
                                if comp_servico == []:
                                    comp_servico = re.findall('\d{2}\/\d{2}\/\d{2,4}', soup.text, re.I)

            # REGRA02 - Encontrar o número do contrato:
            contrato = re.findall('\d{4}\.\d{7}\.\d{2}\.\d{1}', soup.text)
            if contrato == []:
                contrato = re.findall('\d{1}\.\d{3}\.\d{7}\.\d{2}\-\d{1}', soup.text)
                if contrato == []:
                    contrato = re.findall('\d{4}\.\d{7}\.\d{2}\-\d{2}', soup.text)

            # REGRA03 - Encontrar o número do Relatório de Medição (RM)
            rm = re.findall('RM.\d{1,3}|RM..\d{1,3}|RM.no.\d{1,3}', norm, re.I)

            # REGRA04 - Encontrar a número da Nota de Liquidação (NL) NL nº 6674571
            nl = re.findall('NL.00000\d{6,7}|NL..00000\d{6,7}|NL.:.00000\d{6,7}', soup.text)
            if nl == []:
                nl = re.findall('NL.\d{6,7}|NL..\d{6,7}|NL.:.\d{6,7}', soup.text)
                if nl == []:
                    nl = re.findall('NL.no.\d{6,7}', norm, re.I)

            # REGRA05 - Encontrar valores dos serviços
            vlrservicoobs = re.findall('\d{1,3}.\d{3}.\d{3},\d{2}|\d{1,3}.\d{3},\d{2}|\d{1,3},\d{2}', soup.text, re.I)
            vlrservicos = 0
            for x in vlrservicoobs:
                # print(MoedaToFloat(x))
                vlrservicos += MoedaToFloat(x)
                vlrservicos = round(vlrservicos, 2)

            # REGRA06 - Encontrar serviços sem isenção  (Desmobilização) R$ 270.435,79 (Assistencia Pre Operacional) R$ 2.230.813,68
            sem_isencao = re.findall('condicionamento', soup.text, re.I)
            sem_isencao += re.findall('desmobiliza...', soup.text, re.I)
            sem_isencao += re.findall('.assistencia.pre.operacional|.assist.pre.operacional', soup.text, re.I)
            sem_isencao += re.findall('condicionamento', descricao, re.I)
            sem_isencao += re.findall('desmobiliza...', descricao, re.I)
            sem_isencao += re.findall('.assistencia.pre.operacional|.assist.pre.operacional', descricao, re.I)

            # Variavel que arquiva o resultado da classificação
            classificacao = 0
            # CLASSIFICAÇÃO 01 - Classifica a Regra01 do período serviço x competência nota
            if comp_servico == []:
                classificacao += 0
            else:
                try:
                    if (row['mes_comp'], row['ano_comp']) == selecionaCompetencia(
                            comp_servico[len(comp_servico) - 1]):  # verifica se a competencia da nt
                        classificacao += 0                         # é a mesma do periodo do servico
                    else:
                        classificacao += 1
                except KeyError as err:
                    messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                    break

            # CLASSIFICAÇÃO 02 - Base de Calculo X Valor Total das notas sem isenção
            try:
                if MoedaToFloat(row['valor_total']) == MoedaToFloat(row['base_calculo']):  # se o base de calculo da nota for = ao da regra05
                    classificacao += 0         # não somar classificacao
                else:
                    if row['aliquota'] != 0:
                        classificacao += 1
            except KeyError as err:
                messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                break

            # CLASSIFICAÇÃO 03 - CLASSIFICA A REGRA06 DE EXTRAÇÃO

            if sem_isencao != []:
                classificacao += 1

            # CLASSIFICAÇÃO 04 - PERIODO DE EMISSÃO x Aliquota ISS
            datafinal = '15/02/2015'  # Data de Encerramento da Isenção Total
            try:
                if StringToDate(row['data_nota']) >= StringToDate(datafinal):
                    if row['aliquota'] == '' or int(row['aliquota']) == 0:
                        classificacao += 1
            except KeyError as err:
                messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                break

            #INSERIR NOTAS NO BANCO DE DADOS
            db = ConectarDB()
            obs = norm.replace('"',' ') #remove as "" do campo de observação antes de iserir na base de dados
            try:
                db.inserirRegistro(
                    'INSERT INTO notasfiscais(cnpj_prestador, nome_prestador, cnpj_tomador, nome_tomador, numero_nota, mes_comp, ano_comp, data_nota, competencia_nota, valor_total, base_calculo, aliquota, imposto, local_servico, situacao, responsavel_imp, atividade, descricao_servico, observacao, comp_servico, contrato, rm, nl, vlr_servicos, sem_isencao, classificacao, auditada) values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","Não")'.format(
                        row['cnpj_prestador'], str(row['nome_prestador']), row['cnpj_tomador'], str(row['nome_tomador']),
                        row['numero_nota'], row['mes_comp'], row['ano_comp'], row['data_nota'], row['competencia_nota'],
                        row['valor_total'], row['base_calculo'], row['aliquota'], row['imposto'], row['local_servico'],
                        row['situacao'], row['responsavel_imp'], row['atividade'], row['descricao_servico'], obs,
                        ','.join(comp_servico), ','.join(contrato), ','.join(rm), ','.join(nl), vlrservicos,
                        ','.join(sem_isencao), classificacao))
            except KeyError as err:
                messagebox.showwarning('Atenção', 'Campo {} não encontrado!'.format(err))
                break

            #MOSTRAR IMPORTACAO NA CAIXA DE TEXTO DA TELA DE IMPORTAÇÃO
            caixaTexto.insert(END, "Importação da Nota Fiscal n° {} CNPJ: {} Data de emissão: {} processada \n".format(row['numero_nota'],row['cnpj_prestador'],row['data_nota'] ))
            # barra de progressao
            contadorBarraProgressao = contadorBarraProgressao + 1
            barraDeProgresso['value'] = int((contadorBarraProgressao * 100) / totalLinhas)
            window.update()

def pesquisarNotas():
    db = ConectarDB()
    treeViewPqs.delete(*treeViewPqs.get_children()) #limpa o treeview antes de uma nova pesquisa
    tuplas = db.consultarRegistros('SELECT * FROM notasfiscais where cnpj_prestador LIKE "%{texto}%" OR cnpj_tomador LIKE "%{texto}%" OR nome_prestador LIKE "%{texto}%" OR nome_tomador LIKE "%{texto}%" OR numero_nota LIKE "%{texto}%" OR mes_comp LIKE "%{texto}%" OR ano_comp LIKE "%{texto}%" OR data_nota LIKE "%{texto}%" OR valor_total LIKE "%{texto}%" OR base_calculo LIKE "%{texto}%" OR aliquota LIKE "%{texto}%" OR imposto LIKE "%{texto}%" OR local_servico LIKE "%{texto}%" OR situacao LIKE "%{texto}%" OR responsavel_imp LIKE "%{texto}%" OR atividade LIKE "%{texto}%" OR descricao_servico LIKE "%{texto}%" OR observacao LIKE "%{texto}%" OR comp_servico LIKE "%{texto}%" OR contrato LIKE "%{texto}%" OR sem_isencao LIKE "%{texto}%"'.format(texto=textoPesquisa.get()))
    index = iid = 0

    if tuplas == []:
        messagebox.showinfo('Informação', 'Nenhum registro encontrado')
    else:
        for row in tuplas:
            treeViewPqs.insert("", index, iid, values=row)
            index = iid = index + 1

class Log:
    def __init__(self):
        self.arquivo = None
        self.dataatual = datetime.now()
        with open("log.txt","a") as self.arquivo: #Caso arquivo log.txt não exista cria um novo quando o sitema é iniciado.
            pass
        self.arquivo.close()

    def inserirLog(self,texto):
        with open("log.txt", "a") as self.arquivo:
            self.arquivo.write(str(self.dataatual.strftime("%x"+" %X "))+ texto + "\n")
            self.arquivo.close()
            self.atualizaLog()
            self.arquivo.close()

    def lerLog(self):
        with open("log.txt","r") as self.arquivo:
            log = self.arquivo.readlines()
            self.arquivo.close()
            return log

    def atualizaLog(self):
        textoLog.delete(1.0, END)
        for x in self.lerLog():
            textoLog.insert(END, x)

def exibirTodasNF():
    db = ConectarDB()
    treeViewNF.delete(*treeViewNF.get_children())  # limpa o treeview antes de uma nova pesquisa
    auditada = filtroNFauditada.get()
    if auditada == "Todas":
        tuplas = db.consultarRegistros('SELECT * FROM notasfiscais order by {filtro}'.format(filtro=selecaoFiltroNF.get()))
    else:
        tuplas = db.consultarRegistros('SELECT * FROM notasfiscais where auditada = "{audit}" order by {filtro}'.format(filtro=selecaoFiltroNF.get(),audit=auditada))
    index = iid = 0
    if tuplas == []:
        messagebox.showinfo('Informação', 'Nenhuma nota fiscal encontrada')
    else:
        for row in tuplas:
            treeViewNF.insert("", index, iid, values=row)
            index = iid = index + 1

def alterarNotasAuditadas():
    notasParaAlterar:list = []
    for item in treeViewNF.selection():
        item_text = treeViewNF.item(item, "values")
        notasParaAlterar.append((item_text[0],item_text[27],item_text[5])) #(id, auditada, numero_nota)

    if notasParaAlterar == []:
        messagebox.showwarning('Atenção', 'Nenhuma nota selecionada')
    else:
        for x in notasParaAlterar:
            if x[1] == "Não":
                confirmarAlteracao = messagebox.askquestion('Nota Não Auditada', 'Deseja Alterar o status da NF nº {} para "Sim"?'.format(x[2]))
                if confirmarAlteracao == "yes":
                    db = ConectarDB()
                    db.alterarRegistro('UPDATE notasfiscais set auditada = "Sim" where id = {id}'.format(id=x[0]))

            if x[1] == "Sim":
                confirmarAlteracao = messagebox.askquestion('Nota Auditada', 'Deseja Alterar o status da NF nº {} para "Não"?'.format(x[2]))
                if confirmarAlteracao == "yes":
                    db = ConectarDB()
                    db.alterarRegistro('UPDATE notasfiscais set auditada = "Não" where id = {id}'.format(id=x[0]))

        treeViewNF.delete(*treeViewNF.get_children())  # limpa o treeview
        exibirTodasNF()

def excluirNotasSelecionadas():
    confirmarExclusao = messagebox.askquestion('Excluir Notas','Deseja excluir as notas selecionadas?')
    if confirmarExclusao == "yes":
        notasParaExcluir:list = []
        for item in treeViewNF.selection():
            item_text = treeViewNF.item(item,"values")
            notasParaExcluir.append(item_text[0])

        if notasParaExcluir == []:
            messagebox.showwarning('Atenção', 'Nenhuma nota selecionada')
        else:
            db = ConectarDB()
            comando = "DELETE FROM notasfiscais where id in({id})".format(id=','.join(notasParaExcluir))
            db.removerRegistro(comando)
            messagebox.showinfo('Informação', 'Nota(s) Excluída(s)')
            exibirTodasNF()

def gerarGrafico():

    if selecaoFiltroGrafico.get() == "valor_total":
        grafico.clear()
        figura.suptitle("Valor Total das Notas Fiscais")
        db = ConectarDB()
        valores = db.consultarRegistros('SELECT max(nome_prestador),sum(valor_total) FROM notasfiscais group by nome_prestador')
        if valores == []:
            messagebox.showinfo('Informação', 'Nenhuma informação encontrada')
        else:
            for x in valores:
                grafico.barh(x[0], '%.2f' % x[1])
        grafico.set(xlabel="Valores em R$")
        canvas.draw()

    if selecaoFiltroGrafico.get() == "qtr_nf_fraudes":
        grafico.clear()
        figura.suptitle("Quantidade de Notas Fraudulentas")
        db = ConectarDB()
        valores = db.consultarRegistros('SELECT max(nome_prestador),count(classificacao) FROM notasfiscais where classificacao > 0 group by nome_prestador')
        if valores == []:
            messagebox.showinfo('Informação', 'Nenhuma informação encontrada')
        else:
            for x in valores:
                grafico.barh(x[0], x[1])
        canvas.draw()

    if selecaoFiltroGrafico.get() == "vlr_nf_fraudes":
        grafico.clear()
        figura.suptitle("Valor Total das Notas Fiscais Fraudulentas")
        db = ConectarDB()
        valores = db.consultarRegistros('SELECT max(nome_prestador),sum(valor_total) FROM notasfiscais where classificacao > 0 order by nome_prestador')
        if valores == [(None,None)] or valores == []:
            messagebox.showinfo('Informação', 'Nenhuma informação encontrada')
        else:
            for x in valores:
                grafico.barh(x[0], '%.2f'%x[1])
        grafico.set(xlabel="Valores em R$")
        canvas.draw()

    if selecaoFiltroGrafico.get() == "vlr_nf_semisencao":
        grafico.clear()
        figura.suptitle("Valor Total das Notas Fiscais com Serviços Sem Isenção")
        db = ConectarDB()
        valores = db.consultarRegistros('SELECT max(nome_prestador), sum(valor_total) FROM notasfiscais where sem_isencao is not "" group by nome_prestador')
        if valores == []:
            messagebox.showinfo('Informação', 'Nenhuma informação encontrada')
        else:
            for x in valores:
                grafico.barh(x[0], '%.2f' % x[1])
        grafico.set(xlabel="Valores em R$")
        canvas.draw()

""" INICIO CONTROLE DE TELA """

window = Tk()
window.geometry('800x600')
window.resizable(width=0,height=0)
window.title("AuditaNF - Auditoria de NFS-e                          Projeto Final - Algoritmos I - 2020.1 - José Correia (jcln2@cin.ufpe.br)")

tab_control = ttk.Notebook(window) # CONTROLE DAS ABAS

""" ABA DE IMPORTAÇÃO """

abaImportacao = ttk.Frame(tab_control)
tab_control.add(abaImportacao, text=' Importação ')

lblImportacao = Label(abaImportacao, text= 'Arquivo para Importação:')
lblImportacao.place(x=3, y=19)

localImportacao = Entry(abaImportacao, font="arial 10", width=70)
localImportacao.place(height=18, width=500,x=150, y=20)

caixaTexto = scrolledtext.ScrolledText(abaImportacao, width=97, height=31)
caixaTexto.place(x=2, y=78)

barraDeProgresso = Progressbar(abaImportacao, length=790)
barraDeProgresso.place(x=2, y=50)

botaoSelecionar = Button(abaImportacao, text="Selecionar", command = selecionarArquivoEntrada)
botaoSelecionar.place(x=660, y=15)

botaoImportar = Button(abaImportacao, text="Importar",command=importarNotas)
botaoImportar.place(x=730, y=15)

"""ABA DE NOTAS FISCAIS NO BANCO DE DADOS"""

abaNotasFiscais = ttk.Frame(tab_control)
tab_control.add(abaNotasFiscais, text=' Notas Fiscais ')
treeViewNF = ttk.Treeview(abaNotasFiscais, selectmode='extended')
treeViewNF.place(height=525, width=778, x=2, y= 50)

scrollbar_horizontal = ttk.Scrollbar(abaNotasFiscais, orient='horizontal', command = treeViewNF.xview)
scrollbar_vertical = ttk.Scrollbar(abaNotasFiscais, orient='vertical', command = treeViewNF.yview)
scrollbar_horizontal.pack(side='bottom', fill=X)
scrollbar_vertical.pack(side='right', ipady=227, anchor='sw')
treeViewNF.configure(xscrollcommand=scrollbar_horizontal.set, yscrollcommand=scrollbar_vertical.set)

treeViewNF["columns"] = ['id','cnpj_prestador', 'nome_prestador', 'cnpj_tomador', 'nome_tomador', 'numero_nota', 'mes_comp',
                       'ano_comp', 'data_nota', 'competencia_nota', 'valor_total', 'base_calculo', 'aliquota',
                       'imposto', 'local_servico', 'situacao', 'responsavel_imp', 'atividade', 'descricao_servico',
                       'observacao', 'comp_servico', 'contrato', 'RM', 'NL', 'vlr_servicos', 'sem_isencao',
                       'classificacao', 'auditada']
treeViewNF["show"] = "headings"
treeViewNF.column("id",width=40, anchor="center")
treeViewNF.heading("id", text="id")
treeViewNF.column("cnpj_prestador",width=80, anchor="center")
treeViewNF.heading("cnpj_prestador", text="cnpj_prestador")
treeViewNF.column("nome_prestador",width=100, anchor="center")
treeViewNF.heading("nome_prestador", text="nome_prestador")
treeViewNF.column("cnpj_tomador",width=80, anchor="center")
treeViewNF.heading("cnpj_tomador", text="cnpj_tomador")
treeViewNF.column("nome_tomador",width=100, anchor="center")
treeViewNF.heading("nome_tomador", text="nome_tomador")
treeViewNF.column("numero_nota",width=65, anchor="center")
treeViewNF.heading("numero_nota", text="numero_nota")
treeViewNF.column("mes_comp",width=65, anchor="center")
treeViewNF.heading("mes_comp", text="mes_comp")
treeViewNF.column("ano_comp",width=65, anchor="center")
treeViewNF.heading("ano_comp", text="ano_comp")
treeViewNF.column("data_nota",width=65, anchor="center")
treeViewNF.heading("data_nota", text="data_nota")
treeViewNF.column("competencia_nota",width=65, anchor="center")
treeViewNF.heading("competencia_nota", text="competencia_nota")
treeViewNF.column("base_calculo",width=65, anchor="center")
treeViewNF.heading("base_calculo", text="base_calculo")
treeViewNF.column("local_servico",width=65, anchor="center")
treeViewNF.heading("local_servico", text="local_servico")
treeViewNF.column("situacao",width=65, anchor="center")
treeViewNF.heading("situacao", text="situacao")
treeViewNF.column("responsavel_imp",width=65, anchor="center")
treeViewNF.heading("responsavel_imp", text="responsavel_imp")
treeViewNF.column("atividade",width=65, anchor="center")
treeViewNF.heading("atividade", text="atividade")
treeViewNF.column("valor_total",width=65, anchor="center")
treeViewNF.heading("valor_total", text="valor_total")
treeViewNF.column("aliquota",width=65, anchor="center")
treeViewNF.heading("aliquota", text="aliquota")
treeViewNF.column("imposto",width=65, anchor="center")
treeViewNF.heading("imposto", text="imposto")
treeViewNF.column("descricao_servico",width=65, anchor="center")
treeViewNF.heading("descricao_servico", text="descricao_servico")
treeViewNF.column("observacao",width=65, anchor="center")
treeViewNF.heading("observacao", text="observacao")
treeViewNF.column("comp_servico",width=65, anchor="center")
treeViewNF.heading("comp_servico", text="comp_servico")
treeViewNF.column("contrato",width=65, anchor="center")
treeViewNF.heading("contrato", text="contrato")
treeViewNF.column("RM",width=65, anchor="center")
treeViewNF.heading("RM", text="RM")
treeViewNF.column("NL",width=65, anchor="center")
treeViewNF.heading("NL", text="NL")
treeViewNF.column("vlr_servicos",width=65, anchor="center")
treeViewNF.heading("vlr_servicos", text="vlr_servicos")
treeViewNF.column("sem_isencao",width=120, anchor="center")
treeViewNF.heading("sem_isencao", text="sem_isencao")
treeViewNF.column("classificacao",width=80, anchor="center")
treeViewNF.heading("classificacao", text="classificacao")
treeViewNF.column("auditada",width=80, anchor="center")
treeViewNF.heading("auditada", text="auditada")

frameFiltro = Frame(abaNotasFiscais, width=500, height=30, borderwidth=2,relief="groove")
frameFiltro.place(x=10, y= 14)

lblfiltroNF = Label(abaNotasFiscais, text= 'Filtros:')
lblfiltroNF.place(x=12,y=1)

selecaoFiltroNF = StringVar()  #armazena o valor selecionado do Radiobutton
filtroNFimportacao = Radiobutton(frameFiltro, text="Importação", value = "id", variable=selecaoFiltroNF)
filtroNFimportacao.place(x=0)
filtroNFimportacao.select()
filtroNFclassificacao = Radiobutton(frameFiltro, text="Classificação", value = "classificacao desc", variable=selecaoFiltroNF)
filtroNFclassificacao.place(x=90)
filtroNFvalorTotal = Radiobutton(frameFiltro, text="Valor Total", value = "valor_total desc", variable=selecaoFiltroNF)
filtroNFvalorTotal.place(x=185)
filtroNFservSemIsencao = Radiobutton(frameFiltro, text="Sem Isenção", value = "sem_isencao desc", variable=selecaoFiltroNF)
filtroNFservSemIsencao.place(x=270)
lblNFauditada = Label(frameFiltro, text= 'Auditada:')
lblNFauditada.place(x=365,y=2)
filtroNFauditada = Combobox(frameFiltro, width=6)
filtroNFauditada['values'] = ("Todas","Sim","Não",)
filtroNFauditada.current(0)
filtroNFauditada.place(x=425,y=2)

botaoExibirNF = Button(abaNotasFiscais, text=" Exibir Notas ", command = exibirTodasNF)
botaoExibirNF.place(x=520, y=15)

botaoAuditada = Button(abaNotasFiscais, text=" Marcar/Des. ", command = alterarNotasAuditadas)
botaoAuditada.place(x=610, y=15)

botaoExcluirNF = Button(abaNotasFiscais, text=" Excluir Notas ", command = excluirNotasSelecionadas)
botaoExcluirNF.place(x=700, y=15)

""" ABA DE PESQUISA """

abaPesquisa = ttk.Frame(tab_control)
tab_control.add(abaPesquisa, text=' Pesquisar ')

textoPesquisa = Entry(abaPesquisa, font="arial 10", width=70)
textoPesquisa.place(height=18, width=650,x=30, y=20)

treeViewPqs = ttk.Treeview(abaPesquisa, selectmode='browse')
treeViewPqs.place(height=507, width=777, x=2,y=50)
scrollbar_horizontal = ttk.Scrollbar(abaPesquisa, orient='horizontal', command = treeViewPqs.xview)
scrollbar_vertical = ttk.Scrollbar(abaPesquisa, orient='vertical', command = treeViewPqs.yview)
scrollbar_horizontal.pack(side='bottom', fill=X)
scrollbar_vertical.pack(side='right', ipady=228, anchor='sw')
treeViewPqs.configure(xscrollcommand=scrollbar_horizontal.set, yscrollcommand=scrollbar_vertical.set)

treeViewPqs["columns"] = ['id','cnpj_prestador', 'nome_prestador', 'cnpj_tomador', 'nome_tomador', 'numero_nota', 'mes_comp',
                       'ano_comp', 'data_nota', 'competencia_nota', 'valor_total', 'base_calculo', 'aliquota',
                       'imposto', 'local_servico', 'situacao', 'responsavel_imp', 'atividade', 'descricao_servico',
                       'observacao', 'comp_servico', 'contrato', 'RM', 'NL', 'vlr_servicos', 'sem_isencao',
                       'classificacao','auditada']
treeViewPqs["show"] = "headings"
treeViewPqs.column("id",width=40, anchor="center")
treeViewPqs.heading("id", text="id")
treeViewPqs.column("cnpj_prestador", width=80, anchor="center")
treeViewPqs.heading("cnpj_prestador", text="cnpj_prestador")
treeViewPqs.column("nome_prestador", width=100, anchor="center")
treeViewPqs.heading("nome_prestador", text="nome_prestador")
treeViewPqs.column("cnpj_tomador", width=30, anchor="center")
treeViewPqs.heading("cnpj_tomador", text="cnpj_tomador")
treeViewPqs.column("nome_tomador", width=65, anchor="center")
treeViewPqs.heading("nome_tomador", text="nome_tomador")
treeViewPqs.column("numero_nota", width=65, anchor="center")
treeViewPqs.heading("numero_nota", text="numero_nota")
treeViewPqs.column("mes_comp", width=65, anchor="center")
treeViewPqs.heading("mes_comp", text="mes_comp")
treeViewPqs.column("ano_comp", width=65, anchor="center")
treeViewPqs.heading("ano_comp", text="ano_comp")
treeViewPqs.column("data_nota", width=65, anchor="center")
treeViewPqs.heading("data_nota", text="data_nota")
treeViewPqs.column("competencia_nota", width=65, anchor="center")
treeViewPqs.heading("competencia_nota", text="competencia_nota")
treeViewPqs.column("base_calculo", width=65, anchor="center")
treeViewPqs.heading("base_calculo", text="base_calculo")
treeViewPqs.column("local_servico", width=65, anchor="center")
treeViewPqs.heading("local_servico", text="local_servico")
treeViewPqs.column("situacao", width=65, anchor="center")
treeViewPqs.heading("situacao", text="situacao")
treeViewPqs.column("responsavel_imp", width=65, anchor="center")
treeViewPqs.heading("responsavel_imp", text="responsavel_imp")
treeViewPqs.column("atividade", width=65, anchor="center")
treeViewPqs.heading("atividade", text="atividade")
treeViewPqs.column("valor_total", width=65, anchor="center")
treeViewPqs.heading("valor_total", text="valor_total")
treeViewPqs.column("aliquota", width=65, anchor="center")
treeViewPqs.heading("aliquota", text="aliquota")
treeViewPqs.column("imposto", width=65, anchor="center")
treeViewPqs.heading("imposto", text="imposto")
treeViewPqs.column("descricao_servico", width=65, anchor="center")
treeViewPqs.heading("descricao_servico", text="descricao_servico")
treeViewPqs.column("observacao", width=65, anchor="center")
treeViewPqs.heading("observacao", text="observacao")
treeViewPqs.column("comp_servico", width=65, anchor="center")
treeViewPqs.heading("comp_servico", text="comp_servico")
treeViewPqs.column("contrato", width=65, anchor="center")
treeViewPqs.heading("contrato", text="contrato")
treeViewPqs.column("RM", width=65, anchor="center")
treeViewPqs.heading("RM", text="RM")
treeViewPqs.column("NL", width=65, anchor="center")
treeViewPqs.heading("NL", text="NL")
treeViewPqs.column("vlr_servicos", width=65, anchor="center")
treeViewPqs.heading("vlr_servicos", text="vlr_servicos")
treeViewPqs.column("sem_isencao", width=65, anchor="center")
treeViewPqs.heading("sem_isencao", text="sem_isencao")
treeViewPqs.column("classificacao", width=65, anchor="center")
treeViewPqs.heading("classificacao", text="classificacao")
treeViewPqs.column("auditada", width=65, anchor="center")
treeViewPqs.heading("auditada", text="auditada")

botaoPesquisar = Button(abaPesquisa, text="Pesquisar", command = pesquisarNotas)
botaoPesquisar.place(x=700, y=15)

""" ABA GRAFICOS"""

abaGraficos = ttk.Frame(tab_control)
tab_control.add(abaGraficos, text=' Gráficos ')

selecaoFiltroGrafico = StringVar()  #armazena o valor selecionado do Radiobutton

filtroGRvalorTotalNF = Radiobutton(abaGraficos, text="Valor Total das Notas", value = "valor_total", variable=selecaoFiltroGrafico)
filtroGRvalorTotalNF.place(x=20,y=15)
filtroGRvalorTotalNF.select()
filtroQtdNFfraude = Radiobutton(abaGraficos, text="Nº de Notas com Fraudes", value = "qtr_nf_fraudes", variable=selecaoFiltroGrafico)
filtroQtdNFfraude.place(x=20,y=45)
filtroVlrTotalNFfraude = Radiobutton(abaGraficos, text="Vlr Total de NF com Fraudes", value = "vlr_nf_fraudes", variable=selecaoFiltroGrafico)
filtroVlrTotalNFfraude.place(x=250,y=15)
filtroVlrTotalsemIsencao = Radiobutton(abaGraficos, text="Vlr Total de NF com serviços sem isenção", value = "vlr_nf_semisencao", variable=selecaoFiltroGrafico)
filtroVlrTotalsemIsencao.place(x=250,y=45)

botaoGerarGrafico = Button(abaGraficos, text=" Gerar Gráfico ", command = gerarGrafico)
botaoGerarGrafico.place(x=650,y=20)

frameGrafico = Frame(abaGraficos, borderwidth=2,relief="groove")
frameGrafico.place(x=2, y= 80)

figura = Figure(figsize=(7.9,4.5),dpi=100)
grafico = figura.add_subplot(111)

valores:list = []
for x in valores:
    grafico.barh(x[0],x[1])

canvas = FigureCanvasTkAgg(figura, master=frameGrafico)
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, frameGrafico)
toolbar.update()
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

""" ABA DE LOG """

abaLog = ttk.Frame(tab_control)
tab_control.add(abaLog, text=' LOG ')

textoLog = scrolledtext.ScrolledText(abaLog, width=97, height=35)
textoLog.place(x=2, y=5)
for x in Log().lerLog():
    textoLog.insert(END, x)

""" FIM CONTROLE DA TELA"""

tab_control.pack(expand=1, fill='both')
window.mainloop()


