import express from 'express';
import cors from 'cors';
import svgCaptcha from 'svg-captcha';
import knexLib from 'knex';
import jwt from 'jsonwebtoken';

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

// 添加 JWT 密钥
const JWT_SECRET = 'your-secret-key';  // 在生产环境中应该使用环境变量

// 添加认证中间件
const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.json({ code: 401, msg: '请先登录' });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    console.error('认证错误:', error);
    res.json({ code: 401, msg: '认证失败，请重新登录' });
  }
};

// 登录接口（简单示例）
app.post('/api/login', async (req, res) => {
  const { account, password } = req.body;
  try {
    const user = await knex('user').where({ account, password }).first();
    if (user) {
      // 生成 JWT token
      const token = jwt.sign(
        { id: user.id, account: user.account },
        JWT_SECRET,
        { expiresIn: '24h' }
      );

      res.json({ 
        code: 0, 
        msg: '登录成功', 
        data: {
          token,
          user: { 
            id: user.id, 
            account: user.account 
          }
        }
      });
    } else {
      res.json({ code: 1, msg: '账户或密码错误' });
    }
  } catch (error) {
    console.error('登录错误:', error);
    res.json({ code: 500, msg: '登录失败，请重试' });
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

// 新增数据库连接
const stationsDb = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './stations.db'
  },
  useNullAsDefault: true
});

const trainsDb = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './trains.db'
  },
  useNullAsDefault: true
});

// 站点城市映射
const city_stations = {
  "北京": ["北京", "北京西", "北京南", "北京东"],
  "上海": ["上海", "上海虹桥", "上海南", "上海西"],
  "广州": ["广州", "广州南", "广州东"],
  "深圳": ["深圳", "深圳北", "深圳东"],
  "成都": ["成都", "成都东", "成都南"],
  "重庆": ["重庆", "重庆北", "重庆西"],
  "武汉": ["武汉", "武汉汉口", "武汉武昌"],
  "西安": ["西安", "西安北", "西安南"],
  "杭州": ["杭州", "杭州东", "杭州南"],
  "南京": ["南京", "南京南", "南京北"],
  "天津": ["天津", "天津西", "天津南"],
  "沈阳": ["沈阳", "沈阳北", "沈阳南"],
  "大连": ["大连", "大连北", "大连南"],
  "青岛": ["青岛", "青岛北", "青岛西"],
  "厦门": ["厦门", "厦门北", "厦门高崎"]
};

