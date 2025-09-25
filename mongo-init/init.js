// MongoDB 初始化腳本
db = db.getSiblingDB('esigned');

// 建立預設管理員帳號
db.users.insertOne({
  username: "ADMIN",
  email: "ADMIN@esigned.local",
  password: "$2b$12$oxsMMrdwY8xXc9G7DSBiXuZuFc.9lgjg5.oLV48itzEby4lEj.N4S", // 1qaz@WSX
  role: "admin",
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
});

// 建立索引
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.documents.createIndex({ "uploaded_by": 1 });
db.documents.createIndex({ "signed_by": 1 });
db.documents.createIndex({ "created_at": -1 });

print("MongoDB 初始化完成");
