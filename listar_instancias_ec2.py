import os
import boto3
import pandas as pd
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table


def listar_instancias_rds(rds_client, console):
    """
    Busca e exibe instâncias RDS em uma tabela formatada.
    """
    console.print("\n🔍 Listando instâncias RDS na AWS...", style="bold blue")     
    headers = ["🔖 Nome ", "🆔 ID da Instância ", "🔧 Tipo ", "🏦 Storage", "🚦 Estado ", "🌐 Endpoint ","🚪 Port ", "🎲 Engine ", "🪄 Versão ", "📅 Data Criação "]
    dados_para_retorno = []
    contagem = 0
    try:
        response = rds_client.describe_db_instances()
        db_instances = response.get('DBInstances', [])
        
        with console.status(f"[bold green]Buscando instâncias RDS na região: {aws_region}...[/bold green]"):
            response = ec2_client.describe_instances()
        
        if not db_instances:
            console.print("[yellow]Nenhuma instância RDS encontrada.[/yellow]")
            return headers, []

        tabela = Table(title="Instâncias RDS", header_style="bold blue", border_style="bright_black")
        for header in headers: tabela.add_column(header + " ")

        for instance in db_instances:
            contagem += 1
            
            instance_id = instance.get('DBInstanceIdentifier', 'N/A')
            instance_type = instance.get('DBInstanceClass', 'N/A')
            engine = instance.get('Engine', 'N/A')
            endpoint_dict = instance.get('Endpoint', {})
            endpoint = endpoint_dict.get('Address', 'N/A')
            port = str(endpoint_dict.get('Port', 'N/A'))
            tamanho_disco_gb = str(instance.get('AllocatedStorage', 'N/A'))
            tamanho_formatado = f"{tamanho_disco_gb} GiB" if tamanho_disco_gb != 'N/A' else 'N/A'
            versao = instance.get('EngineVersion', 'N/A')


            state = instance.get('DBInstanceStatus', 'N/A')
            
            creation_time = instance.get('InstanceCreateTime')
            launch_time_str = creation_time.strftime("%d/%m/%Y %H:%M") if creation_time else "N/A"
            
            estado_formatado = f"[grey50]{state}[/grey50]"
            if state == 'available': estado_formatado = f"[bold green]{state}[/bold green]"
            elif state == 'stopped': estado_formatado = f"[bold red]{state}[/bold red]"
            
            # Adiciona os dados brutos na lista para retorno
            dados_para_retorno.append([instance_id, instance_id, instance_type, tamanho_formatado, state, endpoint, port, engine, versao, launch_time_str])
            # Adiciona os dados formatados na tabela para exibição
            tabela.add_row(instance_id, instance_id, instance_type, tamanho_formatado, estado_formatado, endpoint, port, engine, versao, launch_time_str)

        console.print(tabela)
        console.print(f"[bold blue]Total de instâncias RDS encontradas: {contagem}[/bold blue]")
        return headers, dados_para_retorno

    except Exception as e:
        console.print(f"[bold red]Erro ao listar instâncias RDS: {e}[/bold red]")
        return headers, []



