<template>
  <div class="homepage">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-item" :class="{ active: activeMenu === 'ticket' }" @click="activeMenu = 'ticket'">
        <i class="iconfont">&#xe600;</i>
        车票
      </div>
      <div class="sidebar-item" :class="{ active: activeMenu === 'common' }" @click="activeMenu = 'common'">
        <i class="iconfont">&#xe601;</i>
        常用查询
      </div>
    </aside>
    <!-- 主体内容 -->
    <main class="main-content">
      <!-- 车票页面 -->
      <template v-if="activeMenu === 'ticket'">
        <!-- 查询表单 -->
        <form class="query-form" @submit.prevent="onQuery">
          <div class="form-row">
            <label>出发地</label>
            <div class="select-wrapper from-select">
              <div class="city-select" @click.stop="toggleFromCity()">{{ from || '请选择' }}</div>
              <!-- 下拉菜单 -->
              <div v-show="showFromCity" class="city-dropdown from-dropdown">
                <div class="city-list">
                  <span v-for="city in hotCities" :key="city" class="city-item" @click="selectFromCity(city)">{{ city
                    }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="form-row">
            <label>到达地</label>
            <div class="select-wrapper to-select">
              <div class="city-select" @click.stop="toggleToCity()">{{ to || '请选择' }}</div>
              <!-- 下拉菜单 -->
              <div v-show="showToCity" class="city-dropdown to-dropdown">
                <div class="city-list">
                  <span v-for="city in hotCities" :key="city" class="city-item" @click="selectToCity(city)">{{ city
                    }}</span>
                </div>
              </div>
            </div>
          </div>
          <el-form-item label="出发日期">
            <el-date-picker v-model="date" type="date" placeholder="选择日期" :disabled-date="disabledDate"
              :shortcuts="shortcuts" value-format="YYYY-MM-DD" :clearable="false" style="width: 180px" />
          </el-form-item>
          <div class="form-row options">
            <label><input type="checkbox" v-model="isStudent" /> 学生</label>
            <label><input type="checkbox" v-model="isHighSpeed" /> 高铁/动车</label>
          </div>
          <button class="query-btn" type="submit">查 询</button>
        </form>
      </template>
      <!-- 常用查询页面 -->
      <template v-else>
        <div class="common-query" v-loading="loading">
          <div class="city-list">
            <span v-for="city in hotCities" :key="city" class="city-item" :class="{ active: selectedCity === city }"
              @click="queryTrains(city)">{{ city }}</span>
          </div>
          <div v-if="trainList.length" class="train-list">
            <div class="train-list-title">{{ selectedCity }}车次列表：</div>
            <ul>
              <li v-for="train in trainList" :key="train.train_code">
                {{ train.train_code }}
                <span v-if="train.is_origin" class="train-badge origin">始发</span>
                <span v-if="train.is_terminal" class="train-badge terminal">终到</span>
              </li>
            </ul>
          </div>
          <div v-else-if="selectedCity && !loading" class="no-data">
            暂无车次数据
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import request from '@/utils/request'; // 确保导入request

const activeMenu = ref("ticket");

const from = ref("");
const to = ref("");
const date = ref(new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit'
}).replace(/\//g, '-'));
const isStudent = ref(false);
const isHighSpeed = ref(false);
const showFromCity = ref(false);
const showToCity = ref(false);
const loading = ref(false);

const hotCities = ref([
  "北京", "上海", "天津", "重庆", "长沙", "长春",
  "成都", "福州", "广州", "贵阳", "呼和浩特", "哈尔滨",
  "合肥", "杭州", "海口", "济南", "昆明", "拉萨",
  "兰州", "南宁", "南京", "南昌", "沈阳", "石家庄",
  "太原", "乌鲁木齐", "武汉", "西宁", "西安", "银川",
  "郑州", "深圳", "厦门"
]);

const selectedCity = ref("");
const trainList = ref([]);

const router = useRouter();

// 修改查询函数
async function onQuery() {
  if (!from.value || !to.value || !date.value) {
    alert('请填写完整信息');
    return;
  }

  loading.value = true;
  try {
    await router.push({
      path: '/ticket',
      query: {
        from: from.value,
        to: to.value,
        date: date.value,
        isStudent: isStudent.value,
        isHighSpeed: isHighSpeed.value  // 确保将高铁/动车选项传递给车票页面
      }
    });
  } finally {
    loading.value = false;
  }
}

// 修改城市选择逻辑，确保互斥
function toggleFromCity() {
  showFromCity.value = !showFromCity.value;
  if (showFromCity.value) {
    showToCity.value = false;  
  }
}

function toggleToCity() {
  showToCity.value = !showToCity.value;
  if (showToCity.value) {
    showFromCity.value = false;  
  }
}

// 修改选择函数
function selectFromCity(city) {
  from.value = city;
  showFromCity.value = false;
}

function selectToCity(city) {
  to.value = city;
  showToCity.value = false;
}

// 更新queryTrains函数，连接后端API
async function queryTrains(city) {
  selectedCity.value = city;
  loading.value = true;

  try {
    const response = await request.get('/api/city/trains', {
      params: { city }
    });

    if (response.data.code === 0 && response.data.data) {
      trainList.value = response.data.data; // 直接使用后端返回的列车列表
    } else {
      trainList.value = [];
      console.error('获取车次数据失败:', response.data.msg);
    }
  } catch (error) {
    console.error('查询车次出错:', error);
    trainList.value = [];
  } finally {
    loading.value = false;
  }
}

// 获取所有城市数据
async function fetchCities() {
  try {
    const response = await request.get('/api/cities');
    if (response.data.code === 0 && response.data.data) {
      hotCities.value = response.data.data;
    }
  } catch (error) {
    console.error('获取城市列表失败:', error);
  }
}

// 日期选择器的禁用日期范围
const disabledDate = (time) => {
  // 获取今天的起始时间（0时0分0秒）
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 获取30天后的结束时间（23时59分59秒）
  const maxDate = new Date()
  maxDate.setDate(today.getDate() + 30)
  maxDate.setHours(23, 59, 59, 999)

  return time.getTime() < today.getTime() || time.getTime() > maxDate.getTime()
}

// 计算日期选择器的快捷选项
const shortcuts = [
  {
    text: '今天',
    value: new Date(),
  },
  {
    text: '明天',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 1)
      return date
    })(),
  },
  {
    text: '后天',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 2)
      return date
    })(),
  },
  {
    text: '一周后',
    value: (() => {
      const date = new Date()
      date.setDate(date.getDate() + 7)
      return date
    })(),
  }
]

