// RF07 — consultas de verificacao dos comentarios persistidos
// Banco: plataforma_educacional / colecao comentarios
// Executar apos a carga (python -m src.main):
//   mongosh mongodb://localhost:27017/plataforma_educacional mongodb/consultas.js

// Contagem total
print("total comentarios:", db.comentarios.countDocuments({}));

// Inserir (exemplo; a carga do pipeline usa upsert pela tripla de negocio)
db.comentarios.updateOne(
  { usuario_id: 104, conteudo_id: 28, data: ISODate("2026-08-20T00:00:00Z") },
  {
    $setOnInsert: {
      usuario_id: 104,
      conteudo_id: 28,
      avaliacao: 5,
      comentario: "Conteudo introdutorio, claro e objetivo.",
      tags: ["didatico", "iniciante", "python"],
      data: ISODate("2026-08-20T00:00:00Z"),
      categoria: "Inteligencia Artificial",
    },
  },
  { upsert: true }
);

// Comentarios de determinado conteudo
const amostra = db.comentarios.findOne({}, { conteudo_id: 1 });
if (amostra) {
  print("comentarios do conteudo", amostra.conteudo_id);
  printjson(
    db.comentarios
      .find(
        { conteudo_id: amostra.conteudo_id },
        { _id: 0, usuario_id: 1, avaliacao: 1, comentario: 1, tags: 1, data: 1 }
      )
      .limit(10)
      .toArray()
  );
}

// Localizar documentos por tag
print("documentos com tag nlp:");
printjson(
  db.comentarios
    .find({ tags: "nlp" }, { _id: 0, usuario_id: 1, conteudo_id: 1, tags: 1, avaliacao: 1 })
    .limit(10)
    .toArray()
);

// Filtrar avaliacoes pela nota
print("avaliacoes com nota 5:");
print("  ", db.comentarios.countDocuments({ avaliacao: 5 }));
print("avaliacoes com nota >= 4:");
print("  ", db.comentarios.countDocuments({ avaliacao: { $gte: 4 } }));

printjson(
  db.comentarios
    .find({ avaliacao: 5 }, { _id: 0, usuario_id: 1, conteudo_id: 1, avaliacao: 1, comentario: 1 })
    .limit(5)
    .toArray()
);

// Agregar quantidade de comentarios por categoria
print("comentarios por categoria:");
printjson(
  db.comentarios
    .aggregate([
      { $group: { _id: "$categoria", quantidade: { $sum: 1 } } },
      { $sort: { quantidade: -1, _id: 1 } },
    ])
    .toArray()
);
