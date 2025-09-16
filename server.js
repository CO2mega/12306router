import express from 'express';
import cors from 'cors';
import svgCaptcha from 'svg-captcha';
import knexLib from 'knex';
import jwt from 'jsonwebtoken';

const app = express();
app.use(cors());
app.use(express.json());

// 修改数据库连接配置

const knex = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './12306.db'
  },
  useNullAsDefault: true,
  pool: { 
    min: 0, 
    max: 10,
    idleTimeoutMillis: 10000, // 空闲连接超时10秒
    acquireTimeoutMillis: 30000 // 获取连接超时30秒
  }
});

// 新建ticket.db数据库连接
const ticketDb = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './ticket.db'
  },
  useNullAsDefault: true,
  pool: { 
    min: 0, 
    max: 10,
    idleTimeoutMillis: 10000,
    acquireTimeoutMillis: 30000
  }
});

// 数据库连接
const stationsDb = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './stations.db'
  },
  useNullAsDefault: true,
  pool: { 
    min: 0, 
    max: 10,
    idleTimeoutMillis: 10000,
    acquireTimeoutMillis: 30000
  }
});

const trainsDb = knexLib({
  client: 'sqlite3',
  connection: {
    filename: './trains.db'
  },
  useNullAsDefault: true,
  pool: { 
    min: 0, 
    max: 10,
    idleTimeoutMillis: 10000,
    acquireTimeoutMillis: 30000
  }
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

// 初始化ticket.db表结构
async function initTicketDb() {
  // 车票表 - 记录已售出的票
  const hasTickets = await ticketDb.schema.hasTable('tickets');
  if (!hasTickets) {
    await ticketDb.schema.createTable('tickets', table => {
      table.increments('id').primary();
      table.integer('user_id').notNullable();
      table.string('train_code').notNullable(); // 车次编号
      table.string('train_full_code'); // 完整车次编号
      table.string('from_station').notNullable(); // 出发站
      table.integer('from_station_no').notNullable(); // 出发站序号
      table.string('to_station').notNullable(); // 到达站
      table.integer('to_station_no').notNullable(); // 到达站序号
      table.date('travel_date').notNullable(); // 乘车日期
      table.integer('seat_number').notNullable(); // 座位号
      table.string('status').defaultTo('booked'); // 状态：booked, cancelled
      table.timestamp('created_at').defaultTo(ticketDb.fn.now());
      table.timestamp('updated_at').defaultTo(ticketDb.fn.now());
      
      // 索引
      table.index(['train_code', 'travel_date']);
      table.index(['user_id']);
    });
  }

  // 座位占用表 - 记录每个区间的占用情况
  const hasSeatOccupancy = await ticketDb.schema.hasTable('seat_occupancy');
  if (!hasSeatOccupancy) {
    await ticketDb.schema.createTable('seat_occupancy', table => {
      table.increments('id').primary();
      table.string('train_code').notNullable(); // 车次编号
      table.date('travel_date').notNullable(); // 乘车日期
      table.integer('seat_number').notNullable(); // 座位号
      table.integer('start_station_no').notNullable(); // 起始站序号
      table.integer('end_station_no').notNullable(); // 终点站序号
      table.integer('ticket_id').notNullable(); // 关联的票ID
      table.timestamp('created_at').defaultTo(ticketDb.fn.now());
      
      // 添加唯一约束确保不会重复记录
      table.unique(['train_code', 'travel_date', 'seat_number', 'start_station_no', 'end_station_no']);
      
      // 索引
      table.index(['train_code', 'travel_date']);
      table.index(['seat_number']);
      table.index(['start_station_no', 'end_station_no']);
    });
  }
}

// 初始化所有数据库
async function initAllDatabases() {
  await initDb();
  await initTicketDb();
  console.log('所有数据库初始化完成');
}

// 启动时初始化
(async function() {
  try {
    // 初始化数据库
    await initAllDatabases();
    await ensureTicketTablesExist();
    
    // 启动服务器
    const PORT = 3000;
    const server = app.listen(PORT, () => {
      console.log(`Mock server running at http://localhost:${PORT}`);
    });
    
    // 添加服务器错误处理
    server.on('error', (error) => {
      console.error('服务器错误:', error);
    });
    
    // 添加服务器关闭处理
    server.on('close', () => {
      console.log('服务器已关闭');
    });
    
  } catch (error) {
    console.error('服务器启动失败:', error);
  }
})();

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
const authMiddleware = (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({
        code: 401,
        msg: '未授权，请先登录'
      });
    }
    
    // 验证token
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({
      code: 401,
      msg: '令牌无效或已过期'
    });
  }
};

