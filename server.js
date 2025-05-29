import express from 'express';
import cors from 'cors';
import svgCaptcha from 'svg-captcha';
import knexLib from 'knex';

const app = express();
app.use(cors());
app.use(express.json());

const knex = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './12306.db'
  },
  useNullAsDefault: true
});

// 初始化表
async function initDb() {
  const hasUser = await knex.schema.hasTable('user');
  if (!hasUser) {
    await knex.schema.createTable('user', table => {
      table.increments('id').primary();
      table.string('account').unique();
      table.string('password');
    });
    // 插入测试用户
    await knex('user').insert([
      { account: 'user1', password: '123456' },
      { account: 'user2', password: 'abcdef' }
    ]);
  }
  const hasTicket = await knex.schema.hasTable('ticket');
  if (!hasTicket) {
    await knex.schema.createTable('ticket', table => {
      table.increments('id').primary();
      table.string('from');
      table.string('to');
      table.string('time');
      table.integer('price');
    });
    // 插入测试车票
    await knex('ticket').insert([
      { from: '北京', to: '上海', time: '08:00', price: 560 },
      { from: '广州', to: '深圳', time: '09:30', price: 80 },
      { from: '成都', to: '重庆', time: '10:15', price: 120 }
    ]);
  }
}
await initDb();

// 车票列表接口
app.get('/api/tickets', async (req, res) => {
  const tickets = await knex('ticket').select('*');
  res.json({ code: 0, data: tickets });
});

// 用户列表接口
app.get('/api/users', async (req, res) => {
  const users = await knex('user').select('id', 'account');
  res.json({ code: 0, data: users });
});

// 登录接口（简单示例）
app.post('/api/login', async (req, res) => {
  const { account, password } = req.body;
  // 忽略验证码校验
  const user = await knex('user').where({ account, password }).first();
  if (user) {
    res.json({ code: 0, msg: '登录成功', user: { id: user.id, account: user.account } });
  } else {
    res.json({ code: 1, msg: '账户或密码错误' });
  }
});

// 验证码接口
app.get('/api/captcha', (req, res) => {
  const captcha = svgCaptcha.create({
    size: 4,
    noise: 2,
    color: true,
    background: '#ccf2ff'
  });
  res.type('svg');
  res.status(200).send(captcha.data); 
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Mock server running at http://localhost:${PORT}`);
});