def listar_instancias_ec2(ec2_client, console):
    """
    Busca, exibe e retorna dados de instâncias EC2, incluindo o Nome da AMI.
    """
    console.print("\n🔍 Listando instâncias EC2 na AWS...", style="bold green")
    
    headers = ["🔖 Nome ", "🆔 ID da Instância ", "🔧 Tipo ", "🚦 Estado ", "💻 Plataforma ", "📼 Nome da AMI ", "🌐 IP Público ", "🌐 IP Privado ", "🔑 Key Pair ", "📅 Data Lançamento "]
    dados_para_retorno = []
    
    try:
        # API feita uma única vez, dentro do status.
        with console.status(f"[bold green]Buscando instâncias EC2 na região: {aws_region}...[/bold green]"):
            response = ec2_client.describe_instances()

        reservations = response.get('Reservations', [])
        
        # --- LÓGICA DA AMI ---
        ami_ids = set()
        all_instances = []
        for r in reservations:
            for instance in r['Instances']:
                all_instances.append(instance)
                if instance.get('ImageId'):
                    ami_ids.add(instance['ImageId'])

        if not all_instances:
            console.print("[yellow]Nenhuma instância EC2 encontrada.[/yellow]")
            return headers, []

        ami_map = {}
        if ami_ids:
            console.print(f" konsultando detalhes de [bold]{len(ami_ids)}[/bold] AMIs...")
            image_details = ec2_client.describe_images(ImageIds=list(ami_ids))
            for image in image_details.get('Images', []):
                ami_map[image['ImageId']] = image.get('Name', 'N/A')
        
        # --- Tabela ---
        tabela = Table(title="Instâncias EC2", header_style="bold green", border_style="bright_black")
        for header in headers:
            tabela.add_column(header)

        for instance in all_instances:
            state_raw = instance.get('State', {}).get('Name', 'N/A')
            key_pair_name = instance.get('KeyName', 'Nenhuma')
            
            instance_name = "Sem Nome"
            for tag in instance.get('Tags', []):
                if tag.get('Key') == 'Name':
                    instance_name = tag.get('Value')

            # Identificacão da plataforma
            plataforma = 'Windows' if 'Platform' in instance and instance['Platform'] == 'windows' else 'Linux/UNIX'
            
            image_id = instance.get('ImageId', 'N/A')
            ami_name = ami_map.get(image_id, image_id) # Mostrar o ID se nao tive nome.


            linha_dados_brutos = [
                instance_name,
                instance.get('InstanceId', 'N/A'),
                instance.get('InstanceType', 'N/A'),
                state_raw,
                plataforma,
                ami_name,
                instance.get('PublicIpAddress', 'N/A'),
                instance.get('PrivateIpAddress', 'N/A'),
                key_pair_name,
                instance.get('LaunchTime').strftime("%d/%m/%Y %H:%M:%S") if instance.get('LaunchTime') else "N/A"
            ]
            dados_para_retorno.append(linha_dados_brutos)

            # Prepara dados para exibição (formatados)
            estado_formatado = f"[grey50]{state_raw}[/grey50]"
            if state_raw == 'running': estado_formatado = f"[bold green]{state_raw}[/bold green]"
            elif state_raw == 'stopped': estado_formatado = f"[bold red]{state_raw}[/bold red]"
            
            tabela.add_row(
                linha_dados_brutos[0], # Nome
                linha_dados_brutos[1], # ID
                linha_dados_brutos[2], # Tipo
                estado_formatado,      # Estado Formatado 
                linha_dados_brutos[4], # Plataforma
                linha_dados_brutos[5], # Nome da AMI
                linha_dados_brutos[6], # IP Público
                linha_dados_brutos[7], # IP Privado
                linha_dados_brutos[8], # Key Pair
                linha_dados_brutos[9]  # Data Lançamento
            )
        
        
        console.print(tabela)
        console.print(f"[bold green]Total de instâncias EC2 encontradas: {len(all_instances)}[/bold green]")
        return headers, dados_para_retorno

    except ClientError as e:
        console.print(f"[bold red]Erro de Cliente Boto3 ao listar EC2: {e}[/bold red]")
        return [], []
    except Exception as e:
        console.print(f"[bold red]Ocorreu um erro inesperado ao listar EC2: {e}[/bold red]")
        return [], [] 



def exportar_para_excel(nome_arquivo, dados_ec2, headers_ec2, dados_rds, headers_rds, console):
    console.print(f"\n🔄 Exportando dados para [bold cyan]'{nome_arquivo}'[/bold cyan]...", style="bold yellow")
    try:
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            if dados_ec2:
                df_ec2 = pd.DataFrame(dados_ec2, columns=headers_ec2)
                df_ec2.to_excel(writer, sheet_name='EC2', index=False)
            if dados_rds:
                df_rds = pd.DataFrame(dados_rds, columns=headers_rds)
                df_rds.to_excel(writer, sheet_name='RDS', index=False)
        console.print(f"✅ Arquivo '{nome_arquivo}' gerado com sucesso!", style="bold green")
    except Exception as e:
        console.print(f"[bold red]❌ Falha ao exportar para Excel: {e}[/bold red]")



if __name__ == "__main__":
    console = Console()
    
    load_dotenv()
    aws_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    aws_region = os.getenv('AWS_REGION')

    if not all([aws_key_id, aws_secret_key, aws_region]):
        console.print("[bold red]❌ Erro: Verifique se o arquivo .env existe e contém as chaves necessárias.[/bold red]")
    else:
        try:
            rds_client = boto3.client(
                'rds',
                aws_access_key_id=aws_key_id,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token,
                region_name=aws_region
            )
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=aws_key_id,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token,
                region_name=aws_region
            )
            
            headers_ec2, dados_ec2 = listar_instancias_ec2(ec2_client, console)
            headers_rds, dados_rds = listar_instancias_rds(rds_client, console)


            # Menu p/ exportação
            if not dados_ec2 and not dados_rds:
                console.print("\nNenhum dado encontrado para exportar. Encerrando.", style="bold yellow")
            else:
                while True:
                    resposta = console.input("\n[bold]Deseja salvar estes dados em um arquivo Excel (XLSX)? (s/n): [/bold]").lower()
                    if resposta in ['s', 'n']: break
                    console.print("[yellow]Opção inválida. Digite 's' ou 'n'.[/yellow]")

                if resposta == 's':
                    nome_base = console.input("[bold]Digite o nome para o arquivo (sem extensão): [/bold]")
                    nome_arquivo_final = f"{nome_base}.xlsx"
                    exportar_para_excel(nome_arquivo_final, dados_ec2, headers_ec2, dados_rds, headers_rds, console)
                else:
                    console.print("Operação cancelada. Encerrando.", style="bold yellow")

        except Exception as e:
            console.print(f"[bold red]Falha crítica no script: {e}[/bold red]")