// 确保数据库中存在必要的表
async function ensureTicketTablesExist() {
  try {
    // 创建tickets表 - 如果表已存在但缺少某些字段，先尝试添加
    if (await ticketDb.schema.hasTable('tickets')) {
      // 检查是否有changed_from字段，没有则添加
      const hasChangedFromField = await ticketDb.schema.hasColumn('tickets', 'changed_from');
      if (!hasChangedFromField) {
        await ticketDb.schema.table('tickets', table => {
          table.integer('changed_from').nullable();
        });
        console.log('tickets表添加了changed_from字段');
      }
    } else {
      // 创建全新的tickets表
      await ticketDb.schema.createTable('tickets', table => {
        table.increments('id').primary();
        table.integer('user_id').notNullable();
        table.string('train_code').notNullable();
        table.string('train_full_code');
        table.string('from_station').notNullable();
        table.integer('from_station_no').notNullable();
        table.string('to_station').notNullable();
        table.integer('to_station_no').notNullable();
        table.date('travel_date').notNullable();
        table.integer('seat_number').notNullable();
        table.string('status').defaultTo('booked');  
        table.integer('changed_from').nullable();   
        table.timestamp('created_at').defaultTo(ticketDb.fn.now());
        table.timestamp('updated_at').defaultTo(ticketDb.fn.now());
      });
      console.log('创建了新的tickets表');
    }
    
    // 创建seat_occupancy表
    if (!(await ticketDb.schema.hasTable('seat_occupancy'))) {
      await ticketDb.schema.createTable('seat_occupancy', table => {
        table.increments('id').primary();
        table.string('train_code').notNullable();
        table.date('travel_date').notNullable();
        table.integer('seat_number').notNullable();
        table.integer('start_station_no').notNullable();
        table.integer('end_station_no').notNullable();
        table.integer('ticket_id').notNullable();
        table.timestamp('created_at').defaultTo(ticketDb.fn.now());
        
        // 添加复合唯一约束
        table.unique(['train_code', 'travel_date', 'seat_number', 'start_station_no', 'end_station_no']);
      });
      console.log('创建了新的seat_occupancy表');
    }
  } catch (error) {
    console.error('确保票务表存在时出错:', error);
  }
}

// 初始化时调用
ensureTicketTablesExist();

// 登录接口
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

      // 确保返回格式正确
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

// 站点城市映射 - 更新包含所有主要城市
const city_stations = {
  "北京": ["北京", "北京西", "北京南", "北京东"],
  "上海": ["上海", "上海虹桥", "上海南", "上海西"],
  "天津": ["天津", "天津西", "天津南", "天津北"],
  "重庆": ["重庆", "重庆北", "重庆西", "重庆南"],
  "广州": ["广州", "广州南", "广州东", "广州北"],
  "深圳": ["深圳", "深圳北", "深圳东", "深圳西"],
  "成都": ["成都", "成都东", "成都南", "成都西"],
  "武汉": ["武汉", "汉口", "武昌", "武汉西"],
  "西安": ["西安", "西安北", "西安南", "西安东"],
  "南京": ["南京", "南京南", "南京北", "南京西"],
  "杭州": ["杭州", "杭州东", "杭州南", "杭州西"],
  "长沙": ["长沙", "长沙南", "长沙西", "长沙北"],
  "长春": ["长春", "长春西", "长春南", "长春北"],
  "福州": ["福州", "福州南", "福州北"],
  "贵阳": ["贵阳", "贵阳北", "贵阳东"],
  "呼和浩特": ["呼和浩特", "呼和浩特东"],
  "哈尔滨": ["哈尔滨", "哈尔滨东", "哈尔滨西", "哈尔滨北"],
  "合肥": ["合肥", "合肥南", "合肥北", "合肥西"],
  "海口": ["海口", "海口东"],
  "济南": ["济南", "济南西", "济南东"],
  "昆明": ["昆明", "昆明南", "昆明北"],
  "拉萨": ["拉萨"],
  "兰州": ["兰州", "兰州西", "兰州东"],
  "南宁": ["南宁", "南宁东", "南宁西"],
  "南昌": ["南昌", "南昌西", "南昌东"],
  "沈阳": ["沈阳", "沈阳北", "沈阳南", "沈阳东"],
  "石家庄": ["石家庄", "石家庄北", "石家庄东"],
  "太原": ["太原", "太原南", "太原东", "太原北"],
  "乌鲁木齐": ["乌鲁木齐", "乌鲁木齐南"],
  "西宁": ["西宁", "西宁西"],
  "银川": ["银川", "银川东"],
  "大连": ["大连", "大连北", "大连南"],
  "青岛": ["青岛", "青岛北", "青岛西"],
  "厦门": ["厦门", "厦门北", "厦门高崎"]
};