// 修改事件处理函数，确保正确关闭下拉框
onMounted(() => {
  // 获取城市列表
  fetchCities();

  document.addEventListener('click', (e) => {
    const fromSelect = document.querySelector('.from-select');
    const toSelect = document.querySelector('.to-select');

    if (!fromSelect?.contains(e.target)) {
      showFromCity.value = false;
    }
    if (!toSelect?.contains(e.target)) {
      showToCity.value = false;
    }
  });
});
</script>

<style scoped>
.homepage {
  display: flex;
  min-height: calc(100vh - 60px);
  background: #f7faff;
  /* 移除 padding-top: 64px; 因为这已经在 MainLayout 中处理 */
}

.sidebar {
  width: 110px;
  background: #2196f3;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 24px;
}

.sidebar-item {
  width: 100%;
  padding: 18px 0;
  text-align: center;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.85;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar-item.active,
.sidebar-item:hover {
  background: #1976d2;
  opacity: 1;
}

.iconfont {
  font-size: 22px;
  margin-bottom: 6px;
}

.main-content {
  flex: 1;
  padding: 36px 24px; /* 减小左右内边距，给更宽的内容让出空间 */
}

.query-form {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(32, 94, 201, 0.08);
  padding: 32px 36px 24px 36px;
  min-width: 520px;
  /* 增加最小宽度 */
  max-width: 560px;
  /* 增加最大宽度 */
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  position: relative;
}

.form-row label {
  width: 80px;
  color: #333;
  /* 修改颜色为统一的深色 */
  font-weight: normal;
  line-height: 40px;
  /* 与输入框高度一致 */
}

.form-row input[type="text"],
.form-row input[type="date"] {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #b7d0f7;
  border-radius: 5px;
  font-size: 15px;
  margin-right: 8px;
}

.options {
  display: flex;
  gap: 24px;
  /* 保持选项之间的间距 */
  margin-bottom: 24px;
}

.options label {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  /* 防止文字换行 */
  min-width: 80px;
  /* 确保有足够空间 */
}

.options input[type="checkbox"] {
  margin: 0;
  width: 16px;
  height: 16px;
}

.query-btn {
  width: 100%;
  background: #ff8800;
  color: #fff;
  font-size: 20px;
  border: none;
  border-radius: 6px;
  padding: 10px 0;
  margin-top: 10px;
  cursor: pointer;
  letter-spacing: 8px;
}

.city-select {
  height: 40px;
  line-height: 40px;
  padding: 0 12px;
  border: 1px solid #b7d0f7;
  border-radius: 4px;
  background: #f9fbff;
  color: #1976d2;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.select-wrapper {
  position: relative;
  flex: 1;
  min-width: 420px;
  /* 确保宽度一致 */
}

.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background: #fff;
  border: 1px solid #b7d0f7;
  border-radius: 4px;
  margin-top: 4px;
  box-shadow: 0 2px 12px rgba(32, 94, 201, 0.12);
  z-index: 1001;
  /* 提高 z-index 确保显示在最上层 */
  /* 移除这两个属性以去掉滚动条 */
  /* max-height: 300px; */
  /* overflow-y: auto; */
}

