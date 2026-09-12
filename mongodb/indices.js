// RF07 — índices e validador da coleção comentarios
// Banco: plataforma_educacional (docker-compose.yml / MONGO_DB)
// Espelhado em src/persistencia_mongo.py (aplicado na carga do pipeline).
//
// Uso no mongosh:
//   mongosh mongodb://localhost:27017/plataforma_educacional mongodb/indices.js

const VALIDADOR = {
  $jsonSchema: {
    bsonType: "object",
    required: [
      "usuario_id",
      "conteudo_id",
      "avaliacao",
      "comentario",
      "tags",
      "data",
      "categoria",
    ],
    properties: {
      usuario_id: { bsonType: ["int", "long"], description: "identificador do usuario" },
      conteudo_id: { bsonType: ["int", "long"], description: "identificador do conteudo" },
      avaliacao: {
        bsonType: ["int", "long"],
        minimum: 1,
        maximum: 5,
        description: "nota de 1 a 5",
      },
      comentario: { bsonType: "string" },
      tags: {
        bsonType: "array",
        items: { bsonType: "string" },
      },
      data: { bsonType: "date" },
      categoria: { bsonType: "string", minLength: 1 },
    },
  },
};

const colecoes = db.getCollectionNames();
if (colecoes.includes("comentarios")) {
  db.runCommand({
    collMod: "comentarios",
    validator: VALIDADOR,
    validationLevel: "strict",
    validationAction: "error",
  });
} else {
  db.createCollection("comentarios", {
    validator: VALIDADOR,
    validationLevel: "strict",
    validationAction: "error",
  });
}

db.comentarios.createIndex(
  { usuario_id: 1, conteudo_id: 1, data: 1 },
  { unique: true, name: "uq_comentario_usuario_conteudo_data" }
);
db.comentarios.createIndex(
  { conteudo_id: 1 },
  { name: "ix_comentario_conteudo" }
);
db.comentarios.createIndex(
  { tags: 1 },
  { name: "ix_comentario_tags" }
);
db.comentarios.createIndex(
  { avaliacao: 1 },
  { name: "ix_comentario_avaliacao" }
);
db.comentarios.createIndex(
  { categoria: 1 },
  { name: "ix_comentario_categoria" }
);

print("Colecao comentarios: validador e indices aplicados.");
