<template>
  <div class="ticket-view">
    <div 
      v-loading="loading"
      element-loading-text="正在查询..."
      element-loading-background="rgba(255, 255, 255, 0.8)"
    >
      <!-- 完全移除标题 -->
      
      <!-- 表单部分 -->
      <el-form :inline="true" class="ticket-form" @submit.prevent="handleSearch">
        <!-- 表单内容保持不变 -->
        <!-- 修改出发地选择 -->
        <el-form-item label="出发地">
          <div class="select-wrapper from-select">
            <div 
              class="city-select"
              @click.stop="toggleFromCity()"
            >{{ searchForm.from || '请选择' }}</div>
            <div v-show="showFromCity" class="city-dropdown from-dropdown">
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
        </el-form-item>

        <!-- 修改到达地选择 -->
        <el-form-item label="目的地">
          <div class="select-wrapper to-select">
            <div 
              class="city-select"
              @click.stop="toggleToCity()"
            >{{ searchForm.to || '请选择' }}</div>
            <div v-show="showToCity" class="city-dropdown to-dropdown">
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
        </el-form-item>

        <el-form-item label="出发日期">
          <el-date-picker
            v-model="searchForm.date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            :shortcuts="shortcuts"
            value-format="YYYY-MM-DD"
            :clearable="false"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 修改表格配置，添加滚动支持 -->
      <div class="table-container">
        <el-table 
          :data="tickets" 
          v-loading="loading"
          style="width: 100%"
          :fit="true"
          :show-overflow-tooltip="true"
          :header-cell-style="{background:'#f5f7fa', color:'#606266'}"
        >
          <el-table-column prop="trainCode" label="车次" width="100" fixed="left" />
          <el-table-column label="出发站" min-width="140">
            <template #default="{ row }">
              {{ row.from.station }} ({{ row.from.sequence }})
            </template>
          </el-table-column>
          <el-table-column label="到达站" min-width="140">
            <template #default="{ row }">
              {{ row.to.station }} ({{ row.to.sequence }})
            </template>
          </el-table-column>
          <el-table-column prop="ticketsLeft" label="余票" min-width="80">
            <template #default="{ row }">
              <span :class="{ 'text-warning': row.ticketsLeft < 20 }">
                {{ row.ticketsLeft }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="runTime" label="全程运行时间" min-width="100" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                :disabled="row.ticketsLeft <= 0"
                @click="handleBook(row)"
              >
                {{ row.ticketsLeft > 0 ? '预订' : '已售完' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const loading = ref(false)

// 从路由查询参数初始化表单
const searchForm = reactive({
  from: route.query.from || '',
  to: route.query.to || '',
  date: route.query.date || new Date().toISOString().slice(0, 10),
  isStudent: route.query.isStudent === 'true',
  isHighSpeed: route.query.isHighSpeed === 'true'
})

// 监听路由参数变化
watch(
  () => route.query,
  (query) => {
    if (query.from) searchForm.from = query.from
    if (query.to) searchForm.to = query.to
    if (query.date) searchForm.date = query.date
    if (query.isStudent !== undefined) searchForm.isStudent = query.isStudent === 'true'
    if (query.isHighSpeed !== undefined) searchForm.isHighSpeed = query.isHighSpeed === 'true'
  }
)

// 组件挂载时自动查询
onMounted(() => {
  if (searchForm.from && searchForm.to) {
    handleSearch()
  }
})

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

const tickets = ref([])

const handleSearch = async () => {
  if (!searchForm.from || !searchForm.to || !searchForm.date) {
    ElMessage.warning('请填写完整查询信息')
    return
  }

  loading.value = true
  try {
    const { data } = await request.get('/api/routes/direct', {
      params: searchForm
    })

    if (data.code === 0) {
      tickets.value = data.data.routes
      if (tickets.value.length === 0) {
        ElMessage.info('未找到符合条件的车次')
      }
    } else {
      ElMessage.error(data.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 预订车票
const handleBook = async (ticket) => {
  try {
    const { data } = await request.post('/api/tickets', {
      trainCode: ticket.trainCode,
      trainFullCode: ticket.trainFullCode,
      fromStation: ticket.from.station,
      toStation: ticket.to.station,
      travelDate: searchForm.date
    })

    if (data.code === 0) {
      ElMessage.success('预订成功！')
      ticket.ticketsLeft -= 1  // 减少余票
    } else {
      ElMessage.error(data.msg || '预订失败')
    }
  } catch (error) {
    console.error('预订错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 添加城市选择相关的状态
const showFromCity = ref(false)
const showToCity = ref(false)

// 热门城市列表
const hotCities = [
  "北京", "上海", "天津", "重庆", "长沙", "长春",
  "成都", "福州", "广州", "贵阳", "呼和浩特", "哈尔滨",
  "合肥", "杭州", "海口", "济南", "昆明", "拉萨",
  "兰州", "南宁", "南京", "南昌", "沈阳", "石家庄",
  "太原", "乌鲁木齐", "武汉", "西宁", "西安", "银川",
]

// 城市选择函数
function toggleFromCity() {
  showFromCity.value = !showFromCity.value
  if (showFromCity.value) {
    showToCity.value = false
    // 计算下拉框位置
    nextTick(() => {
      positionDropdown('.from-select', '.from-dropdown')
    })
  }
}

function toggleToCity() {
  showToCity.value = !showToCity.value
  if (showToCity.value) {
    showFromCity.value = false
    // 计算下拉框位置
    nextTick(() => {
      positionDropdown('.to-select', '.to-dropdown')
    })
  }
}

// 动态计算并设置下拉框位置
function positionDropdown(triggerSelector, dropdownSelector) {
  const trigger = document.querySelector(triggerSelector)
  const dropdown = document.querySelector(dropdownSelector)
  
  if (!trigger || !dropdown) return
  
  const rect = trigger.getBoundingClientRect()
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  
  // 计算下拉框的位置
  dropdown.style.top = `${rect.bottom + scrollTop}px`
  dropdown.style.left = `${rect.left}px`
  
  // 防止超出视口右侧
  const viewportWidth = window.innerWidth
  const dropdownWidth = dropdown.offsetWidth
  
  if (rect.left + dropdownWidth > viewportWidth) {
    // 如果会超出右侧，则右对齐
    dropdown.style.left = 'auto'
    dropdown.style.right = '20px'
  }
}

// 在窗口大小变化时重新定位下拉框
window.addEventListener('resize', () => {
  if (showFromCity.value) {
    positionDropdown('.from-select', '.from-dropdown')
  }
  if (showToCity.value) {
    positionDropdown('.to-select', '.to-dropdown')
  }
})

// 添加点击外部关闭下拉菜单
onMounted(() => {
  document.addEventListener('click', (e) => {
    const fromSelect = document.querySelector('.from-select')
    const toSelect = document.querySelector('.to-select')
    
    if (!fromSelect?.contains(e.target)) {
      showFromCity.value = false
    }
    if (!toSelect?.contains(e.target)) {
      showToCity.value = false
    }
  })
})

// 城市选择处理函数
function selectFromCity(city) {
  searchForm.from = city
  showFromCity.value = false
}

function selectToCity(city) {
  searchForm.to = city
  showToCity.value = false
}
</script>

<style scoped>
/* 修复表格纵向滚动问题 */

/* 页面基本样式调整，考虑header高度和增加上下边距 */
.ticket-view {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #fff;
  padding: 40px 80px 100px; /* 增大顶部和底部内边距 */
  box-sizing: border-box;
  margin: 50px auto 120px auto; /* 左右居中，底部margin增大为120px */
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  
}

/* 完全移除标题 */
h2 {
  display: none; /* 隐藏标题 */
}

/* 表单样式优化 - 增大上下边距并居中 */
.ticket-form {
  background: #f5f7fa;
  padding: 25px; /* 增大内边距 */
  border-radius: 4px;
  margin-bottom: 30px; /* 增大表单与表格间距 */
  margin-top: 10px; /* 增加表单顶部间距 */
  border: 1px solid #e6e6e6;
  width: 100%;
  max-width: 1500px; /* 增大表单宽度 */
  margin-left: auto;
  margin-right: auto;
}

/* 表格容器样式改进 - 增大边距和居中 */
.table-container {
  width: 100%;
  max-width: 1500px; /* 增大表格宽度 */
  margin: 20px auto 60px; /* 增加上下边距，左右自动居中 */
  overflow: auto;
  flex: 1;
  min-height: 0;
  height: calc(100vh - 300px); /* 调整高度，留下更多底部空间 */
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.03);
}

/* 表格样式改进 */
:deep(.el-table) {
  width: 100%;
  height: 100%;
  border: 1px solid #ebeef5 !important;
}

/* 调整表格列宽度，使其更适合电脑屏幕 */
:deep(.el-table .el-table__cell[data-label="车次"]) {
  min-width: 120px; /* 增加宽度 */
}

:deep(.el-table .el-table__cell[data-label="出发站"]) {
  min-width: 220px; /* 进一步增加宽度 */
}

:deep(.el-table .el-table__cell[data-label="到达站"]) {
  min-width: 220px; /* 进一步增加宽度 */
}

:deep(.el-table .el-table__cell[data-label="余票"]) {
  min-width: 120px; /* 增加宽度 */
}

:deep(.el-table .el-table__cell[data-label="全程运行时间"]) {
  min-width: 140px; /* 增加宽度 */
}

:deep(.el-table .el-table__cell[data-label="操作"]) {
  min-width: 140px; /* 增加宽度 */
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto !important;
  max-height: calc(100vh - 350px); /* 调整最大高度 */
}

/* 确保表格底部有足够空间 */
:deep(.el-table::after) {
  content: "";
  display: block;
  height: 30px; /* 表格底部额外空间 */
}

/* 确保表格内容边框正确显示 */
:deep(.el-table--border .el-table__cell) {
  border-right: 1px solid #ebeef5;
}

:deep(.el-table__row:last-child .el-table__cell) {
  border-bottom: 1px solid #ebeef5;
}

/* 修复表格在某些情况下的显示问题 */
:deep(.el-table__inner-wrapper) {
  height: 100%;
}

/* 城市选择样式 */
.select-wrapper {
  position: relative;
  min-width: 200px; /* 增大选择器宽度 */
  width: auto;
  z-index: 2000; /* 增加 z-index，确保下拉菜单在表格之上 */
}

.city-select {
  height: 40px;
  line-height: 40px;
  padding: 0 15px; /* 增大内边距 */
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between; /* 添加空间，放置可能的下拉图标 */
}

.city-dropdown {
  position: fixed; /* 改为固定定位，防止被容器裁剪 */
  z-index: 2500; /* 确保在最顶层 */
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 500px; /* 增大宽度 */
  max-height: 400px; /* 限制最大高度 */
  overflow-y: auto; /* 允许垂直滚动 */
}

/* 单独定位从出发地和目的地下拉框 */
.from-dropdown {
  top: auto; /* 清除可能的top设置 */
  left: auto; /* 清除可能的left设置 */
}

.to-dropdown {
  top: auto; /* 清除可能的top设置 */
  left: auto; /* 清除可能的left设置 */
}

.city-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* 调整为5列，更合理的布局 */
  padding: 15px; /* 增大内边距 */
  gap: 12px; /* 增大间距 */
}

.city-item {
  padding: 8px 5px; /* 增大内边距 */
  text-align: center;
  cursor: pointer;
  border-radius: 4px;
}

.city-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

/* 针对超大屏幕进一步优化 */
@media screen and (min-width: 1920px) {
  .ticket-view {
    max-width: 1800px; /* 超大屏幕下进一步扩大 */
    padding: 100px 30px 60px; /* 增大内边距 */
  }
  
  .ticket-form, .table-container {
    max-width: 1700px;
  }
  
  .table-container {
    margin-bottom: 80px; /* 增大底部间距 */
  }
}

/* 大屏幕优化 */
@media screen and (min-width: 1600px) and (max-width: 1919px) {
  .ticket-view, .ticket-form, .table-container {
    max-width: 1500px;
  }
  
  .table-container {
    margin-bottom: 70px; /* 增大底部间距 */
  }
}

/* 中等屏幕 */
@media screen and (max-width: 1600px) {
  .ticket-view, .ticket-form, .table-container {
    max-width: 95%;
  }
}

/* 高亮行效果 */
:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

/* 表头样式 */
:deep(.el-table__header) {
  background-color: #f5f7fa;
}

/* 确保滚动条样式美观 */
:deep(.el-scrollbar__bar) {
  opacity: 1 !important;
}

/* 警告文字样式 */
.text-warning {
  color: #e6a23c;
  font-weight: bold;
}

/* 确保表格底部有足够的空白区域 */
.ticket-view::after {
  content: "";
  display: block;
  height: 40px; /* 页面底部额外空间 */
}
</style>