// 直达路线查询接口
app.get('/api/routes/direct', async (req, res) => {
  try {
    const { from, to, date } = req.query;

    // 验证城市参数
    if (!from || !to) {
      return res.json({ 
        code: 1, 
        msg: '请提供出发城市和目的地' 
      });
    }

    // 获取出发城市和目的地对应的站点
    const fromStations = city_stations[from] || [];
    const toStations = city_stations[to] || [];

    if (fromStations.length === 0 || toStations.length === 0) {
      return res.json({
        code: 1,
        msg: '不支持的城市'
      });
    }

    // 查询站点ID
    const startStations = await trainsDb('train_routes')
      .whereIn('city', fromStations.length > 0 ? fromStations : [from])
      .distinct('station_id')
      .select('station_id');
    
    const endStations = await trainsDb('train_routes')
      .whereIn('city', toStations.length > 0 ? toStations : [to])
      .distinct('station_id')
      .select('station_id');

    if (startStations.length === 0 || endStations.length === 0) {
      return res.json({
        code: 1,
        msg: '未找到对应的站点'
      });
    }

    // 提取站点ID数组
    const startIds = startStations.map(s => s.station_id);
    const endIds = endStations.map(s => s.station_id);

    // 从stations.db查询真实站点名称
    const startStationNames = await stationsDb('stations')
      .whereIn('id', startIds)
      .select('id', 'name');
    
    const endStationNames = await stationsDb('stations')
      .whereIn('id', endIds)
      .select('id', 'name');
    
    // 创建站点ID到站点名称的映射
    const stationIdToName = {};
    startStationNames.forEach(station => {
      stationIdToName[station.id] = station.name;
    });
    endStationNames.forEach(station => {
      stationIdToName[station.id] = station.name;
    });

    // 查询符合条件的路线
    const routes = await trainsDb.raw(`
      WITH start_routes AS (
        SELECT DISTINCT train_code, station_id, station_no, train_full_code, run_time
        FROM train_routes
        WHERE station_id IN (${startIds.join(',')})
      ),
      end_routes AS (
        SELECT DISTINCT train_code, station_id, station_no, train_full_code
        FROM train_routes
        WHERE station_id IN (${endIds.join(',')})
      )
      SELECT DISTINCT 
        s.train_code,
        s.train_full_code,
        s.station_id as start_id,
        e.station_id as end_id,
        s.station_no as start_no,
        e.station_no as end_no,
        s.run_time
      FROM start_routes s
      JOIN end_routes e ON s.train_code = e.train_code
      WHERE s.station_no < e.station_no
      ORDER BY s.train_code
      LIMIT 30
    `);

    // 假设我们在user.db中有一个daily_ticket_stats表来记录每日售票情况
    // 如果没有，我们可以默认每辆车有100个座位
    const userDb = knexLib({
      client: 'sqlite3',
      connection: {
        filename: './user.db'
      },
      useNullAsDefault: true
    });

    // 尝试查询售票统计
    let ticketStats = {};
    try {
      const stats = await userDb('daily_ticket_stats')
        .where('travel_date', date)
        .select('train_code', 'sold_count');
      
      stats.forEach(stat => {
        ticketStats[stat.train_code] = stat.sold_count || 0;
      });
    } catch (error) {
      console.log('售票统计查询失败，使用默认值:', error);
    }

    // 格式化结果
    const formattedRoutes = routes.map(route => {
      return {
        trainCode: route.train_code,
        trainFullCode: route.train_full_code || route.train_code,
        from: {
          station: stationIdToName[route.start_id] || from, // 使用stations.db中的真实站名
          sequence: route.start_no
        },
        to: {
          station: stationIdToName[route.end_id] || to, // 使用stations.db中的真实站名
          sequence: route.end_no
        },
        runTime: route.run_time || "未知", // 直接使用数据库中的run_time
        // 默认每辆车有100个座位，减去已售数量
        ticketsLeft: 100 - (ticketStats[route.train_code] || 0)
      };
    });

    res.json({
      code: 0,
      data: {
        routes: formattedRoutes,
        total: formattedRoutes.length,
        from,
        to,
        date
      }
    });

  } catch (error) {
    console.error('查询路线错误:', error);
    res.json({
      code: 500,
      msg: '查询失败，请稍后重试'
    });
  }
});

// 修改购票接口，添加认证
app.post('/api/tickets', authMiddleware, async (req, res) => {
  const trx = await userDb.transaction();
  
  try {
    const { trainCode, trainFullCode, fromStation, toStation, travelDate } = req.body;
    const userId = req.user.id;

    // 验证日期
    const bookingDate = new Date(travelDate);
    const now = new Date();
    const maxDate = new Date();
    maxDate.setDate(now.getDate() + 30);

    if (bookingDate < now || bookingDate > maxDate) {
      return res.json({
        code: 1,
        msg: '请选择合法的乘车日期（未来30天内）'
      });
    }

    // 检查余票
    const stats = await trx('daily_ticket_stats')
      .where({ train_code: trainCode, travel_date: travelDate })
      .first();

    const soldCount = stats ? stats.sold_count : 0;
    
    if (soldCount >= 100) {
      return res.json({
        code: 1,
        msg: '该车次已售罄'
      });
    }

    // 添加订单记录
    await trx('tickets').insert({
      user_id: userId,
      train_code: trainCode,
      train_full_code: trainFullCode,
      from_station: fromStation,
      to_station: toStation,
      travel_date: travelDate,
      status: 'booked'
    });

    // 更新售票统计
    await trx('daily_ticket_stats')
      .insert({
        train_code: trainCode,
        travel_date: travelDate,
        sold_count: 1
      })
      .onConflict(['train_code', 'travel_date'])
      .merge({
        sold_count: trx.raw('sold_count + 1')
      });

    await trx.commit();

    res.json({
      code: 0,
      msg: '预订成功'
    });

  } catch (error) {
    await trx.rollback();
    console.error('预订失败:', error);
    res.json({
      code: 500,
      msg: '预订失败，请稍后重试'
    });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Mock server running at http://localhost:${PORT}`);
});