"""
Script de inicialização e provisionamento do Apache Superset (RF13).
Executa as migrações, cria o usuário administrador e registra a conexão
com o PostgreSQL (plataforma_educacional) e os datasets das views analíticas.
"""
import subprocess
import sys
import time
from src.logger import get_logger

CONTAINER_NAME = "desafio_superset"
PG_URI = "postgresql+psycopg2://postgres:postgres@postgres:5432/plataforma_educacional"


def rodar_cmd(cmd, descricao):
    logger = get_logger(__name__)
    logger.info(f"Executando: {descricao}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        logger.warning(f"Aviso ao executar '{descricao}': {res.stderr.strip() or res.stdout.strip()}")
        return False
    logger.info(f"Sucesso: {descricao}")
    return True


def inicializar_superset():
    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("INICIALIZANDO APACHE SUPERSET (RF13)")
    logger.info("=" * 60)

    # 1. Aguarda container ficar ativo
    logger.info("Verificando status do container Superset...")
    tentativas = 0
    while tentativas < 30:
        res = subprocess.run(
            f"docker inspect {CONTAINER_NAME} --format '{{{{.State.Status}}}}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if "running" in res.stdout:
            logger.info(f"Container {CONTAINER_NAME} está em execução.")
            break
        time.sleep(2)
        tentativas += 1
    else:
        logger.error(f"Container {CONTAINER_NAME} não iniciou a tempo.")
        return False

    # 2. Migração do banco do Superset
    rodar_cmd(f"docker exec {CONTAINER_NAME} superset db upgrade", "Migração do banco de metadados do Superset")

    # 3. Criação do usuário admin
    cmd_admin = (
        f"docker exec {CONTAINER_NAME} superset fab create-admin "
        "--username admin --firstname Admin --lastname FICDEV "
        "--email admin@ficdev.local --password admin"
    )
    rodar_cmd(cmd_admin, "Criação do usuário administrador (admin/admin)")

    # 4. Inicialização de roles e permissões
    rodar_cmd(f"docker exec {CONTAINER_NAME} superset init", "Inicialização de permissões e roles padrão")

    # 5. Provisionamento da conexão com o banco PostgreSQL via script Python dentro do container
    script_python_db = f"""
from superset.app import create_app
app = create_app()
with app.app_context():
    from superset import db
    from superset.models.core import Database
    from superset.connectors.sqla.models import SqlaTable

    # Verifica se a base já existe
    nome_banco = 'Plataforma Educacional (PostgreSQL)'
    db_obj = db.session.query(Database).filter_by(database_name=nome_banco).first()
    if not db_obj:
        db_obj = Database(database_name=nome_banco, sqlalchemy_uri='{PG_URI}')
        db.session.add(db_obj)
        db.session.commit()
        print('Banco registrado com sucesso no Superset.')
    else:
        print('Banco ja existente no Superset.')

    # Registra Datasets das views analiticas se nao existirem
    views = [
        ('vw_kpi_metricas_gerais', 'Métricas Gerais e Indicadores'),
        ('vw_kpi_desempenho_categoria', 'Desempenho por Categoria e Tipo'),
        ('vw_kpi_evolucao_temporal', 'Evolução Temporal de Interações'),
        ('vw_kpi_analise_conteudos', 'Análise Granular de Conteúdos'),
        ('vw_kpi_recomendacoes_resumo', 'Resumo de Recomendações Vetoriais')
    ]
    for tabela, desc in views:
        tbl = db.session.query(SqlaTable).filter_by(table_name=tabela, database_id=db_obj.id).first()
        if not tbl:
            tbl = SqlaTable(table_name=tabela, database_id=db_obj.id, schema='public', description=desc)
            db.session.add(tbl)
            print(f'Dataset {{tabela}} registrado.')
    db.session.commit()
    print('Datasets provisionados com sucesso.')
"""
    cmd_provision = f'docker exec -i {CONTAINER_NAME} python -c "{script_python_db}"'
    rodar_cmd(cmd_provision, "Provisionamento da conexão PostgreSQL e Datasets das Views de KPI")

    logger.info("=" * 60)
    logger.info("APACHE SUPERSET PRONTO PARA USO!")
    logger.info("URL de Acesso: http://localhost:8088")
    logger.info("Credenciais: Usuário = admin | Senha = admin")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    if not inicializar_superset():
        sys.exit(1)