// 直达路线查询接口 - 修改以减少并发查询并确保连接释放
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

    // 使用单一事务进行查询站点ID
    const trx1 = await trainsDb.transaction();
    let startIds, endIds;
    
    try {
      // 查询站点ID
      const startStations = await trx1('train_routes')
        .whereIn('city', fromStations.length > 0 ? fromStations : [from])
        .distinct('station_id')
        .select('station_id');
      
      const endStations = await trx1('train_routes')
        .whereIn('city', toStations.length > 0 ? toStations : [to])
        .distinct('station_id')
        .select('station_id');
      
      // 提取站点ID数组
      startIds = startStations.map(s => s.station_id);
      endIds = endStations.map(s => s.station_id);
      
      await trx1.commit();
    } catch (err) {
      await trx1.rollback();
      throw err;
    }

    if (startIds.length === 0 || endIds.length === 0) {
      return res.json({
        code: 1,
        msg: '未找到对应的站点'
      });
    }

    // 使用单一事务查询真实站点名称
    const trx2 = await stationsDb.transaction();
    let stationIdToName = {};
    
    try {
      // 从stations.db查询真实站点名称
      const startStationNames = await trx2('stations')
        .whereIn('id', startIds)
        .select('id', 'name');
      
      const endStationNames = await trx2('stations')
        .whereIn('id', endIds)
        .select('id', 'name');
      
      // 创建站点ID到站点名称的映射
      startStationNames.forEach(station => {
        stationIdToName[station.id] = station.name;
      });
      endStationNames.forEach(station => {
        stationIdToName[station.id] = station.name;
      });
      
      await trx2.commit();
    } catch (err) {
      await trx2.rollback();
      throw err;
    }

    // 使用单一事务查询符合条件的路线
    const trx3 = await trainsDb.transaction();
    let routes;
    
    try {
      // 查询符合条件的路线 - 修改查询方式，减少子查询
      routes = await trx3.raw(`
        SELECT DISTINCT 
          a.train_code,
          a.train_full_code,
          a.station_id as start_id,
          b.station_id as end_id,
          a.station_no as start_no,
          b.station_no as end_no,
          a.run_time
        FROM train_routes a
        JOIN train_routes b ON a.train_code = b.train_code
        WHERE a.station_id IN (${startIds.join(',')})
        AND b.station_id IN (${endIds.join(',')})
        AND a.station_no < b.station_no
        ORDER BY a.train_code
        LIMIT 30
      `);
      
      await trx3.commit();
    } catch (err) {
      await trx3.rollback();
      throw err;
    }

    // 使用单一事务查询每个车次的区间占用情况
    const trx4 = await ticketDb.transaction();
    let availableSeatsMap = {};
    
    try {
      const totalSeats = 100; // 假设每个车次有100个座位
      
      // 优化查询：一次性获取所有车次的占用情况
      const trainCodes = routes.map(route => route.train_code);
      const allOccupiedSeats = await trx4('seat_occupancy')
        .whereIn('train_code', trainCodes)
        .where('travel_date', date)
        .select('train_code', 'seat_number', 'start_station_no', 'end_station_no');
      
      // 按车次分组
      const occupiedSeatsByTrain = {};
      allOccupiedSeats.forEach(seat => {
        if (!occupiedSeatsByTrain[seat.train_code]) {
          occupiedSeatsByTrain[seat.train_code] = [];
        }
        occupiedSeatsByTrain[seat.train_code].push(seat);
      });
      
      // 计算每个车次的可用座位
      for (const route of routes) {
        const trainCode = route.train_code;
        const startNo = route.start_no;
        const endNo = route.end_no;
        
        const occupiedSeats = occupiedSeatsByTrain[trainCode] || [];
        
        // 计算冲突座位数
        let conflictCount = 0;
        
        for (let seat = 1; seat <= totalSeats; seat++) {
          const hasConflict = occupiedSeats.some(record => {
            return record.seat_number === seat && 
                  !(record.end_station_no <= startNo || record.start_station_no >= endNo);
          });
          
          if (hasConflict) {
            conflictCount++;
          }
        }
        
        // 计算可用座位数
        availableSeatsMap[trainCode] = totalSeats - conflictCount;
      }
      
      await trx4.commit();
    } catch (err) {
      await trx4.rollback();
      throw err;
    }

    // 格式化结果
    const formattedRoutes = routes.map(route => {
      return {
        trainCode: route.train_code,
        trainFullCode: route.train_full_code || route.train_code,
        from: {
          station: stationIdToName[route.start_id] || from,
          sequence: route.start_no
        },
        to: {
          station: stationIdToName[route.end_id] || to,
          sequence: route.end_no
        },
        runTime: route.run_time || "未知",
        ticketsLeft: availableSeatsMap[route.train_code] || 0
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

// 修改购票接口，使用区间占用模型并保存到用户数据库
app.post('/api/tickets', authMiddleware, async (req, res) => {
  const trx = await ticketDb.transaction();
  
  try {
    const { trainCode, trainFullCode, fromStation, toStation, fromStationNo, toStationNo, travelDate } = req.body;
    const userId = req.user.id; // 从JWT令牌中获取用户ID
    
    // 参数验证
    if (!trainCode || !fromStation || !toStation || !fromStationNo || !toStationNo || !travelDate) {
      return res.json({
        code: 1,
        msg: '参数不完整'
      });
    }
    
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
    
    // 检查区间是否合法
    if (parseInt(fromStationNo) >= parseInt(toStationNo)) {
      return res.json({
        code: 1,
        msg: '出发站必须在到达站之前'
      });
    }
    
    // 假设每个车次有100个座位
    const totalSeats = 100;
    
    // 查询当前已占用的区间
    const occupiedSeats = await trx('seat_occupancy')
      .where({
        train_code: trainCode,
        travel_date: travelDate
      })
      .select('seat_number', 'start_station_no', 'end_station_no');
    
    // 找出可用座位
    const availableSeats = [];
    
    for (let seatNum = 1; seatNum <= totalSeats; seatNum++) {
      const conflicts = occupiedSeats.filter(record => {
        // 检查是否有区间重叠
        return record.seat_number === seatNum && 
               !(parseInt(record.end_station_no) <= parseInt(fromStationNo) || 
                 parseInt(record.start_station_no) >= parseInt(toStationNo));
      });
      
      if (conflicts.length === 0) {
        availableSeats.push(seatNum);
      }
    }
    
    if (availableSeats.length === 0) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '该车次在所选区间已无可用座位'
      });
    }
    
    // 分配第一个可用座位
    const assignedSeat = availableSeats[0];
    
    // 添加车票记录
    const [ticketId] = await trx('tickets').insert({
      user_id: userId,
      train_code: trainCode,
      train_full_code: trainFullCode || trainCode,
      from_station: fromStation,
      from_station_no: fromStationNo,
      to_station: toStation,
      to_station_no: toStationNo,
      travel_date: travelDate,
      seat_number: assignedSeat,
      status: 'booked'
    });
    
    // 添加座位占用记录
    await trx('seat_occupancy').insert({
      train_code: trainCode,
      travel_date: travelDate,
      seat_number: assignedSeat,
      start_station_no: fromStationNo,
      end_station_no: toStationNo,
      ticket_id: ticketId
    });
    
    await trx.commit();
    
    res.json({
      code: 0,
      msg: '购票成功',
      data: {
        ticketId,
        trainCode,
        fromStation,
        toStation,
        travelDate,
        seatNumber: assignedSeat
      }
    });
    
  } catch (error) {
    await trx.rollback();
    console.error('购票失败:', error);
    res.json({
      code: 500,
      msg: '购票失败，请稍后重试'
    });
  }
});

