# AuditaNF
 Projeto Final - Algoritmos I - CinUFPE 2020.1


# Descrição geral:

O AuditaNF é um aplicativo criado como uma ferramenta auxiliar no processo de fiscalização das Notas Fiscais de Serviços Eletrônicas por parte de Auditores Fiscais Tributários Municipais através da extração de informações e classificação de possíveis fraudes cometidas por empresas prestadoras de serviço.

# Dependencias:

- Versão do interpretador utilizada: Python 3.8 
- Bibliotecas Python: É necessário instalar as seguintes bibliotecas externas utilizando o comando pip:
	beautifulsoup4
	matplotlib
- Arquivo para importação: O arquivo que contém as notas fiscais a serem auditadas devem estar no formato “.csv” e tem que conter os seguintes campos: 'id','cnpj_prestador', 'nome_prestador', 'cnpj_tomador', 'nome_tomador', 'numero_nota', 'mes_comp', 'ano_comp', 'data_nota', 'competencia_nota', 'valor_total', 'base_calculo', 'aliquota','imposto', 'local_servico', 'situacao', 'responsavel_imp', 'atividade', 'descricao_servico', 'observacao', 'comp_servico', 'contrato', 'RM', 'NL', 'vlr_servicos', 'sem_isencao', 'classificacao', 'auditada', separados por “ ; ”(ponto e vírgula).

#Funcionalidades:

O sistema é composto por 5 abas, sendo elas: Importação, Notas Fiscais, Pesquisar, Gráficos e Log. Suas funcionalidades são:
	Importação: Esta aba é realizada à importação do arquivo CSV com as notas fiscais:
		Primeiro clicar no botão selecionar.
		Selecionar no computador o arquivo .csv e clicar em abrir.
		Clicar no botão importar.
	




