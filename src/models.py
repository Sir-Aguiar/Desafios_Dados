"""
Models SQLAlchemy 2.0 equivalentes a sql/criar_tabelas.sql (RF06).
O DDL do arquivo SQL e a fonte da verdade; estes models so mapeiam as tabelas.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Categoria(Base):
    __tablename__ = "categoria"
    __table_args__ = (UniqueConstraint("nome", name="uq_categoria_nome"),)

    categoria_id: Mapped[int] = mapped_column(
        SmallInteger, Identity(), primary_key=True
    )
    nome: Mapped[str] = mapped_column(String(80), nullable=False)

    conteudos: Mapped[list["Conteudo"]] = relationship(back_populates="categoria")


class Usuario(Base):
    __tablename__ = "usuario"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    interacoes: Mapped[list["Interacao"]] = relationship(back_populates="usuario")
    recomendacoes: Mapped[list["Recomendacao"]] = relationship(back_populates="usuario")


class Conteudo(Base):
    __tablename__ = "conteudo"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Artigo', 'Curso', 'Podcast', 'Vídeo')",
            name="ck_conteudo_tipo",
        ),
        CheckConstraint(
            "nivel IN ('Básico', 'Intermediário', 'Avançado')",
            name="ck_conteudo_nivel",
        ),
        CheckConstraint("carga_horaria_min >= 0", name="ck_conteudo_carga"),
    )

    conteudo_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    categoria_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(
            "categoria.categoria_id",
            name="fk_conteudo_categoria",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    nivel: Mapped[str] = mapped_column(String(20), nullable=False)
    carga_horaria_min: Mapped[int] = mapped_column(Integer, nullable=False)
    data_publicacao: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    autor: Mapped[str | None] = mapped_column(String(200))

    categoria: Mapped[Categoria] = relationship(back_populates="conteudos")
    interacoes: Mapped[list["Interacao"]] = relationship(back_populates="conteudo")
    recomendacoes: Mapped[list["Recomendacao"]] = relationship(
        back_populates="conteudo"
    )


class Interacao(Base):
    __tablename__ = "interacao"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "conteudo_id",
            "data_hora",
            name="uq_interacao_usuario_conteudo_data",
        ),
        CheckConstraint(
            "tipo_interacao IN ("
            "'avaliação', 'compartilhamento', 'conclusão', "
            "'curtida', 'início', 'visualização')",
            name="ck_interacao_tipo",
        ),
        CheckConstraint("tempo_consumido >= 0", name="ck_interacao_tempo"),
        CheckConstraint(
            "percentual_conclusao >= 0 AND percentual_conclusao <= 100",
            name="ck_interacao_percentual",
        ),
        CheckConstraint(
            "avaliacao_atribuida IS NULL OR (avaliacao_atribuida BETWEEN 1 AND 5)",
            name="ck_interacao_avaliacao",
        ),
    )

    interacao_id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "usuario.usuario_id",
            name="fk_interacao_usuario",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    conteudo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "conteudo.conteudo_id",
            name="fk_interacao_conteudo",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    tipo_interacao: Mapped[str] = mapped_column(String(30), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tempo_consumido: Mapped[int] = mapped_column(Integer, nullable=False)
    percentual_conclusao: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    avaliacao_atribuida: Mapped[int | None] = mapped_column(SmallInteger)

    usuario: Mapped[Usuario] = relationship(back_populates="interacoes")
    conteudo: Mapped[Conteudo] = relationship(back_populates="interacoes")


class Recomendacao(Base):
    __tablename__ = "recomendacao"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "posicao",
            "gerado_em",
            name="uq_recomendacao_usuario_posicao_geracao",
        ),
        UniqueConstraint(
            "usuario_id",
            "conteudo_id",
            "gerado_em",
            name="uq_recomendacao_usuario_conteudo_geracao",
        ),
        CheckConstraint(
            "pontuacao >= 0 AND pontuacao <= 100",
            name="ck_recomendacao_pontuacao",
        ),
        CheckConstraint("posicao >= 1", name="ck_recomendacao_posicao"),
        CheckConstraint(
            "classificacao IN ('Positivo', 'Estável', 'Negativo')",
            name="ck_recomendacao_classificacao",
        ),
    )

    recomendacao_id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "usuario.usuario_id",
            name="fk_recomendacao_usuario",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    conteudo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "conteudo.conteudo_id",
            name="fk_recomendacao_conteudo",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    pontuacao: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    posicao: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    classificacao: Mapped[str] = mapped_column(String(10), nullable=False)
    gerado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    usuario: Mapped[Usuario] = relationship(back_populates="recomendacoes")
    conteudo: Mapped[Conteudo] = relationship(back_populates="recomendacoes")
