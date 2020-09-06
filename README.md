# AuditaNF
 Projeto Final - Algoritmos I - CinUFPE 2020.1


# Descrição geral:

O AuditaNF é um aplicativo criado como uma ferramenta auxiliar no processo de fiscalização das Notas Fiscais de Serviços Eletrônicas por parte de Auditores Fiscais Tributários Municipais através da extração de informações e classificação de possíveis fraudes cometidas por empresas prestadoras de serviço.

# Dependencias:

- Versão do interpretador utilizada: Python 3.8 
- Bibliotecas Python: É necessário instalar as seguintes bibliotecas externas utilizando o comando pip:
	- beautifulsoup4
	- matplotlib
- Arquivo para importação: O arquivo que contém as notas fiscais a serem auditadas devem estar no formato “.csv” e conter os seguintes campos separados por “;”(ponto e vírgula): 'id','cnpj_prestador', 'nome_prestador', 'cnpj_tomador', 'nome_tomador', 'numero_nota', 'mes_comp', 'ano_comp', 'data_nota', 'competencia_nota', 'valor_total', 'base_calculo', 'aliquota','imposto', 'local_servico', 'situacao', 'responsavel_imp', 'atividade', 'descricao_servico', 'observacao', 'comp_servico', 'contrato', 'RM', 'NL', 'vlr_servicos', 'sem_isencao', 'classificacao', 'auditada'.


# Funcionalidades:

O sistema é composto por 5 abas, sendo elas: Importação, Notas Fiscais, Pesquisar, Gráficos e Log. Suas funcionalidades são:

- Importação: Esta aba é realizada à importação do arquivo CSV com as notas fiscais:
	- Primeiro clicar no botão selecionar.
	- Selecionar no computador o arquivo .csv e clicar em abrir.
	- Clicar no botão importar.
	
- Notas Fiscais: Nesta aba é possível exibir todas as notas fiscais importadas para o sistema com diversos filtros, Alterar o status de auditoria das notas e Excluir as notas fiscais. Cada procedimento é realizado através dos botões:
	- Exibir Notas
		- Primeiro selecionar um dos filtros:
			- Importação: Exibe as notas por ordem de importação.
			- Classificação: Exibe as notas pela nota de classificação da maior para a menor.
			- Valor total: Exibe as notas pelo valor total do maior para o menor.
			- Sem isenção: Exibe as notas ordenando primeiro as notas que descrevem serviços que não possuem isenção de imposto.
		- Selecionar o status de auditoria das notas:
			- Todas: Exibe todas as notas fiscais auditadas ou não.
			- Sim: Exibe apenas as notas que já foram auditadas.
			- Não: Exibe apenas as notas que não foram auditadas.
		- Clicar no botão Exibir Notas.
	- Marcar/Des.:
		- Primeiro selecionar as notas fiscais que deseja alterar o status.
		- Clicar no botão Marcar/Des para alterar para o status de auditada “Sim” ou “Não”.
	- Excluir Notas:
		- Primeiro selecionar as notas fiscais que deseja excluir.
		- Clicar no botão Excluir Notas.
- Pesquisar: Nesta aba é possível realizar uma pesquisa em toda base de dados.
	- Digitar a informação que deseja localizar e clicar no botão Pesquisar.
	
- Gráficos: Nesta aba são exibidos 4 tipos de gráficos:
	- Valor total das notas: Exibe um gráfico em formato de barras onde o Y é composto pelo nome das empresas e o X é composto pelo valor total das notas de cada empresa.
	- Nº de notas com fraudes: Exibe um gráfico em formato de barras onde o Y é composto pelo nome das empresas e o X é composto pela quantidade de notas fiscais que apresentaram classificação maior ou igual à 1.
	- Valor total de notas fiscais com fraudes: Exibe um gráfico em formato de barras onde o Y é composto pelo nome das empresas e o X é composto pela soma do valor total de todas as notas que apresentaram classificação maior ou igual à 1.
	- Valor total de NF com serviços sem isenção: Exibe um gráfico em formato de barras onde o Y é composto pelo nome das empresas e o X é composto pela soma do valor total de todas as notas que apresentaram descrição de serviço sem isenção de imposto.
	
- LOG: Esta tela é exibido o log de todas as transações de INSERT, UPDATE e DELETE no banco de dados do sistema.