// 添加退票接口
app.post('/api/tickets/refund', authMiddleware, async (req, res) => {
  const trx = await ticketDb.transaction();
  
  try {
    const { ticketId } = req.body;
    const userId = req.user.id;
    
    // 查询票信息
    const ticket = await trx('tickets')
      .where({
        id: ticketId,
        user_id: userId,
        status: 'booked' // 只能退已订票
      })
      .first();
    
    if (!ticket) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '未找到有效车票或无权退票'
      });
    }
    
    // 更新车票状态
    await trx('tickets')
      .where('id', ticketId)
      .update({
        status: 'cancelled',
        updated_at: trx.fn.now()
      });
    
    // 删除座位占用记录
    await trx('seat_occupancy')
      .where('ticket_id', ticketId)
      .delete();
    
    await trx.commit();
    
    res.json({
      code: 0,
      msg: '退票成功'
    });
    
  } catch (error) {
    await trx.rollback();
    console.error('退票失败:', error);
    res.json({
      code: 500,
      msg: '退票失败，请稍后重试'
    });
  }
});

// 获取用户已购车票列表
app.get('/api/user/tickets', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // 查询用户车票
    const tickets = await ticketDb('tickets')
      .where({
        user_id: userId,
        status: 'booked'  // 只查询未退票/未改签的车票
      })
      .select(
        'id',
        'train_code as trainCode',
        'from_station as fromStation',
        'to_station as toStation',
        'travel_date as travelDate',
        'seat_number as seatNumber'
      )
      .orderBy('travel_date', 'asc');
    
    res.json({
      code: 0,
      data: {
        tickets
      }
    });
    
  } catch (error) {
    console.error('查询用户车票错误:', error);
    res.json({
      code: 500,
      msg: '查询车票失败，请稍后重试'
    });
  }
});