.city-list {
  display: grid;
  grid-template-columns: repeat(6, 1fr); /* 每行6个城市 */
  padding: 6px;
  gap: 8px;
  width: 100%;
}

.city-item {
  padding: 6px 8px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.train-list {
  margin-top: 18px;
  background: #f7faff;
  border-radius: 6px;
  padding: 16px 20px;
  width: 100%;
}

.train-list-title {
  color: #1976d2;
  font-weight: 500;
  margin-bottom: 8px;
}

.common-query {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(32, 94, 201, 0.08);
  padding: 32px 36px 24px 36px;
  width: 95%;  /* 增加宽度占比 */
  max-width: 1200px;  /* 增加最大宽度 */
  margin: 0 auto;
}

/* 日期选择器样式 */
:deep(.el-date-picker__header-label) {
  font-size: 16px;
}

:deep(.el-date-picker__time-header) {
  display: none;
}

:deep(.el-input__wrapper) {
  background-color: #fff;
}

/* 统一标签样式 */
.form-row label {
  width: 80px;
  color: #333;
  /* 修改颜色为统一的深色 */
  font-weight: normal;
  line-height: 40px;
  /* 与输入框高度一致 */
}

/* 统一输入框样式 */
.city-select,
:deep(.el-input__wrapper) {
  height: 40px;
  line-height: 40px;
  width: 180px !important;
  border: 1px solid #dcdfe6;
  /* 统一边框颜色 */
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 14px;
  padding: 0 12px;
  position: relative;
  display: flex;
  align-items: center;
  /* 垂直居中 */
}

/* 城市选择下拉面板 */
.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-top: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.city-list {
  display: flex;
  flex-wrap: wrap;
  padding: 12px;
  gap: 8px;
}

.city-item {
  padding: 6px 12px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 4px;
}

.city-item:hover {
  background: #f5f7fa;
  color: #409EFF;
}

/* 优化选项布局样式 */
.options {
  display: flex;
  gap: 24px;
  /* 保持选项之间的间距 */
  margin-bottom: 24px;
}

/* 修改选项标签样式 */
.options label {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  /* 防止文字换行 */
  min-width: 80px;
  /* 确保有足够空间 */
}

/* 优化复选框样式 */
.options input[type="checkbox"] {
  margin: 0;
  width: 16px;
  height: 16px;
}

/* 优化下拉框层级 */
.from-dropdown {
  z-index: 1001;
  /* 降低出发地下拉框的层级 */
}

.to-dropdown {
  z-index: 1002;
  /* 提高到达地下拉框的层级 */
}

/* 修改选择框基础样式 */
.city-select {
  position: relative;
  z-index: 1000;
  /* 基础层级 */
  width: 100%;
  height: 40px;
  line-height: 40px;
  padding: 0 12px;
  border: 1px solid #b7d0f7;
  border-radius: 4px;
  background: #f9fbff;
  color: #1976d2;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

/* 删除重复的下拉框样式定义，只保留一处 */
.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background: #fff;
  border: 1px solid #b7d0f7;
  border-radius: 4px;
  margin-top: 4px;
  box-shadow: 0 2px 12px rgba(32, 94, 201, 0.12);
  z-index: 1001;
  /* 提高 z-index 确保显示在最上层 */
}

/* 修改样式以匹配您的数据格式 */
.train-list ul {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* 增加到5列 */
  gap: 12px;
  padding: 0;
  margin: 0;
  list-style: none;
}

.train-list li {
  background: #f0f7ff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #daeafd;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.city-item.active {
  background: #1976d2;
  color: white;
}

.train-badge {
  font-size: 12px;
  padding: 1px 4px;
  border-radius: 3px;
  line-height: 1.2;
}

.train-badge.origin {
  background-color: #67c23a;
  color: white;
}

.train-badge.terminal {
  background-color: #409EFF;
  color: white;
}

/* 在宽屏下增加列数 */
@media (min-width: 1400px) {
  .train-list ul {
    grid-template-columns: repeat(6, 1fr); /* 在大屏上增加到6列 */
  }
}

/* 在小屏下减少列数 */
@media (max-width: 768px) {
  .train-list ul {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .train-list ul {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .city-list {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
