# Automação de inventário de recursos AWS com Python.

## Introdução

### O objetivo principal deste script é automatizar e centralizar a coleta de informações da infraestrutura na AWS, transformando um processo de horas em uma execução de segundos.

> Pontos-chave:
> - <b>Centralizar:</b> Reunir dados de múltiplos serviços da AWS (atualmente EC2 e RDS) em um único local.
> - <b>Automatizar:</b> Eliminar a necessidade de cliques manuais e navegação no console da AWS para tarefas de inventário.
> - <b>Padronizar:</b> Gerar relatórios consistentes e fáceis de compartilhar (em formato Excel), com informações sempre no mesmo formato.
> - <b>Fornecer Visibilidade Profunda:</b> Extrair detalhes que muitas vezes não são óbvios no console, como o Nome da AMI, Key Pairs associados e até mesmo executar comandos para verificar versões de software dentro das instâncias.

## O fluxo de trabalho é simples e seguro:
1. <b>Configuração Segura:</b> O script lê as credenciais de acesso de um arquivo de ambiente (.env) local, garantindo que informações sensíveis não fiquem expostas no código.
2. <b>Conexão com a AWS:</b> Utiliza o Boto3, o SDK oficial da AWS, para se conectar de forma segura à nossa conta e interagir com as APIs dos serviços.
3. <b>Coleta Inteligente de Dados:</b>
    - Para cada serviço (EC2, RDS), o script faz chamadas de API otimizadas.
    - Ele não apenas pega dados básicos, mas também realiza "consultas em duas etapas" para enriquecer as informações (por exemplo, busca o ID da AMI e depois usa esse ID para encontrar o nome legível da imagem).
4. <b>Apresentação e Exportação:</b>
    - Os dados são exibidos no terminal em tabelas claras e coloridas para uma verificação rápida.
    - Ao final, o script pergunta de forma interativa se o usuário deseja exportar os dados.
    - Se sim, ele gera um relatório em Excel (.xlsx) com abas separadas para cada serviço (EC2, RDS), pronto para ser analisado, arquivado ou compartilhado.


## Como usar:
### Baixe o projeto usando o comando:
> git clone https://github.com/carlosfilho1/aws-script.git

### Crie um arquivo dentro do projeto '.env' e copie as informações da sua conta AWS (Access Key)
> <b>aws_access_key_id=</b> < SUAS CRENDENCIAIS > <br>
> <b>aws_secret_access_key=</b> < SUAS CRENDENCIAIS > <br>
> <b>aws_session_token=</b> < SUAS CRENDENCIAIS > <br>
> <b>AWS_REGION=</b>us-east-1<br>
> <i>obs: A regiao coloquei default como us-east-1, caso seja outra regiao precisa ser alterado.</i><br>
> <i>obs²:</i> Informações como <b>aws_session_token</b> pode ser opcional, caso tenha apenas uma conta.

## Executando o projeto.
### Crie uma variável de ambiente com o comando abaixo:
> python3 -m venv env

### Execute a variável de ambiente:
> source env/bin/activate

### Logo apos de ativar a variavel de ambiente instale as 5 bibliotecas abaixo:
> - pip install boto3
> - pip install python-dotenv
> - pip install tabulate
> - pip install rich
> - pip install pandas openpyxl

### Apos concluir todo o processo, execute o projeto.

> python3 listar_instancias_ec2.py

### <b>Caso apresente algum erro, verifique suas crendenciais.</b>