// 车票改签接口
app.post('/api/tickets/change', authMiddleware, async (req, res) => {
  const trx = await ticketDb.transaction();
  
  try {
    const { 
      ticketId, 
      newTrainCode, 
      newTrainFullCode,
      newFromStation, 
      newToStation, 
      newFromStationNo, 
      newToStationNo, 
      newTravelDate 
    } = req.body;
    
    const userId = req.user.id;
    
    // 查询原车票信息
    const oldTicket = await trx('tickets')
      .where({
        id: ticketId,
        user_id: userId,
        status: 'booked'
      })
      .first();
    
    if (!oldTicket) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '未找到有效车票或无权改签'
      });
    }
    
    // 参数验证
    if (!newTrainCode || !newFromStation || !newToStation || !newFromStationNo || !newToStationNo || !newTravelDate) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '改签参数不完整'
      });
    }
    
    // 验证日期
    const bookingDate = new Date(newTravelDate);
    const now = new Date();
    const maxDate = new Date();
    maxDate.setDate(now.getDate() + 30);
    
    if (bookingDate < now || bookingDate > maxDate) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '请选择合法的乘车日期（未来30天内）'
      });
    }
    
    // 检查区间是否合法
    if (parseInt(newFromStationNo) >= parseInt(newToStationNo)) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '出发站必须在到达站之前'
      });
    }
    
    // 假设每个车次有100个座位
    const totalSeats = 100;
    
    // 查询当前已占用的区间
    const occupiedSeats = await trx('seat_occupancy')
      .where({
        train_code: newTrainCode,
        travel_date: newTravelDate
      })
      .whereNot('ticket_id', ticketId)  // 排除自己的原车票
      .select('seat_number', 'start_station_no', 'end_station_no');
    
    // 找出可用座位
    const availableSeats = [];
    
    for (let seatNum = 1; seatNum <= totalSeats; seatNum++) {
      const conflicts = occupiedSeats.filter(record => {
        // 检查是否有区间重叠
        return record.seat_number === seatNum && 
               !(parseInt(record.end_station_no) <= parseInt(newFromStationNo) || 
                 parseInt(record.start_station_no) >= parseInt(newToStationNo));
      });
      
      if (conflicts.length === 0) {
        availableSeats.push(seatNum);
      }
    }
    
    if (availableSeats.length === 0) {
      await trx.rollback();
      return res.json({
        code: 1,
        msg: '该车次在所选区间已无可用座位'
      });
    }
    
    // 分配第一个可用座位
    const assignedSeat = availableSeats[0];
    
    // 取消原车票
    await trx('tickets')
      .where('id', ticketId)
      .update({
        status: 'changed',
        updated_at: trx.fn.now()
      });
    
    // 删除原来的座位占用记录
    await trx('seat_occupancy')
      .where('ticket_id', ticketId)
      .delete();
    
    // 添加新车票记录
    const [newTicketId] = await trx('tickets').insert({
      user_id: userId,
      train_code: newTrainCode,
      train_full_code: newTrainFullCode || newTrainCode,
      from_station: newFromStation,
      from_station_no: newFromStationNo,
      to_station: newToStation,
      to_station_no: newToStationNo,
      travel_date: newTravelDate,
      seat_number: assignedSeat,
      status: 'booked',
      changed_from: ticketId  // 记录改签来源
    });
    
    // 添加新座位占用记录
    await trx('seat_occupancy').insert({
      train_code: newTrainCode,
      travel_date: newTravelDate,
      seat_number: assignedSeat,
      start_station_no: newFromStationNo,
      end_station_no: newToStationNo,
      ticket_id: newTicketId
    });
    
    await trx.commit();
    
    res.json({
      code: 0,
      msg: '改签成功',
      data: {
        ticketId: newTicketId,
        trainCode: newTrainCode,
        fromStation: newFromStation,
        toStation: newToStation,
        travelDate: newTravelDate,
        seatNumber: assignedSeat
      }
    });
    
  } catch (error) {
    await trx.rollback();
    console.error('改签失败:', error);
    res.json({
      code: 500,
      msg: '改签失败，请稍后重试'
    });
  }
});

