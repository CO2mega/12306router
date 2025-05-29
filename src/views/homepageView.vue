<template>
  <div class="homepage">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div
        class="sidebar-item"
        :class="{ active: activeMenu === 'ticket' }"
        @click="activeMenu = 'ticket'"
      >
        <i class="iconfont">&#xe600;</i>
        车票
      </div>
      <div
        class="sidebar-item"
        :class="{ active: activeMenu === 'common' }"
        @click="activeMenu = 'common'"
      >
        <i class="iconfont">&#xe601;</i>
        常用查询
      </div>
    </aside>
    <!-- 主体内容 -->
    <main class="main-content">
      <!-- 车票页面 -->
      <template v-if="activeMenu === 'ticket'">
        <!-- 查询类型选项卡 -->
        <div class="query-tabs">
          <span :class="['tab', activeTab === 0 && 'active']" @click="activeTab = 0">
            <i class="iconfont">&#xe603;</i> 单程
          </span>
          <span :class="['tab', activeTab === 1 && 'active']" @click="activeTab = 1">
            <i class="iconfont">&#xe604;</i> 往返
          </span>
          <span :class="['tab', activeTab === 2 && 'active']" @click="activeTab = 2">
            <i class="iconfont">&#xe605;</i> 中转换乘
          </span>
          <span :class="['tab', activeTab === 3 && 'active']" @click="activeTab = 3">
            <i class="iconfont">&#xe606;</i> 退改签
          </span>
        </div>
        <!-- 查询表单 -->
        <form class="query-form" @submit.prevent="onQuery">
          <div class="form-row">
            <label>出发地</label>
            <div class="city-select" @click="showFromCity = true">{{ from || '请选择' }}</div>
          </div>
          <div class="form-row">
            <label>到达地</label>
            <div class="city-select" @click="showToCity = true">{{ to || '请选择' }}</div>
          </div>
          <div class="form-row">
            <label>出发日期</label>
            <input type="date" v-model="date" />
          </div>
          <div class="form-row options">
            <label><input type="checkbox" v-model="isStudent" /> 学生</label>
            <label><input type="checkbox" v-model="isHighSpeed" /> 高铁/动车</label>
          </div>
          <button class="query-btn" type="submit">查 询</button>
        </form>
        <!-- 城市选择弹窗：出发地 -->
        <div v-if="showFromCity" class="city-modal">
          <div class="city-modal-content">
            <div class="city-modal-header">
              <span>选择出发地</span>
              <span class="close-btn" @click="showFromCity = false">×</span>
            </div>
            <div>
              <div class="city-list">
                <span
                  v-for="city in hotCities"
                  :key="city"
                  class="city-item"
                  @click="selectFromCity(city)"
                >{{ city }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 城市选择弹窗：到达地 -->
        <div v-if="showToCity" class="city-modal">
          <div class="city-modal-content">
            <div class="city-modal-header">
              <span>选择到达地</span>
              <span class="close-btn" @click="showToCity = false">×</span>
            </div>
            <div>
              <div class="city-list">
                <span
                  v-for="city in hotCities"
                  :key="city"
                  class="city-item"
                  @click="selectToCity(city)"
                >{{ city }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <!-- 常用查询页面 -->
      <template v-else>
        <div class="common-query">
          <div class="city-list">
            <span
              v-for="city in hotCities"
              :key="city"
              class="city-item"
              @click="queryTrains(city)"
            >{{ city }}</span>
          </div>
          <div v-if="trainList.length" class="train-list">
            <div class="train-list-title">{{ selectedCity }}车次列表：</div>
            <ul>
              <li v-for="train in trainList" :key="train">{{ train }}</li>
            </ul>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue";

const activeMenu = ref("ticket"); // "ticket" 或 "common"
const activeTab = ref(0);
const from = ref("");
const to = ref("");
const date = ref(new Date().toISOString().slice(0, 10));
const isStudent = ref(false);
const isHighSpeed = ref(false);
const showFromCity = ref(false);
const showToCity = ref(false);

const hotCities = [
  "北京", "上海", "天津", "重庆", "长沙", "长春",
  "成都", "福州", "广州", "贵阳", "呼和浩特", "哈尔滨",
  "合肥", "杭州", "海口", "济南", "昆明", "拉萨",
  "兰州", "南宁", "南京", "南昌", "沈阳", "石家庄",
  "太原", "乌鲁木齐", "武汉", "西宁", "西安", "银川",
  "郑州", "深圳", "厦门"
];

const selectedCity = ref("");
const trainList = ref([]);

// 示例车次数据
const cityTrains = {
  北京: ["G101", "G102", "D123"],
  上海: ["G201", "G202", "D223"],
  广州: ["G301", "G302", "D323"],
  // ...可补充其它城市
};

function onQuery() {
  alert(`出发地: ${from.value}\n到达地: ${to.value}\n日期: ${date.value}\n学生: ${isStudent.value}\n高铁/动车: ${isHighSpeed.value}`);
}
function selectFromCity(city) {
  from.value = city;
  showFromCity.value = false;
}
function selectToCity(city) {
  to.value = city;
  showToCity.value = false;
}
function queryTrains(city) {
  selectedCity.value = city;
  trainList.value = cityTrains[city] || ["暂无数据"];
}
</script>

<style scoped>
.homepage {
  display: flex;
  min-height: 100vh;
  background: #f7faff;
  padding-top: 64px; /* 顶部留出 header 空间 */
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
  padding: 36px 48px;
}
.query-tabs {
  display: flex;
  gap: 28px;
  margin-bottom: 18px;
  font-size: 18px;
}
.tab {
  color: #888;
  cursor: pointer;
  padding: 0 8px 6px 8px;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tab.active {
  color: #1976d2;
  border-bottom: 2px solid #1976d2;
  font-weight: 500;
}
.query-form {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(32,94,201,0.08);
  padding: 32px 36px 24px 36px;
  max-width: 480px;
}
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  position: relative;
}
.form-row label {
  width: 80px;
  color: #1976d2;
  font-weight: 500;
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
  margin-bottom: 24px;
  gap: 24px;
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
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #b7d0f7;
  border-radius: 5px;
  background: #f9fbff;
  font-size: 15px;
  cursor: pointer;
  color: #333;
  margin-right: 8px;
  min-width: 80px;
}
.city-modal {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.city-modal-content {
  background: #fff;
  border-radius: 8px;
  width: 520px;
  padding: 18px 24px 24px 24px;
  box-shadow: 0 2px 16px rgba(32,94,201,0.12);
}
.city-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #1976d2;
  margin-bottom: 12px;
}
.close-btn {
  font-size: 22px;
  cursor: pointer;
  color: #888;
}
.city-tabs {
  display: flex;
  gap: 18px;
  border-bottom: 1.5px solid #e3eefd;
  margin-bottom: 10px;
}
.city-tab {
  padding: 4px 10px;
  cursor: pointer;
  color: #888;
  border-bottom: 2px solid transparent;
}
.city-tab.active {
  color: #1976d2;
  border-bottom: 2px solid #1976d2;
  font-weight: 500;
}
.city-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 32px;
  padding: 10px 0 0 0;
}
.city-item {
  font-size: 16px;
  color: #1976d2;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 3px;
  transition: background 0.2s;
}
.city-item:hover {
  background: #e3eefd;
}
.train-list {
  margin-top: 18px;
  background: #f7faff;
  border-radius: 6px;
  padding: 12px 18px;
}
.train-list-title {
  color: #1976d2;
  font-weight: 500;
  margin-bottom: 8px;
}
.common-query {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(32,94,201,0.08);
  padding: 32px 36px 24px 36px;
  max-width: 480px;
  margin: 0 auto;
}
</style>