// 修改登录接口
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

      // 确保返回格式正确
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

// 修改注册接口
app.post('/api/register', async (req, res) => {
  try {
    const { account, password, captcha } = req.body;
    
    // 略过验证码校验
    
    // 检查账户是否已存在
    const existingUser = await knex('user').where({ account }).first();
    if (existingUser) {
      return res.json({ code: 1, msg: '该账户已被注册' });
    }
    
    // 直接使用明文密码插入
    const [userId] = await knex('user').insert({
      account,
      password
    });
    
    res.json({ 
      code: 0, 
      msg: '注册成功',
      data: { userId }
    });
    
  } catch (error) {
    console.error('注册错误:', error);
    res.json({ code: 500, msg: '服务器错误，请稍后重试' });
  }
});

// 添加重置密码接口
app.post('/api/reset-password', async (req, res) => {
  try {
    const { account, newPassword, confirmPassword } = req.body;
    
    // 验证密码一致性
    if (newPassword !== confirmPassword) {
      return res.json({
        code: 1,
        msg: '两次密码输入不一致'
      });
    }
    
    // 查找用户
    const user = await knex('user').where({ account }).first();
    if (!user) {
      return res.json({
        code: 1,
        msg: '用户不存在'
      });
    }
    
    // 更新密码
    await knex('user')
      .where({ account })
      .update({ password: newPassword });
    
    res.json({
      code: 0,
      msg: '密码重置成功，请重新登录'
    });
  } catch (error) {
    console.error('重置密码错误:', error);
    res.json({
      code: 500,
      msg: '重置密码失败，请稍后重试'
    });
  }
});

// 替换现有的关闭连接池代码
let isShuttingDown = false;

// 优雅关闭连接池
process.on('SIGINT', async () => {
  if (isShuttingDown) {
    return; // 防止重复触发
  }
  
  isShuttingDown = true;
  console.log('开始关闭数据库连接池...');
  
  // 添加超时保护
  const forceExitTimeout = setTimeout(() => {
    console.log('强制退出进程 - 连接池关闭超时');
    process.exit(1);
  }, 5000); // 给予更多时间完成清理
  
  try {
    await Promise.all([
      knex.destroy().catch(err => console.error('关闭主数据库连接池错误:', err)),
      ticketDb.destroy().catch(err => console.error('关闭车票数据库连接池错误:', err)),
      stationsDb.destroy().catch(err => console.error('关闭站点数据库连接池错误:', err)),
      trainsDb.destroy().catch(err => console.error('关闭列车数据库连接池错误:', err))
    ]);
    
    // 清除超时定时器
    clearTimeout(forceExitTimeout);
    
    console.log('所有数据库连接池已关闭');
    process.exit(0);
  } catch (err) {
    // 清除超时定时器
    clearTimeout(forceExitTimeout);
    
    console.error('关闭数据库连接池时出错:', err);
    process.exit(1);
  }
});

// 处理未捕获的异常
process.on('uncaughtException', (err) => {
  console.error('未捕获的异常:', err);
  // 记录错误但不退出进程
});

// 处理未处理的 Promise 拒绝
process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的 Promise 拒绝:', reason);
  // 记录错误但不退出进程
});